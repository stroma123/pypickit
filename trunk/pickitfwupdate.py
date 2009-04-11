#!/usr/bin/python
# -*- coding: utf-8 -*-
from pickit.utils.IntelHex import IntelHex
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2
import sys
import time

# Check args
if len(sys.argv) != 2:
	print >>sys.stderr, "Syntax: pickitfwupdate <firmware hex file>"
	sys.exit(1)
hexreader = IntelHex(sys.argv[1])


pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

# enter pickit bootloader
transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)
pickit.EnterBootloader()
del pickit
del transport

# Reconnect...
print "Waiting for PICKIT to settle..."
time.sleep(3)
transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)

# erase OS flash area
pickit.EraseProgramMem(0x2000, 0xC0)
pickit.EraseProgramMem(0x5000, 0xC0)

# Write out only the OS part of the firmware image
buf = ()
writeaddr = 0
for (curaddr, data) in hexreader.data():
	# Ignore anything outside the main OS area
	if (curaddr < 0x2000) or (curaddr >= 0x8000):
		continue

	# perform address updates/checks
	if len(buf) == 0:
		writeaddr = curaddr
	if writeaddr % 32:
		raise Exception("Write address %08x was not aligned to 32 byte boundary" % writeaddr)
	if (writeaddr + len(buf)) != curaddr:
		raise Exception("Unexpected write address %08x (expected %08x)" % (curaddr, writeaddr + len(buf)))

	# Write to flash if we have 32 bytes worth
	buf += data
	if len(buf) >= 32:
		# write it
		print "Writing %i bytes to %08x\r" % (32, writeaddr),
		sys.stdout.flush()
		pickit.WriteProgramMem(writeaddr, buf[:32])
		
		# read it back and verify
		if pickit.ReadProgramMem(writeaddr, 32) != buf[:32]:
		    raise Exception("Flash data verification failed")
		
		# Update buffer
		buf = buf[32:]
		writeaddr += 32

pickit.Reset()
print
del pickit
del transport
del hexreader
