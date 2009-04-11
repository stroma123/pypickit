#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import time
import usb
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder
from pickit.elantech.EKT8210 import EKT8210
import pickit.utils.SpiUtils
import serial


pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

# Setup the pickit 
usbtransport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(usbtransport)
pickit.ClearReadBuffer()
pickit.ClearWriteBuffer()
pickit.ClearScriptBuffer()

# Open the serial port for data
sport = serial.Serial("/dev/ttyUSB0", 9600)
ekt8210 = EKT8210(sport)

# setup the pickit to power the elantech chip
pickit.SetVppVoltage(3.3, 0.1)
pickit.SetVddVoltage(3.3, 0.1)
s = PicKit2ScriptBuilder()
s += SpiUtils.SetupExternalPowerScript()
s.VddVoltageOn()
s.VppVoltageOn()

pickit.RunScriptImmediate(SpiUtils.ShutdownScript())
pickit.RunScriptImmediate(s)




x = 1 

if x == 0:
  WriteRegister(sport, 8, 0x8000)
  WriteRegister(sport, 9, 0x8000)
  WriteRegister(sport, 10, 0x8000)
  WriteRegister(sport, 12, 0x8000)
  WriteRegister(sport, 13, 0xc000)

elif x== 1:
  WriteRegister(sport, 8, 0)
  WriteRegister(sport, 9, 0)
  WriteRegister(sport, 10, 0)
  WriteRegister(sport, 12, 0)
  WriteRegister(sport, 13, 0)

#print 
ReadNextPacket(sport, 2)

SetAbsoluteMode(sport, True)

#if GetReportRate(sport) != 0:
#  print "RESET"
SetReportRate(sport, 5)

WriteRegister(sport, 7, 0x1000)

sport.timeout = 2
while len(sport.read(1)) > 0:
  pass
sport.timeout = None
print >>sys.stderr, "GO"

for reg in (8,9,10,12,13):
  print "%02i == %04x" % (reg, ReadRegister(sport, reg))


pktcount = 0
while pktcount < 50000:
    data = ReadNextPacket(sport)
    
#    print hex(data[0])
    if data[0] == ETECH_PKT_RELRPT:
	# FIXME
	pass

    elif data[0] == ETECH_PKT_ABSRPT:
        if pktcount == 0:	
           starttime = time.time()

#        pktcount +=  1
#        print pktcount,
    
	finger_count = (data[5] >> 1) & 3
	buttons = data[5] >> 4
	touch_area = data[4]
	x = (((data[1] & 0xf0) << 4) | data[2]) << 4
	y = (((data[1] & 0x0f) << 8) | data[3]) << 4
	
	print "Fingers: %i" % finger_count
	print "Buttons: %01x" % buttons
	if touch_area != 255:
  	  print "Position: %04x %04x" % (x, y)
  	  print "TouchArea: %i" % touch_area
#	print hex(data[5] & 0x08)
  
endtime = time.time()
#print "Packets per sec: %f" % (pktcount / int(endtime - starttime))
 
#  else:
#    print "Unknown packet type %02x" % pkttype
 
pickit.RunScriptImmediate(SpiUtils.ShutdownScript())
