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

pickit.SetVddVoltage(3.3, 0.5) # FIXME
pickit.SetVppVoltage(3.3, 0.5) # FIXME

# Disable pickit power lines and set data pins as inputs
s = PicKit2ScriptBuilder()
s.SetProgrammingSpeed(0)
s.ConfigureIcspPins(1,0,1,0)
s.ConfigureAuxPin(1,0)
s.VddGndOff()
s.VddVoltageOff()
s.VppPwmOff()
s.VppGndOff()
s.VppVoltageOn() # FIXME
s.VddVoltageOn() # FIXME
pickit.RunScriptImmediate(s)

def outputPin(sample, oldSample, bit):
    if (oldSample ^ sample) & bit:
        sys.stdout.write("----------")
    else:
        if sample & bit:
            sys.stdout.write("         |")
        else:
            sys.stdout.write("|         ")

sampleRate = pickit.ANALYZER_SAMPLE_RATE_1KHZ
samplePeriod = pickit.LogicAnalyserSamplePeriodMHz(sampleRate)

print "   TIME   "  "    #     "  "   DAT    "  "    #     "  "   CLK    "  "    #     "  "   AUX    "
oldSample = 0
timeMhz = 0
samples = pickit.LogicAnalyser(False, 1, 1, 0, 1, 1000, sampleRate)
for x in xrange(0, len(samples)):
    sample = samples[x]
    sys.stdout.write("%10d" % timeMhz)
    sys.stdout.write("    #     ")
    outputPin(sample, oldSample, 1)
    sys.stdout.write("    #     ")
    outputPin(sample, oldSample, 2)
    sys.stdout.write("    #     ")
    outputPin(sample, oldSample, 4)
    sys.stdout.write("    #     ")

    timeMhz += samplePeriod
    oldSample = sample
    print 
