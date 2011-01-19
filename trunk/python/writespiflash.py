#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import time
import usb
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder
from pickit.spiflash.SpiFlash import SpiFlash
import pickit.utils.SpiUtils

if len(sys.argv) != 2:
    print >>sys.stderr, "Syntax: readspiflash <file to write>"
    sys.exit(1)
infile = sys.argv[1]

pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)
spiflash = SpiFlash(pickit)
pickit.ClearReadBuffer()
pickit.ClearWriteBuffer()
pickit.ClearScriptBuffer()

# setup the pickit
pickit.SetVppVoltage(3.3, 0.5)
pickit.SetVddVoltage(3.3, 0.5)
pickit.RunScriptImmediate(SpiUtils.SetupExternalPowerScript())

# Read the SPI flash ID
print "JEDEC id: %s" % " ".join([hex(i) for i in spiflash.ReadJedecId()])

# Erase the chip
spiflash.WriteEnable()
spiflash.ChipErase()
while 'WIP' in spiflash.ReadDecodedStatus():
    print "Waiting for erase to complete...\r",
    sys.stdout.flush()
    time.sleep(1)
print 

# Write data to the chip
f = open(infile, "rb")
buf = f.read(256)
while len(buf):
    pos = f.tell() - 256
    print "Writing %08x\r" % pos,

    for i in xrange(0, len(buf), 32):
	pickit.WriteData(tuple([ord(x) for x in buf[i:i+32]]))

    spiflash.WriteEnable()
    spiflash.WritePage(pos)

    while 'WIP' in spiflash.ReadDecodedStatus():
	pass

    # read next chunk from file
    buf = f.read(256)

f.close()
print

# Shutdown pickit again
pickit.RunScriptImmediate(SpiUtils.ShutdownScript())
