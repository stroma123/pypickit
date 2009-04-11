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

transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)

for i in xrange(0, 256, 32):
    print "%08x: %s" % (i, " ".join([hex(x) for x in pickit.ReadIEeepromMem(i, 32)]))
