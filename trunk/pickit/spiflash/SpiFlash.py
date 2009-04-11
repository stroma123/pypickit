# -*- coding: utf-8 -*-
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder
import pickit.utils.SpiUtils


class SpiFlash():
    
    def __init__(self, pickit):

	self.__pickit = pickit

    def ReadJedecId(self):
	"""Read the JEDEC ID from the flash chip"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x9f)
	s.SpiReadByteBuffer()
	s.SpiReadByteBuffer()
	s.SpiReadByteBuffer()
	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)
	return self.__pickit.ReadData()

    def ReadDecodedStatus(self):
	"""Read and decode the status register"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x05)
	s.SpiReadByteBuffer()
	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)
	return self.DecodeStatus(self.__pickit.ReadData()[0])

    def DecodeStatus(self, status):
	"""Decode a supplied status register value"""

	result = ()

	if status & 0x01:
	    result += ('WIP', )
	if status & 0x02:
	    result += ('WEL', )
	if status & 0x04:
	    result += ('BP0', )
	if status & 0x08:
	    result += ('BP1', )
	if status & 0x10:
	    result += ('BP2', )
	if status & 0x20:
	    result += ('BP3', )
	if status & 0x40:
	    result += ('CP', )
	if status & 0x80:
	    result += ('SRWD', )

	return result

    def StartReadData(self, address = 0):
	"""Issue the continuous data read instruction (leaves CS# low)"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x03)
	s.SpiWriteByte((address >> 16) & 0xff)
	s.SpiWriteByte((address >> 8) & 0xff)
	s.SpiWriteByte(address & 0xff)
	
	self.__pickit.RunScriptImmediate(s)

    def StopReadData(self):
	"""Complete the data read process"""

	self.__pickit.RunScriptImmediate(SpiUtils.CSHighScript())

    def WritePage(self, address):
	"""Issue the page program instruction for the given address, reading 256 bytes from the writebuffer"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x02)
	s.SpiWriteByte(address >> 16)
	s.SpiWriteByte(address >> 8)
	s.SpiWriteByte(address)

	s.SetLabel('loop')
	s.SpiWriteByteBuffer()
	s.Repeat('loop', 256)

	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)

    def ReadSpiBytes(self, count):
	"""Read count bytes from SPI and store in the readbuffer"""

	s = PicKit2ScriptBuilder()

	s.SetLabel('loop')
	s.SpiReadByteBuffer()
	s.Repeat('loop', count)

	self.__pickit.RunScriptImmediate(s.Code())
	return self.__pickit.ReadData()

    def WriteEnable(self):
	"""Send the write enable command"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x06)
	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)

    def WriteDisable(self):
	"""Send the write disable command"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x04)
	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)

    def ChipErase(self):
	"""Erase all memory on target chip"""

	s = PicKit2ScriptBuilder()

	s += SpiUtils.CSLowScript()
	s.SpiWriteByte(0x60)
	s += SpiUtils.CSHighScript()

	self.__pickit.RunScriptImmediate(s)
