#!/usr/bin/python
# -*- coding: utf-8 -*-

class IntelHex():

    def __init__(self, filename):
        self.__file = open(filename)

    def __del__(self):
        self.__file.close()

    def data(self):
        baseaddress = 0
        linecounter = 0
        for line in self.__file:
            # Get next line
            line = line.strip()
            linecounter+=1

            # some simple sanity checks
            if len(line) < 11:
                continue
            if line[0] != ':':
                continue

            # Parse the line data
            bytecount = int(line[1:3], 16)
            address = int(line[3:7], 16)
            rtype = int(line[7:9], 16)
            cc = int(line[9+bytecount*2:9+bytecount*2+2], 16)
            data = tuple([int(line[i:i+2],16) for i in xrange(9, 9 + bytecount * 2, 2)])

            # Calculate the checksum
            calccc = bytecount + (address & 0xff) + (address >> 8) + rtype
            if len(data) > 0:
                calccc += reduce(lambda x,y: x+y, data)
            calccc = (0x100 - (calccc & 0xff)) & 0xff
            if cc != calccc:
                raise Exception("Corrupted Intel HEX file found at line %i" % linecounter)

            # Process the records
            if rtype == 0x00:
                yield (baseaddress + address, data)
            elif rtype == 0x01:
                return
            elif rtype == 0x02:
                if address != 0 or len(data) !=2:
                    raise Exception("Corrupted Intel HEX file found at line %i" % linecounter)
                baseaddress = ((data[0] << 8) | data[1]) << 4
            elif rtype == 0x04:
                if address != 0 or len(data) !=2:
                    raise Exception("Corrupted Intel HEX file found at line %i" % linecounter)
                baseaddress = ((data[0] << 8) | data[1]) << 16
            else:
                raise Exception("Unsupported Intel HEX record type %i found at line %i" % (rtype, linecounter))
