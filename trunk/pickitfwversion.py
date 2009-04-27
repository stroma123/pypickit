#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from pickit.PicKit2LibUsbTransport import PicKit2LibUsbTransport
from pickit.PicKit2 import PicKit2


pickits = PicKit2LibUsbTransport.findpickits()
if len(pickits) == 0:
    print "Couldn't find a pickit"
    sys.exit(1)

transport = PicKit2LibUsbTransport(pickits[0])
pickit = PicKit2(transport)

print pickit.GetFirmwareVersion()

del transport
