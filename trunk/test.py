#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import time
import usb
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder

pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

print tuple([ord(x) for x in 'abcd'])
sys.exit(0)

transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)
pickit.ClearReadBuffer()
pickit.ClearWriteBuffer()
pickit.ClearScriptBuffer()


s = PicKit2ScriptBuilder()

import Spi
tmp = Spi.ReadSpiBytes(10).Code()
ickit.RunScriptImmediate(Spi.ReadSpiBytes(10).Code())
print pickit.ReadData()
