# -*- coding: utf-8 -*-
import PicKit2ScriptBuilder
import time

class PicKit2():  

    FOSC			= 48000000

    # pickit commands in normal mode
    CMD_NOP 			= 'Z'
    CMD_GETVERSION 		= 'v'
    CMD_ENTERBOOTLOADER 	= 'B'
    CMD_SET_VDD 		= 0xA0
    CMD_SET_VPP 		= 0xA1
    CMD_READ_STATUS 		= 0xA2
    CMD_READ_VOLTAGES		= 0xA3
    CMD_DOWNLOAD_SCRIPT		= 0xA4
    CMD_RUN_SCRIPT		= 0xA5
    CMD_EXECUTE_SCRIPT		= 0xA6
    CMD_CLR_DOWNLOAD_BUFFER	= 0xA7
    CMD_DOWNLOAD_DATA 		= 0xA8
    CMD_CLR_UPLOAD_BUFFER	= 0xA9
    CMD_UPLOAD_DATA		= 0xAA
    CMD_CLR_SCRIPT_BUFFER	= 0xAB
    CMD_UPLOAD_DATA_NOLEN	= 0xAC
    CMD_END_OF_BUFFER		= 0xAD
    CMD_RESET			= 0xAE
    CMD_SCRIPT_BUFFER_CHKSUM	= 0xAF
    CMD_SET_VOLTAGE_CALS	= 0xB0
    CMD_WR_INTERNAL_EE		= 0xB1
    CMD_RD_INTERNAL_EE		= 0xB2
    CMD_ENTER_UART_MODE		= 0xB3
    CMD_EXIT_UART_MODE		= 0xB4
    CMD_ENTER_LEARN_MODE	= 0xB5
    CMD_EXIT_LEARN_MODE		= 0xB6
    CMD_ENABLE_PKG2GO_MODE	= 0xB7
    CMD_LOGIC_ANALYZER_GO	= 0xB8
    CMD_COPY_RAM_UPLOAD		= 0xB9

    # The following commands are only valid in pkg2 learning mode
    CMD_READ_OSCCAL		= 0x80
    CMD_WRITE_OSCAL		= 0x81
    CMD_START_CHECKSUM		= 0x82
    CMD_VERIFY_CHECKSUM		= 0x83
    CMD_CHECK_DEVICE_ID		= 0x84
    CMD_READ_BANDGAP		= 0x85
    CMD_WRITE_CFG_BANDGAP	= 0x86
    CMD_CHANGE_CHECKSUM_FMT	= 0x87


    # Pickit commands in bootloader mode
    CMD_BOOT_READ_FLASH 	= 0x01
    CMD_BOOT_WRITE_FLASH 	= 0x02
    CMD_BOOT_ERASE_FLASH 	= 0x03
    CMD_BOOT_READ_EEDATA 	= 0x04
    CMD_BOOT_WRITE_EEDATA 	= 0x05
    CMD_BOOT_RESET	 	= 0xFF

    # Internal EEPROM locations
    IEEPROM_ADC_CAL_L       	= 0x00
    IEEPROM_ADC_CAL_H       	= 0x01
    IEEPROM_CPP_OFFSET      	= 0x02
    IEEPROM_CPP_CAL         	= 0x03
    IEEPROM_PK2GO_KEY1      	= 0x04
    IEEPRMO_PK2GO_KEY2      	= 0x05
    IEEPROM_PK2GO_KEY3      	= 0x06
    IIEPROM_PK2GO_MEM       	= 0x07 # One of EXT_EEPROM_SIZE_*
    IIEPROM_UNIT_ID         	= 0xF0 # 16 byte area for unit id

    EXT_EEPROM_SIZE_128K		= 0
    EXT_EEPROM_SIZE_256K		= 1

    PK2GO_CHECKSUM_TYPE_STD		= 0
    PK2GO_CHECKSUM_TYPE_FLASH	= 1
    PK2GO_CHECKSUM_TYPE_EEPROM	= 2

    # Sizes of buffers on the PICKIT
    SIZE_SCRIPTBUFFER		= 768
    SIZE_WRITEBUFFER		= 256
    SIZE_READBUFFER		= 128
    SIZE_TRANSFER		= 64
    SIZE_BOOTLOADERHDR		= 5
    SIZE_PROGRAMFLASHWRITE 	= 32
    SIZE_PROGRAMFLASHERASE	= 64

    ANALYZER_SAMPLE_RATE_1MHZ	= 0
    ANALYZER_SAMPLE_RATE_500KHZ	= 1
    ANALYZER_SAMPLE_RATE_250KHZ	= 3
    ANALYZER_SAMPLE_RATE_100KHZ	= 9
    ANALYZER_SAMPLE_RATE_50KHZ	= 19
    ANALYZER_SAMPLE_RATE_25KHZ	= 39
    ANALYZER_SAMPLE_RATE_10KHZ	= 99
    ANALYZER_SAMPLE_RATE_5KHZ	= 199
    ANALYZER_SAMPLE_RATE_1KHZ	= 255


    def __init__(self, transport):
        """Create a new PicKit instance.

        Arguments:
        transport -- transport instance to use."""
        self.__transport = transport
        self.__mode = self.GetFirmwareVersion()[0]
        self.__rxbuf = ()

    def GetFirmwareVersion(self):
        """Get firmware version of PIC and determine normal or bootloader mode."""

        buf = self.__transport.command((PicKit2.CMD_GETVERSION, ))

        if buf[5] == ord('B'):
            return ('BOOTLOADER', buf[6], buf[7])
        else:
            return ('NORMAL', buf[0], buf[1], buf[2])

    def EnterBootloader(self):
        """Enter bootloader mode if not already in it."""

        self.__checkmode(('BOOTLOADER', 'NORMAL'))

        if self.__mode != 'BOOTLOADER':
            buf = self.__transport.write((PicKit2.CMD_ENTERBOOTLOADER, ))
        self.__mode = self.GetFirmwareVersion()[0]

    def Reset(self):
        """Reset the PICKIT."""

        self.__checkmode(('BOOTLOADER', 'NORMAL'))

        if self.__mode != 'BOOTLOADER':
            buf = self.__transport.write((PicKit2.CMD_RESET, ))
        else:
            buf = self.__transport.write((PicKit2.CMD_BOOT_RESET, ))

    def ReadProgramMem(self, baseaddress, length):
        """Bootloader only: read program memory.
        
        Arguments:
        baseaddress: address to start reading from.
        length: number of bytes to read."""

        self.__checkmode(('BOOTLOADER', ))

        length = self.__fixlength(length, self.SIZE_TRANSFER - self.SIZE_BOOTLOADERHDR)

        return self.__transport.command(self.__boothdr(PicKit2.CMD_BOOT_READ_FLASH, length, baseaddress))[self.SIZE_BOOTLOADERHDR:self.SIZE_BOOTLOADERHDR+length]

    def WriteProgramMem(self, baseaddress, data):
        """Bootloader only: write program memory.
        
        Arguments:
        baseaddress: address to start reading from.
        data: data to write (must be PicKit2.PROGRAMWRITEBLOCKSIZE bytes)."""

        self.__checkmode(('BOOTLOADER', ))

        length = len(data)
        if length != self.SIZE_PROGRAMFLASHWRITE:
            raise PicKitException("Data to write must be %i bytes long." % self.SIZE_PROGRAMFLASHWRITE)

        self.__transport.write(self.__boothdr(PicKit2.CMD_BOOT_WRITE_FLASH, length, baseaddress) + data)
        return length

    def EraseProgramMem(self, baseaddress, blockcount):
        """Bootloader only: erase program memory.
        
        Arguments:
        baseaddress: address to start erasing at.
        blockcount: Number of 64 byte blocks to erase."""

        self.__checkmode(('BOOTLOADER', ))

        self.__transport.write(self.__boothdr(PicKit2.CMD_BOOT_ERASE_FLASH, blockcount, baseaddress))

    def ReadIEeepromMem(self, baseaddress, length):
        """Read internal EEPROM memory.
        
        Arguments:
        baseaddress: address to start reading from.
        length: number of bytes to read."""

        self.__checkmode(('BOOTLOADER', 'NORMAL'))

        if self.__mode == 'BOOTLOADER':
            length = self.__fixlength(length, MAXTXSIZE - self.SIZE_BOOTLOADERHDR)

            return self.__transport.command(self.__boothdr(PicKit2.CMD_BOOT_READ_EEDATA, length, baseaddress))[self.SIZE_BOOTLOADERHDR:self.SIZE_BOOTLOADERHDR+length]
        elif self.__mode == 'NORMAL':
            length = self.__fixlength(length, 32)

            return self.__transport.command((PicKit2.CMD_RD_INTERNAL_EE, baseaddress & 0xff, length & 0xff))[:32]

    def WriteIEepromMem(self, baseaddress, data):
        """Write internal EEPROM memory.
        
        Arguments:
        baseaddress: address to start writing to.
        data: data to write."""

        self.__checkmode(('BOOTLOADER', 'NORMAL'))

        if self.__mode == 'BOOTLOADER':
            length = self.__fixlength(len(data), MAXTXSIZE - self.SIZE_BOOTLOADERHDR)

            self.__transport.write(self.__boothdr(PicKit2.CMD_BOOT_WRITE_EEDATA, length, baseaddress) + data)
        elif self.__mode == 'NORMAL':
            length = self.__fixlength(len(data), 32)

            self.__transport.write((PicKit2.CMD_WR_INTERNAL_EE, baseaddress & 0xff, length & 0xff) + data[:length])
        return length

    def SetVddVoltage(self, voltage, threshold):
        """Set Vdd voltage to voltage, sets VDDERROR status flag if it exceeds voltage * threshold."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        if voltage < 2.5:
            voltage = 2.5
        
        ccp = int((voltage * 32.0) + 10.5) << 6
        vfault = int(((threshold * voltage) / 5.0) * 255.0) & 0xff
        if vfault > 210:
            vfault = 210

        self.__transport.write((PicKit2.CMD_SET_VDD, ccp & 0xff, ccp >> 8, vfault))

    def SetVppVoltage(self, voltage, threshold):
        """Set Vpp voltage to voltage, sets VPPERROR status flag if it exceeds voltage * threshold."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        ccp = 0x40

        vppadc = int(voltage * 18.61) & 0xff
        vfault = int(threshold * voltage * 18.61) & 0xff

        self.__transport.write((PicKit2.CMD_SET_VPP, ccp, vppadc, vfault))

    def ReadVoltages(self):
        """Returns current (Vdd, Vpp) voltage samples."""

        self.__checkmode(('NORMAL', ))

        buf = self.__transport.command((PicKit2.CMD_READ_VOLTAGES, ), 4)

        vdd = (((buf[1] << 8) | buf[0]) / 65536.0) * 5.0
        vpp = (((buf[3] << 8) | buf[2]) / 65536.0) * 13.7	
        return (vdd, vpp)

    def SetVoltageCalibrations(self, adc_scaling, vdd_offset, vdd_scaling):
        """Stores various voltage calibration settings in the internal EEPROM.
        
        adc_scaling - values read from the ADCs are multipled by this when reading the Vpp + Vdd voltage.
        vdd_offset - When setting Vdd voltage, the hardware configuration value will have this offset added to it.
        vdd_scaling - When setting Vdd voltage, the hardware configuration value will be multipled by this value."""

        self.__checkmode(('NORMAL', ))

        buf = self.__transport.write((PicKit2.CMD_SET_VOLTAGE_CALS, adc_scaling & 0xff, adc_scaling >> 8, vdd_offset, vdd_scaling))

    def ReadDecodedStatus(self):
        """Read and return the decoded pickit status."""

        self.__checkmode(('NORMAL', ))

        buf = self.__transport.command((PicKit2.CMD_READ_STATUS, ), 2)

        result = ()
        if buf[0] & 0x01:
            result += ('VDDGNDON', )
        if buf[0] & 0x02:
            result += ('VDDON', )
        if buf[0] & 0x04:
            result += ('VPPGNDON', )
        if buf[0] & 0x08:
            result += ('VPPON', )
        if buf[0] & 0x10:
            result += ('VDDERROR', )
        if buf[0] & 0x20:
            result += ('VPPERROR', )
        if buf[0] & 0x40:
            result += ('BUTTONPRESSED', )
        if buf[0] & 0x80:
            result += ('UNKNOWN', )

        if buf[1] & 0x01:
            result += ('RESET', )
        if buf[1] & 0x02:
            result += ('UARTMODE', )
        if buf[1] & 0x04:
            result += ('ICDTIMEOUT', )
        if buf[1] & 0x08:
            result += ('READBUFFERFULL', )
        if buf[1] & 0x10:
            result += ('WRITEBUFFEREMPTY', )
        if buf[1] & 0x20:
            result += ('SCRIPTBUFFEREMPTY', )
        if buf[1] & 0x40:
            result += ('SCRIPTBUFFEROVERFLOW', )
        if buf[1] & 0x80:
            result += ('WRITEBUFFEROVERFLOW', )
        return result

    def WriteScript(self, scriptid, script):
        """Upload script to the pickit's scriptbuffer storing it as scriptid."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        if isinstance(script, PicKit2ScriptBuilder.PicKit2ScriptBuilder):
            script = script.Code()

        self.__transport.write((PicKit2.CMD_DOWNLOAD_SCRIPT, scriptid, len(script)) + script)

    def RunScript(self, scriptid, iterations = 1):
        """Run the perviously uploaded script 'scriptid' from the pickit's scriptbuffer iterations (max 256) times."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        if iterations == 0:
                return
        if iterations >= 256: # a value of 0 means 256 iterations
                iterations  = 0

        self.__transport.write((PicKit2.CMD_RUN_SCRIPT, scriptid, iterations))

    def RunScriptImmediate(self, script):
        """Upload the supplied script and execute it immediately."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        if isinstance(script, PicKit2ScriptBuilder.PicKit2ScriptBuilder):
            script = script.Code()

        self.__transport.write((PicKit2.CMD_EXECUTE_SCRIPT, len(script)) + script)

    def ClearScriptBuffer(self):
        """Clear anything stored in the script buffer."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        self.__transport.write((PicKit2.CMD_CLR_SCRIPT_BUFFER, ))

    def ChecksumScriptBuffer(self):
        """Retrieve a checksum of the script buffer from the pickit and returns (length_checksum, buffer_checksum)

        length_checksum is the sum of the lengths of all scripts stored in the script buffer.
        buffer_checksum is the sum of each byte of all scripts stored in the script buffer."""

        self.__checkmode(('NORMAL', ))

        buf = self.__transport.command((PicKit2.CMD_SCRIPT_BUFFER_CHKSUM, ), 4)

        length_checksum = (buf[1] << 8) | buf[0]
        buffer_checksum = (buf[3] << 8) | buf[2]
        return (length_checksum, buffer_checksum)

    def ClearWriteBuffer(self):
        """Clear anything stored in the write buffer."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        self.__transport.write((PicKit2.CMD_CLR_DOWNLOAD_BUFFER, ))

    def WriteData(self, data):
        """Write data to the pickit for onboard processing. Returns number of bytes actually written"""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        self.__transport.write((PicKit2.CMD_DOWNLOAD_DATA, len(data)) + data)
        return len(data)

    def ClearReadBuffer(self):
        """Clear anything stored in the read buffer."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        self.__transport.write((PicKit2.CMD_CLR_UPLOAD_BUFFER, ))
        self.__rxbuf = ()

    def CopyRamToReadBuffer(self, srcaddr):
        """Copy 128 bytes of pickit RAM starting at srcaddr to the readbuffer. Bits 15->12 are ignored."""

        self.__checkmode(('NORMAL', ))

        self.__transport.write((PicKit2.CMD_COPY_RAM_UPLOAD, srcaddr & 0xff, srcaddr >> 8))

    def ReadData(self, skiplengthbyte=False):
        """Read data from the pickit readbuffer. Normally, this returns up to SIZE_TRANSFER-1 bytes worth of data.

        However, if you know there is SIZE_TRANSFER worth of data waiting, you can make it return SIZE_TRANSFER  bytes 
        by setting skiplengthbyte. If there wansn't SIZE_TRANSFER waiting, you'll still receive SIZE_TRANSFER, consisting 
        of the real data followed by undefined bytes."""

        self.__checkmode(('NORMAL', 'PK2GOLEARN'))

        if self.__mode == 'NORMAL':
            if not skiplengthbyte:
                buf = self.__transport.command((PicKit2.CMD_UPLOAD_DATA, ))
                length = buf[0]
                return buf[1:length+1]
            else:
                return self.__transport.command((PicKit2.CMD_UPLOAD_DATA_NOLEN, ))
        else:
            if not skiplengthbyte:
                self.__transport.write((PicKit2.CMD_UPLOAD_DATA, ))
            else:
                self.__transport.write((PicKit2.CMD_UPLOAD_DATA_NOLEN, ))

    def BufferedReadData(self, count = 1, timeout = None):
        """Convenience method wrapping ReadData which reads exactly count bytes of data 
        with an optional timeout (in standard python float time seconds).
        
        Returns empty list if timeout expired."""

        # accumulate data in the buffer until we have enough
        start = time.time()
        while len(self.__rxbuf) < count:
            if (timeout != None) and ((start + timeout) > time.time()):
                return ()

            # Read data
            tmp = self.ReadData()

            # Accumulate it, or delay for 1ms
            if len(tmp) > 0:
                self.__rxbuf += tmp
            else:
                time.sleep(0.0001)	    

        # return requested number of data bytes from buffer
        tmp = self.__rxbuf[0:count]
        self.__rxbuf = self.__rxbuf[count:]
        return tmp

    def EnterUartMode(self, baudrate):
        """Enter UART mode - lines will work as a serial UART with data format 8N1. Data will be automatically readfrom/writtento the writebuffer/readbuffer."""

        self.__checkmode(('NORMAL', ))

        timervalue = 65536 - int(((1.0 / baudrate) - (3.0 / 1000000)) * (self.FOSC/4/2.0))
        self.__transport.write((PicKit2.CMD_ENTER_UART_MODE, timervalue & 0xff, timervalue >> 8))

    def ExitUartMode(self):
        """Leave UART mode - serial data acquistion will no longer occur."""

        self.__checkmode(('NORMAL', ))

        self.__transport.write((PicKit2.CMD_EXIT_UART_MODE, ))

    def EnterPk2GoLearnMode(self, memsize):
        """Enter the PK2GO learning mode - all commands will be stored in an external eeprom instead of being executed immediately.
        Args:
        memsize 	is one of EXT_EEPROM_SIZE_*, and can be read from the internal EEPROM.
        """

        self.__checkmode(('NORMAL', ))

        self.__transport.write((PicKit2.CMD_ENTER_LEARN_MODE, 0x50, 0x4b, 0x32, memsize))
        self.__mode = 'PK2GOLEARN'

    def ExitPk2GoLearnMode(self):
        """Exit the PK2GO learning mode and return to normal mode."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_EXIT_LEARN_MODE, ))
        self.__mode = 'NORMAL'

    def EnterPk2GoMode(self, memsize):
    """Enter the PK2GO runtime mode - the pickit will function as a stanalone programmer until the next time the GetFirmwareVersion command is executed.
        Args:
        memsize 	is one of EXT_EEPROM_SIZE_*, and can be read from the internal EEPROM.
        """

        self.__checkmode(('NORMAL', ))

        self.__transport.write((PicKit2.CMD_ENABLE_PK2GO_MODE, 0x50, 0x4b, 0x32, memsize))

    def LogicAnalyser(self, edgetriggertype, channeltriggermask, channellevel, channeledge, triggercount, posttriggercount, samplerate):
        """Enter the pickit 3 channel logic analyser mode. 
        Args:
        edgetriggertype  	True for rising edge trigger, false for falling edge. Setting applies to all channels.

        channeltriggermask	Set a bit to enable a channel as a trigger, clear it to not trigger on that channel.
                                bit 0: channel 1
                                bit 1: channel 2
                                bit 2: channel 3

        channellevel		Set a bit for a high trigger, clear it for a low trigger.
                                bit 0: channel 1
                                bit 1: channel 2
                                bit 2: channel 3

        channeledge		Set a bit to trigger on an edge, clear it for a level trigger.
                                bit 0: channel 1
                                bit 1: channel 2
                                bit 2: channel 3

        triggercount		Number of times trigger condition must occur.

        posttriggercount 	This mode always returns 1024 samples. The device actually records continually from when the mode is entered, 
                                even though the trigger condition has not yet been met. 

                                If the posttriggercount is > 1024, then only the final 1024 will be returned.

                                If the posttriggercount is < 1024, it will return "posttrigger" count samples from AFTER the trigger, the 
                                remaining will be from those recorded before the trigger event occurred.

        samplerate		One of the ANALYZER_SAMPLE_RATE_XXX values.

        Returns: 1024 samples of data."""

        self.__checkmode(('NORMAL', ))
        
        if channeltriggermask != 0:
            if triggercount == 0:
                channeltriggermask = 0
                channellevel = 0
                channeledge = 0
            if triggercount >= 256:
                triggercount = 0 # a value of 0 means 256 counts

        self.__transport.write((PicKit2.CMD_LOGIC_ANALYZER_GO, 
                                edgetriggertype & 1, 
                                (channeltriggermask & 7) << 2, 
                                (channellevel & 7) << 2,
                                (channeledge & 7) << 2,
                                triggercount,
                                posttriggercount,
                                posttriggercount >> 8,
                                samplerate))

        buf = self.__transport.read(2, 30000)

        # read and process the trigaddr
        trigAddr = buf[0] | (buf[1] << 8)
        if trigAddr & 0x4000: # Was aborted
            return
        upperdata = 0
        if trigAddr & 0x8000:
            upperdata = 1
        trigAddr = (trigAddr & 0xfff) + 1
        trigAddr -= 0x600
        if trigAddr == 0x200:
            trigAddr = 0

        lasttriggersample = 1023 - (posttriggercount % 1024)
        trigAddr += lasttriggersample / 2

        if lasttriggersample & 1:
            upperdata = !upperdata
            if upperdata:
                trigAddr += 1
        trigAddr %= 512

        # Read sample data from memory
        data = []
        for i in xrange(0, 512, 128):
            self.CopyRamToReadBuffer(0x600 + i)
            data += self.ReadData(skiplengthbyte=True)
            data += self.ReadData(skiplengthbyte=True)

        # Decode samples
        result = []
        for x in xrange(0, 1024):
            tmp = data[trigAddr]
            if upperdata:
                trigAddr -= 1
                if trigAddr < 0:
                    trigAddr += 512
                tmp = (tmp >> 4) + (tmp << 4)
            result += (tmp & 0x1c) >> 2
            upperdata = !upperdata

        return result

    def SaveOscCal(self, address):
        """Read the OSCCAL register (at 'address') from the target device and store it for later."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_READ_OSCCAL, address & 0xff, address >> 8))

    def RestoreOscCal(self, address):
        """Write the OSCCAL register (at 'address') stored earlier to the target device."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_WRITE_OSCCAL, address & 0xff, address >> 8))

    def SaveBandgap(self):
        """Read the bandgap from the target device config word and store it for later."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_READ_BANDGAP, ))

    def RestoreBandgap(self):
        """Write the bandgap stored earlier to the target device config word."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_WRITE_BANDGAP, ))

    def ResetChecksum(self, cktype):
        """Reset the checksum calculation. 
		Args:
        cktype is one of PK2GO_CHECKSUM_TYPE_*."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_START_CHECKSUM, cktype, 0))

    def VerifyChecksum(self, checksum):
        """Verify the calculated checksum against the supplied value."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_VERIFY_CHECKSUM, checksum & 0xff, checksum >> 8))

    def ChangeChecksumType(self, cktype):
        """Change the type of checksum being calculated.
        Args:
        cktype is one of PK2GO_CHECKSUM_TYPE_*."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_CHANGE_CHKSUM_FMT, cktype, 0))

    def CheckDeviceId(self, mask, value):
        """Check the device ID of the target device against the supplied mask/value."""

        self.__checkmode(('PK2GOLEARN', ))

        self.__transport.write((PicKit2.CMD_CHECK_DEVICE_ID, mask & 0xff, mask >> 8, value & 0xff, value >> 8))




    def __boothdr(self, cmd, length, address):
        return (cmd, length, address & 0xff, (address & 0xff00) >> 8, (address & 0xff0000) >> 16)

    def __fixlength(self, length, maxlength):
        if length == -1 or length > maxlength:
            return maxlength
        return length

    def __checkmode(self, modes):
        if not self.__mode in modes:
            raise PicKitException("Cannot use this from %s mode" % self.__mode)


class PicKitException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "PicKitException(%s)" % repr(self.value)
