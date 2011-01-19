#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import time
import usb
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder
from pickit.csr.CsrSpiPicKitTransport import CsrSpiPicKitTransport 
import pickit.utils.SpiUtils

pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

# Setup the pickit 
usbtransport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(usbtransport)
csrtransport = CsrSpiPicKitTransport(pickit)
pickit.ClearReadBuffer()
pickit.ClearWriteBuffer()
pickit.ClearScriptBuffer()

# setup the pickit to power the CSR chip
pickit.SetVppVoltage(3.3, 0.5)
pickit.SetVddVoltage(3.3, 0.5)
s = PicKit2ScriptBuilder()
s += SpiUtils.SetupExternalPowerScript()
s.VddVoltageOn()
s.VppVoltageOn()
pickit.RunScriptImmediate(s)

# Read a value
print csrtransport.ReadWord(0x2b)

pickit.RunScriptImmediate(SpiUtils.ShutdownScript())
