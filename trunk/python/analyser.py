#!/usr/bin/python2

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

# enable voltages
pickit.SetVppVoltage(3.3, 0.5)
pickit.SetVddVoltage(3.3, 0.5)

s = PicKit2ScriptBuilder()
s.SetProgrammingSpeed(0)
s.ConfigureIcspPins(1,0,1,0)
s.ConfigureAuxPin(1,0)

s.VddGndOff()
s.VddVoltageOff()

s.VppPwmOff()
s.VppGndOff()

s.VppVoltageOn()
s.VddVoltageOn()

pickit.RunScriptImmediate(s)


print pickit.LogicAnalyser(False, 1, 1, 0, 1, 1000, pickit.ANALYZER_SAMPLE_RATE_1KHZ)