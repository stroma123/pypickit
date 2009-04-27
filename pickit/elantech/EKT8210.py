# -*- coding: utf-8 -*-

class EKT8210():
    """Support for communicating with an Elantech EKT8210 based touchpad in serial mode."""

    ETECH_PKT_RELRPT		= 0x50
    ETECH_PKT_ABSRPT		= 0x51
    ETECH_PKT_READREG_RESP 	= 0x52
    ETECH_PKT_READREG_REQ 	= 0x53
    ETECH_PKT_WRITEREG 		= 0x54
    ETECH_PKT_HELLO		= 0x55

    ETECH_REG_FIRMWAREVERSION	= 0x00
    ETECH_REG_BUTTONSTATUS	= 0x01
    ETECH_REG_X			= 0x02
    ETECH_REG_Y			= 0x03
    ETECH_REG_SENSITIVITY	= 0x04
    ETECH_REG_POWERSTATE	= 0x05
    ETECH_REG_TOUCHAREA		= 0x06
    ETECH_REG_PADSIZE		= 0x07    
    # Unknown: reg 8  -- R/W top bit
    # Unknown: reg 9  -- R/W top bit
    # Unknown: reg 10 -- R/W top bit
    ETECH_REG_MODE		= 0x0b
    # Unknown: reg 12 -- R/W top bit
    # Unknown: reg 13 -- R/W top two bits valid bit combos: 11, 10, 01 (00 doesn't "stick")
    ETECH_REG_REPORTRATE	= 0x0e
    ETECH_REG_FIRMWAREID	= 0x0f

    
    def __init__(self, pickit):
        """Constructor.

        pickit: pickit the touchpad is attached to - using baud rate 9600."""

        self.__pickit = pickit
        
    def ReadNextPacket(self, timeout = None):
        """Read the next complete packet from the touchpad with an optional timeout.
        
        timeout: None for no timeout, or a positive float number of seconds.
        Returns: the packet in a tuple, or () if the timeout expired."""

        # Read first byte of packet
        pkttype = self.__pickit.BufferedReadData(1, timeout)
        if len(pkttype) == 0:
            return ()
        pkttype = pkttype[0]
        
        length = 0
        if pkttype == self.ETECH_PKT_RELRPT:
            length = 4 
        elif pkttype == self.ETECH_PKT_ABSRPT:
            length = 5
        elif pkttype == self.ETECH_PKT_READREG_RESP:
            length = 3
        elif pkttype == self.ETECH_PKT_HELLO:
            length = 3
        else:
            raise Exception("Unknown packet type 0x%02x" % pkttype)

        data = (pkttype, ) + self.__pickit.BufferedReadData(length)
        if (data[length] & 1) != 1:
            raise Exception("Bad sync bit")
            
        return data

    def ReadRegister(self, reg):
        """Read the contents of a touchpad register.

        reg: Register to read.
        Returns: 16 bit value."""

        self.__pickit.WriteData((self.ETECH_PKT_READREG_REQ, reg << 4, 0x00, 0x01))
        
        # Wait for appropriate response
        while True:
            data = self.ReadNextPacket()
            if data[0] == self.ETECH_PKT_READREG_RESP:
                break
        
        if (data[1] >> 4) != reg:
            raise Exception("Invalid response to read register")
        return (((data[1] << 16) | (data[2] << 8) | data[3]) >> 4) & 0xffff

    def WriteRegister(self, reg, value):
        """Write the contents of a touchpad register.

        reg: Register to read.
        value: 16 bit value."""

        reg = reg & 0xf
        value = value & 0xffff  
        self.__pickit.WriteData((self.ETECH_PKT_WRITEREG, (reg << 4 | value >> 12) & 0xff, (value >> 4) & 0xff, (value << 4 | 0x01) & 0xff))

    def GetFirmwareVersion(self):
        """Get the version of the firmware.

        Returns: tuple of (major, minor)."""

        tmp = self.ReadRegister(self.ETECH_REG_FIRMWAREVERSION)
        return (tmp >> 8, tmp & 0xff)

    def GetButtonStatus(self):
        """Get the current button status.
        
        Returns: The status (one bit per button)."""

        return self.ReadRegister(self.ETECH_REG_BUTTONSTATUS)

    def GetXPosition(self):
        """Get the current pressed X position.

        Returns: 16 bit x value."""

        return self.ReadRegister(self.ETECH_REG_X)

    def GetYPosition(self):
        """Get the current pressed Y position.

        Returns: 16 bit y value."""

        return self.ReadRegister(self.ETECH_REG_Y)

    def GetSensitivity(self):
        """Get the sensitivity of the touchpad.

        Returns: The sensitivity."""

        return ReadRegister(self.ETECH_REG_SENSITIVITY) >> 12
    
    def SetSensitivity(self, sensitivity):
        """Set the sensitivity of the touchpad.

        sensitivity: The sensitivity."""

        self.WriteRegister(self.ETECH_REG_SENSITIVITY, (sensitivity & 0xf) << 12)

    def GetPowerState(self):
        """Get the power state of the touchpad.

        Returns: "NORMAL" or "SLEEP"."""

        return ["NORMAL", "SLEEP"][(self.ReadRegister(self.ETECH_REG_POWERSTATE) & 0x8000) != 0x8000]
    
    def SetPowerState(self, state):
        """Set the power state of the touchpad.

        state: True -- normal, False -- sleep"""

        self.WriteRegister(self.ETECH_REG_POWERSTATE, [0x0000, 0x8000][state == True])

    def GetTouchArea(self):
        """The pad appears to be divided up into discrete 2d areas, 
        each of which has a unique id ranging from 0 -> 89. This 
        returns the id of the currently touched area.


        Returns: Area ID."""

        return self.ReadRegister(self.ETECH_REG_TOUCHAREA) >> 8

    def GetPadSize(self, size):
        """Get the size of the pad.

        Returns: Size."""

        self.ReadRegister(self.ETECH_REG_PADSIZE) >> 12

    def SetPadSize(self, size):
        """This appears to control the size of the pad. 0 is 
        the largest, whilst 15 is the smallest.

        size: Size to set."""

        self.WriteRegister(self.ETECH_REG_PADSIZE, size << 12)

    def GetAbsoluteMode(self):
        """Determine the mode of the touchpad.

        Returns: True - absolute mode, False - relative mode."""

        return (self.ReadRegister(self.ETECH_REG_MODE) & 0x8000) != 0x8000
    
    def SetAbsoluteMode(self, mode):
        """Set the touchpad into absolute mode.

        mode: True for absolute mode, False for relative mode."""

        self.WriteRegister(self.ETECH_REG_MODE, [0x8000, 0][mode == True])

    def GetReportRate(self):
        """Get the touchpad's reporting rate.
    
        Returns: the reporting rate."""

        return self.ReadRegister(self.ETECH_REG_REPORTRATE) >> 12

    def SetReportRate(self, rate):
        """Set the touchpad's reporting rate (number of Report packets per second).
        
        rate: 0 is fastest, 5 is slowest."""

        if rate > 5:
            rate = 5
        self.WriteRegister(self.ETECH_REG_REPORTRATE, rate << 12)
    
    def GetFirmwareId(self):
        """Get the firmware ID.

        Returns: The ID (should be 0x8210 for EKT8210)."""

        return self.ReadRegister(self.ETECH_REG_FIRMWAREID)

    def ParseAbsoluteReportPacket(self, data):
        """Parse a report packet in absolute mode.

        data: The 6 byte packet data.
        Returns: tuple of (x, y, touch area, finger count, button state)."""
    
        finger_count = (data[5] >> 1) & 3
        buttons = data[5] >> 4
        touch_area = data[4]
        x = (((data[1] & 0xf0) << 4) | data[2]) << 4
        y = (((data[1] & 0x0f) << 8) | data[3]) << 4

        # Note: bit 3 of data[5] is unaccounted for

        return (x, y, touch_area, finger_count, buttons)
