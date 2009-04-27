# -*- coding: utf-8 -*-
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder
import pickit.utils.SpiUtils
import time


class CsrSpiPicKitTransport():

    def __init__(self, pickit):
        """Create a new CsrSpiPicKitTransport.

        Arguments:
        pickit -- pickit instance to use."""
        self.__pickit = pickit

    def ResetSPIScript(self):
        """Script reset the SPI port on the CSR chip. Returns with CS# high"""

        s = PicKit2ScriptBuilder()
        
        s += SpiUtils.CSHighScript()
        s.SetLabel('loop')
        s.ConfigureIcspPins(1,0,0,1)
        s.ShortDelay(1)
        s.ConfigureIcspPins(1,0,0,0)
        s.ShortDelay(1)
        s.Repeat('loop', 2)
        
        return s

    def StartReadDataScript(self, address):
        """Script setup for reading from a CSR chip starting at address - does not actually read the data and leaves CS# low"""

        s = PicKit2ScriptBuilder()

        s += self.ResetSPIScript()

        s += SpiUtils.CSLowScript()
        
        # Write the command and the address
        s.SpiWriteByte(0x03)
        s.SpiWriteByte(address >> 8)
        s.SpiWriteByte(address)
        
        # Read the check word
        s.SpiReadByteBuffer()
        s.SpiReadByteBuffer()

        return s

    def StartWriteDataScript(self, address):
        """Script setup for writing to a CSR chip starting at address - does not actually write the data and leaves CS# low"""

        s = PicKit2ScriptBuilder()

        s += self.ResetSPIScript()

        s += SpiUtils.CSLowScript()
        
        # Write the command and the address
        s.SpiWriteByte(0x02)
        s.SpiWriteByte(address >> 8)
        s.SpiWriteByte(address)
        
        # Read the check word
        s.SpiReadByteBuffer()
        s.SpiReadByteBuffer()

        return s



    def IsRunning(self):
        """Determine if the embedded CPU is running. Leaves CS# High"""

        s = PicKit2ScriptBuilder()

        s += self.ResetSPIScript()
        s.ReadIcspPinState()

        self.__pickit.ClearReadBuffer()
        self.__pickit.RunScriptImmediate(s.Code())
        if self.__pickit.ReadData()[0] & 2:
            return False
        return True

    def Read(self, address, count = 1):
        """Read up to count 16bit words starting at address.
        Returns data read."""

        if count > 31: # 31 'cos of the check word
            count = 31

        s = PicKit2ScriptBuilder()

        s += self.StartReadDataScript(address)
        s.SetLabel('loop')
        s.SpiReadByteBuffer()
        s.SpiReadByteBuffer()
        s.Repeat('loop', count)
        s += SpiUtils.CSHighScript()

        self.__pickit.ClearReadBuffer()
        self.__pickit.RunScriptImmediate(s.Code())

        if (self.__pickit.ReadData() != 0x03) or (self.__pickit.ReadData() != address >> 8):
            raise Exception("Check word was not correct")

        raw = self.__pickit.ReadData(True)
        return tuple([(a[i] << 8) | a[i+1] for i in xrange(0, count*2, 2)])

    def ReadVerified(self, address, count = 1):
        """Read up to count 16bit words starting at address and checks it was read successfully.
        Returns a tuple of the data read."""

        rxdata1 = self.Read(address, count)
        rxdata2 = self.Read(address, count)

        if rxdata1 != rxdata2:
        raise Exception("Read verification failed")
        
        return rxdata1

    def ReadWord(self, address):
        """Convenience method to read a single 16bit word from address.
        Returns the word."""
        
        return self.Read(address, 1)[0]

    def ReadWordVerified(self, address):
        """Convenience method to read a single 16bit word from address.
        Returns the word."""
        
        return self.ReadVerified(address, 1)[0]

    def ReadAll(self, address, count):
        """Read exactly count 16bit words from device starting at address."""
        
        data = ()
        while len(data) < count:
            pos += self.Read(address + len(data), count - len(data))
        return data

    def ReadAllVerified(self, address, count):
        """Verified read of exactly count 16bit words from device starting at address."""
        
        data = ()
        while len(data) < count:
            pos += self.Read(address + len(data), count - len(data))
        return data

    def Write(self, address, data):
        """Write some of the 16bit bytes supplied in data.
        Returns number of bytes consumed."""

        if type(data) == int:
            data = (data, )

        writelen = len(data)
        if writelen > 16:
            writelen = 16

        s = PicKit2ScriptBuilder()

        s += self.StartWriteDataScript(address)
        s.SetLabel('loop')
        s.SpiWriteByteBuffer()
        s.SpiWriteByteBuffer()
        s.Repeat('loop', writelen * 2)
        s += self.CSHighScript()
        
        raw = ()
        for i in data[0: writelen]:
            raw += (i >> 8, i & 0xff)

        self.__pickit.ClearWriteBuffer()
        self.__pickit.WriteData(raw)

        self.__pickit.RunScriptImmediate(s.Code())
        return writelen

    def WriteVerified(self, address, data):
        """Write some of the 16bit bytes supplied in data and checks it was written successfully.
        Returns number of bytes consumed."""

        count = self.Write(address, value)
        rxdata = self.Read(address, count)

        if rxdata != data:
        raise Exception("Write verification failed")
        
        return count

    def WriteAll(self, address, data):
        """Write all supplied data to device starting at address."""
        
        pos = 0
        while pos < len(data):
            pos += self.Write(address + pos, data[pos:])

    def WriteAllVerified(self, address, data):
        """Verified write of all supplied data to device starting at address."""
        
        pos = 0
        while pos < len(data):
            pos += self.WriteVerified(address + pos, data[pos:])



    def GetCoreType(self):
        """Get the type of core."""
        
        tmp = self.__transport.ReadWord(0x2b)
        if tmp < 2:
            return 2
        elif tmp < 0x10:
            return 3
        else:
            raise Exception("Chip has unknown core type")
