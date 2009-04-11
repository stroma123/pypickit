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


if len(sys.argv) != 3:
    print >>sys.stderr, "Syntax: readspiflash <file to save in> <size of flash in bytes>"
    sys.exit(1)
outfile = sys.argv[1]
flashsize = int(sys.argv[2])

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

# Read data from the pickit
f = open(outfile, "wb")
spiflash.StartReadData(0)
for i in xrange(0, flashsize, 32):
    print "Reading %08x\r" % i,
    f.write(''.join(chr(x) for x in spiflash.ReadSpiBytes(32)))
spiflash.StopReadData()
f.close()
print

# Shutdown pickit again
pickit.RunScriptImmediate(SpiUtils.ShutdownScript())
