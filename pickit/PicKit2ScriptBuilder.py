# -*- coding: utf-8 -*-

class PicKit2ScriptBuilder():  

    VDD_ON		= 0xFF
    VDD_OFF		= 0xFE 
    VDD_GND_ON		= 0xFD
    VDD_GND_OFF		= 0xFC
    VPP_ON		= 0xFB
    VPP_OFF		= 0xFA
    VPP_PWM_ON		= 0xF9
    VPP_PWM_OFF		= 0xF8
    MCLR_GND_ON		= 0xF7
    MCLR_GND_OFF	= 0xF6
    BUSY_LED_ON		= 0xF5
    BUSY_LED_OFF	= 0xF4
    SET_ICSP_PINS	= 0xF3
    WRITE_BYTE_LITERAL	= 0xF2
    WRITE_BYTE_BUFFER   = 0xF1
    READ_BYTE_BUFFER    = 0xF0
    READ_BYTE  		= 0xEF
    WRITE_BITS_LITERAL	= 0xEE
    WRITE_BITS_BUFFER	= 0xED
    READ_BITS_BUFFER	= 0xEC
    READ_BITS		= 0xEB
    SET_ICSP_SPEED      = 0xEA
    LOOP		= 0xE9
    DELAY_LONG 		= 0xE8
    DELAY_SHORT		= 0xE7
    IF_EQ_GOTO		= 0xE6
    IF_GT_GOTO		= 0xE5
    GOTO_INDEX	        = 0xE4
    EXIT_SCRIPT		= 0xE3
    PEEK_SFR		= 0xE2
    POKE_SFR		= 0xE1
    ICDSLAVE_RX         = 0xE0
    ICDSLAVE_TX_LIT     = 0xDF
    ICDSLAVE_TX_BUF     = 0xDE
    LOOPBUFFER		= 0xDD
    ICSP_STATES_BUFFER  = 0xDC
    POP_DOWNLOAD	= 0xDB
    COREINST18          = 0xDA
    COREINST24		= 0xD9
    NOP24               = 0xD8
    VISI24        	= 0xD7
    RD2_BYTE_BUFFER	= 0xD6
    RD2_BITS_BUFFER	= 0xD5
    WRITE_BUFWORD_W	= 0xD4
    WRITE_BUFBYTE_W	= 0xD3
    CONST_WRITE_DL	= 0xD2
    WRITE_BITS_LIT_HLD  = 0xD1
    WRITE_BITS_BUF_HLD	= 0xD0
    SET_AUX		= 0xCF
    AUX_STATE_BUFFER	= 0xCE
    I2C_START		= 0xCD
    I2C_STOP		= 0xCC
    I2C_WR_BYTE_LIT	= 0xCB
    I2C_WR_BYTE_BUF	= 0xCA
    I2C_RD_BYTE_ACK	= 0xC9
    I2C_RD_BYTE_NACK	= 0xC8
    SPI_WR_BYTE_LIT	= 0xC7
    SPI_WR_BYTE_BUF	= 0xC6
    SPI_RD_BYTE_BUF	= 0xC5
    SPI_RDWR_BYTE_LIT   = 0xC4
    SPI_RDWR_BYTE_BUF	= 0xC3
    ICDSLAVE_RX_BL      = 0xC2
    ICDSLAVE_TX_LIT_BL  = 0xC1
    ICDSLAVE_TX_BUF_BL  = 0xC0
    MEASURE_PULSE       = 0xBF
    UNIO_TX             = 0xBE
    UNIO_TX_RX          = 0xBD
    JT2_SETMODE         = 0xBC
    JT2_SENDCMD         = 0xBB
    JT2_XFERDATA8_LIT   = 0xBA
    JT2_XFERDATA32_LIT  = 0xB9
    JT2_XFRFASTDAT_LIT  = 0xB8
    JT2_XFRFASTDAT_BUF  = 0xB7
    JT2_XFERINST_BUF    = 0xB6
    JT2_GET_PE_RESP     = 0xB5
    JT2_WAIT_PE_RESP    = 0xB4
    JT2_PE_PROG_RESP    = 0xB3


    def __init__(self):
	self.ClearScript()
  
    def __add__(self, other):
	sb = PicKit2ScriptBuilder()
	sb.__code = self.__code
	sb.__labels = self.__labels
	sb.__code += other.Code()
	return sb

    def ClearScript(self):
	"""Clear any accumulated code and labels."""

	self.__code = ()
	self.__labels = {}
    
    def SetLabel(self, label):
	"""Set a label at the current position in code."""

	if label in self.__labels:
	    raise Exception("Cannot change a label once it has been set")
	self.__labels[label] = len(self.__code)

    def Code(self):
	"""Retrieved accumulated code."""

	tmp = ()
	for tok in self.__code:
	    if type(tok) != tuple:
		tmp += (tok, )
		continue
	    
	    if tok[0] not in self.__labels:
		raise Exception("Reference to unknown label %s" % tok[0])
	    baseidx = len(tmp) + tok[1]
	    tokidx = self.__labels[tok[0]]

	    tmp += (-(tokidx - baseidx),  )

	return tmp

    




    ######################################## Vdd routing configuration ########################################

    # Note: if you turn VddVoltage and VddGnd off, then you can SUPPLY an external voltage to the pickit on the 
    # Vdd pin, and it will use it as the + logic level for the DAT/CLK/AUX pins.

    def VddVoltageOn(self):
	"""Routes configured Vdd voltage out to VDD_TGT pin.

	DO NOT TURN ON AT THE SAME TIME AS VddGndOn - WILL CAUSE A SHORT CIRCUIT!"""

	self.__code += (self.VDD_ON, )

    def VddVoltageOff(self):
	"""Stops routing configured Vdd voltage out to VDD_TGT pin."""

	self.__code += (self.VDD_OFF, )

    def VddGndOn(self):
	"""Routes GND to VDD_TGT pin.
	
	DO NOT TURN ON AT THE SAME TIME AS VddOn - WILL CAUSE A SHORT CIRCUIT!"""

	self.__code += (self.VDD_GND_ON, )

    def VddGndOff(self):
	"""Stops routing GND to VDD_TGT pin."""

	self.__code += (self.VDD_GND_OFF, )




    ######################################## Vpp routing configuration ########################################

    def VppVoltageOn(self):
	"""Routes configured Vpp voltage out to VPP pin."""

	self.__code += (self.VPP_ON, )

    def VppVoltageOff(self):
	"""Stops routing configured Vpp voltage out to VPP pin."""

	self.__code += (self.VPP_OFF, )

    def VppGndOn(self):
	"""Routes GND to VPP pin."""

	self.__code += (self.MCLR_GND_ON, )

    def VppGndOff(self):
	"""Stops routing GND to VPP pin."""

	self.__code += (self.MCLR_GND_OFF, )

    def VppPwmOn(self):
	"""Enable Vpp PWM - Vpp will closely match configured voltage."""

	self.__code += (self.VPP_PWM_ON, )

    def VppPwmOff(self):
	"""Disable Vpp PWM - Vpp will be ~3.3v."""

	self.__code += (self.VPP_PWM_OFF, )






    ######################################## GPIO pin support ########################################

    def ConfigureIcspPins(self, datpin_isinput, datpin_value, clkpin_isinput, clkpin_value):
	"""Configure the ICSPCLK/ICSPDAT pins on the pickit connector."""

	value = 0
	value |= (0,1)[clkpin_isinput]
	value |= (0,2)[datpin_isinput]
	value |= (0,4)[clkpin_value]
	value |= (0,8)[datpin_value]
	self.__code += (self.SET_ICSP_PINS, value)

    def ConfigureAuxPin(self, auxpin_isinput, auxpin_value):
	"""Configure the AUX pin on the pickit connector."""

	tmp = 0
	tmp |= (0,1)[auxpin_isinput]
	tmp |= (0,2)[auxpin_value]
	self.__code += (self.SET_AUX, tmp)

    def ReadIcspPinState(self):
	"""Saves the ICSP (ICSPCLK/ICSPDAT) pin states to the readbuffer.
	
	The stored byte will have bit 0 = clk_state, bit 1 = dat_state (only read if the pins are configured as inputs)."""

	self.__code += (self.ICSP_STATES_BUFFER, )

    def ReadAuxPinState(self):
	"""Saves the AUX pin state to the readbuffer.
	
	The stored byte will have bit 0 = aux_state (only read if the pin is configured as an input)."""

	self.__code += (self.AUX_STATE_BUFFER, )

    def MeasureIcspdatPinPulse(self):
	"""Waits 700ms for low->high edge on the ICSPDAT pin, then times how long it stays high (max 700ms).

	Pulse length is stored as a count of 21.333us increments as two bytes in the readbuffer (LOWBYTE then HIGHBYTE)."""

	self.__code += (self.MEASURE_PULSE, )






    ######################################## Miscellaneous ########################################

    def BusyLedOn(self):
	"""Turn on the busy LED."""

	self.__code += (self.BUSY_LED_ON, )

    def BusyLedOff(self):
	"""Turn off the busy LED."""

	self.__code += (self.BUSY_LED_OFF, )

    def SetProgrammingSpeed(self, delay_count):
	"""Sets the programming speed (see constants) - the specific "speed" depends on the programming method in use.

	=0 => fastest speed (i.e. minimum delay between operations)
	>0 => number of delays between operations - (delay is speed * programming-specific-value)."""

	self.__code += (self.SET_ICSP_SPEED, delay_count)

    def PopWriteBuffer(self):
	"""Pops (and discards) the next byte from the writebuffer."""

	self.__code += (self.POP_DOWNLOAD, )

    def PushWriteBuffer(self, value):
	"""Pushes the given value to the writebuffer."""

	self.__code += (self.CONST_WRITE_DL, value)

    def LongDelay(self, count):
	"""Delays for 5.46ms * count"""

	if count > 255:
	    raise Exception("Cannot LongDelay() for more than 255 ticks")

	self.__code += (self.DELAY_LONG, count & 0xff)

    def ShortDelay(self, count):
	"""Delays for 42.7us * count"""

	if count > 255:
	    raise Exception("Cannot LongDelay() for more than 255 ticks")

	self.__code += (self.DELAY_SHORT, count & 0xff)

    def ReadSFR(self, address):
	"""Reads a special function register (literally 0x0f00 + address) and stores its value in the readbuffer."""

	self.__code += (self.PEEK_SFR, address)

    def WriteSFR(self, address, value):
	"""Writes the given value to a special function register (literally 0x0f00 + address)."""

	self.__code += (self.POKE_SFR, address, value)






    ######################################## Script flow control ########################################

    def Repeat(self, label, repeatcount):
	"""Jumps to label and executes code between that and the Repeat instruction repeatcount times."""

	if repeatcount > 256:
	    raise Exception("Cannot Repeat() for more than 256 iterations")

	if repeatcount > 1:
	    self.__code += (self.LOOP, (label, -1), repeatcount - 1)

    def RepeatBuffer(self, label):
	"""Jumps to label and executes code between that and the Repeat instruction repeatcount times read from the writebuffer.
	
	repeatcount = (writebuffer[1] << 8) | writebuffer[0]."""

	self.__code += (self.LOOPBUFFER, (label, -1))

    def GotoIfEqual(self, label, value):
	"""Jumps to a label if the last byte written to the readbuffer is equal to the given value."""

	self.__code += (self.IF_EQ_GOTO, value, (label, -2))

    def GotoIfGreater(self, label, value):
	"""Jumps to a label if the last byte written to the readbuffer is greater than the given value."""

	self.__code += (self.IF_GT_GOTO, value, (label, -2))

    def Goto(self, label):
	"""Unconditionally jumps to the given label."""

	self.__code += (self.GOTO_INDEX, (label, -1))

    def ExitScript(self):
	"""Terminates execution of current script."""

	self.__code += (self.EXIT_SCRIPT, )








    ######################################## ICSP protocol support ########################################

    def IcspWriteByte(self, value):
	"""Writes the given 8bit value out using ICSP, LSB first.

	Bit protocol: set data, delay, clock high, delay, clock low."""

	self.__code += (self.WRITE_BYTE_LITERAL, value)

    def IcspWriteByteBuffer(self):
	"""Writes the next 8bit byte on the writebuffer out using ICSP, LSB first.

	Bit protocol: set data, delay, clock high, delay, clock low."""

	self.__code += (self.WRITE_BYTE_BUFFER, )

    def IcspReadByteBuffer(self):
	"""Reads an 8bit byte in using ICSP, LSB first, and stores it in the readbuffer.

	Bit protocol: clock high, delay, read data, clock low, delay."""

	self.__code += (self.READ_BYTE_BUFFER, )

    def IcspDiscardByte(self):
	"""Reads an 8bit byte in using ICSP, LSB first, and discards it.

	Bit protocol: clock high, delay, read data, clock low, delay."""

	self.__code += (self.READ_BYTE, )

    def IcspWriteBits(self, bitcount, value):
	"""Writes bitcount bits of the given 8bit value out using ICSP, LSB first.

	Bit protocol: set data, delay, clock high, delay, clock low."""

	self.__code += (self.WRITE_BITS_LITERAL, bitcount, value)

    def IcspWriteBitsBuffer(self, bitcount):
	"""Writes bitcount bits of the next 8bit byte on the writebuffer out using ICSP, LSB first.

	Bit protocol: set data, delay, clock high, delay, clock low."""

	self.__code += (self.WRITE_BITS_BUFFER, bitcount)

    def IcspReadBitsBuffer(self, bitcount):
	"""Reads the next bitcount bits in using ICSP, LSB first, and stores them as a byte in the readbuffer.

	Bit protocol: clock high, delay, read data, clock low, delay."""

	self.__code += (self.READ_BITS_BUFFER, bitcount)

    def IcspDiscardBits(self, bitcount):
	"""Reads the next bitcount bits in using ICSP, LSB first, and discards them.

	Bit protocol: clock high, delay, read data, clock low, delay."""

	self.__code += (self.READ_BITS, bitcount)

    def IcspWriteBitsAlt(self, bitcount,  value):
	"""Writes bitcount bits of the given 8bit value out using ICSP, LSB first using an alternative protocol.

	Bit protocol: set data, clock high, delay, clock low, delay."""

	self.__code += (self.WRITE_BITS_LITERAL, bitcount, value)

    def IcspWriteBitsBufferAlt(self, bitcount):
	"""Writes bitcount bits of the next 8bit byte on the writebuffer out using ICSP, LSB first using an alternative protocol.

	Bit protocol: set data, clock high, delay, clock low, delay."""

	self.__code += (self.WRITE_BITS_BUFFER, bitcount)







    ######################################## I2C protocol support ########################################

    def I2cStart(self):
	"""Creates an i2c start condition."""

	self.__code += (self.I2C_START, )

    def I2cStop(self):
	"""Creates an i2c stop condition."""

	self.__code += (self.I2C_STOP, )

    def I2cWriteByte(self, value):
	"""Writes the given value using i2c."""

	self.__code += (self.I2C_WR_BYTE_LIT, value)

    def I2cWriteByteBuffer(self):
	"""Writes the next value in the writebuffer using i2c."""

	self.__code += (self.I2C_WR_BYTE_BUF)

    def I2cReadByteBufferAck(self):
	"""Reads the next value using i2c, stores it in the readbuffer, and ACKs it."""

	self.__code += (self.I2C_RD_BYTE_ACK)

    def I2cReadByteBufferNack(self):
	"""Reads the next value using i2c, stores it in the readbuffer, and NACKs it."""

	self.__code += (self.I2C_RD_BYTE_NACK)







    ######################################## SPI protocol support ########################################

    def SpiWriteByte(self, value):
	"""Write the supplied value using SPI."""

	self.__code += (self.SPI_WR_BYTE_LIT, value)

    def SpiWriteByteBuffer(self):
	"""Write the next value in the writebuffer using SPI."""

	self.__code += (self.SPI_WR_BYTE_BUF, )

    def SpiReadByteBuffer(self):
	"""Read a value from SPI into the readbuffer."""

	self.__code += (self.SPI_RD_BYTE_BUF, )

    def SpiWriteReadByte(self, value):
	"""Write the supplied value using SPI, while simultaneously reading a byte and storing it in the readbuffer"""

	self.__code += (self.SPI_RDWR_BYTE_LIT, value)

    def SpiWriteReadByteBuffer(self):
	"""Write the next value in the writebuffer using SPI, while simultaneously reading a byte and storing it in the readbuffer"""

	self.__code += (self.SPI_RDWR_BYTE_BUF, value)





    ######################################## UNI/O protocol support ########################################

    def UnioWrite(self, address, count):
	"""Write count bytes from the writebuffer to the UNI/O  device at address."""

	self.__code += (self.UNIO_TX, address, count)

    def UnioWriteRead(self, address, txcount, rxcount):
	"""Write txcount bytes from the writebuffer to the UNI/O device at address, then reads rxcount bytes and stores them in the readbuffer."""

	self.__code += (self.UNIO_TX_RX, address, txcount, rxcount)





    ######################################## ICD protocol support ########################################

    def IcdReadByteBuffer(self):
	"""Read a byte from an ICD slave and store in the readbuffer."""

	self.__code += (self.ICDSLAVE_RX)

    def IcdWriteByte(self, value):
	"""Write given value to an ICD slave."""

	self.__code += (self.ICDSLAVE_TX_LIT, value)

    def IcdWriteByteBuffer(self):
	"""Write next value from writebuffer to an ICD slave."""

	self.__code += (self.ICDSLAVE_TX_BUF, )

    def IcdReadByteBufferBaseline(self):
	"""Read a byte from an ICD slave using the baseline handshake and store in the readbuffer."""

	self.__code += (self.ICDSLAVE_RX_BL, )

    def IcdWriteByteBaseline(self, value):
	"""Write given value to an ICD slave using the baseline handshake."""

	self.__code += (self.ICDSLAVE_TX_LIT_BL, value)

    def IcdWriteByteBufferBaseline(self):
	"""Write next value from writebuffer to an ICD slave using the baseline handshake."""

	self.__code += (self.ICDSLAVE_TX_BUF_BL, )





    ######################################## JTAG protocol support ########################################


    def JtagWriteTMS(self, value, numbits):
	"""Clocks out 'numbits' bits of 'value' on the JTAG TMS line, LSB first. 0 will be transmitted on TDI."""

	self.__code += (self.JT2_SETMODE, numbits, value)

    def JtagWriteIR5(self, command):
	"""Writes a 5 bit command to the JTAG Instruction Register using the Update-IR state."""

	self.__code += (self.JT2_SENDCMD, command)

    def JtagWriteDR8(self, value):
	"""Writes the 8 bit value to the JTAG Data Register using the Update-DR state, 
	and stores the 8 bits received simultaneously to the readbuffer."""

	self.__code += (self.JT2_XFERDATA8_LIT, value)

    def JtagWriteDR32(self, value):
	"""Writes the 32 bit value to the JTAG Data Register using the Update-DR state, 
	and stores the 32 bits received simultaneously to the readbuffer (MSB|MID|MID|LSB)"""

	self.__code += (self.JT2_XFERDATA32_LIT, value >> 24, value >> 16, value >> 8, value & 0xff)

    def JtagWritePauseDR32(self, value):
	"""Writes the 32 bit value to the JTAG Data Register using the Pause-DR state, 
	and stores the 32 bits received simultaneously to the readbuffer (MSB|MID|MID|LSB)"""

	self.__code += (self.JT2_XFRFASTDAT_LIT, value >> 24, value >> 16, value >> 8, value & 0xff)

    def JtagWritePauseDR32Buffer(self):
	"""Writes the next 32 bit value in the writebuffer (MSB|MID|MID|LSB) to the JTAG Data Register using the Pause-DR state, 
	and stores the 32 bits received simultaneously to the readbuffer (MSB|MID|MID|LSB)"""

	self.__code += (self.JT2_XFRFASTDAT_BUF, )




    ######################################## Microchip-specific protocol support ########################################

    def Pic32XferInstructionBuffer(self):
	"""Perform the Microchip specific Pic32 XferInstruction operation: 
	Transfers the next 32 bits of data on the writebuffer (MSB|MID|MID|LSB) to the target and executes it."""

	self.__code += (self.JT2_XFRFINST_BUF, )

    def Pic32GetPEResponse(self):
	"""Perform the Microchip specific Pic32 Get Programming Executive Response operation: 
	Waits for the PE to return a response, and stores it received data in the readbuffer (MSB|MID|MID|LSB). 
	The instruction (the last one transferred with XferInstruction?) is executed."""

	self.__code += (self.JT2_GET_PE_RESP, )

    def Pic32WaitPEResponse(self):
	"""Perform the Microchip specific Pic32 Wait for Programming Executive Response operation: 
	Waits for the PE to return a response, but does not actually store it anywhere. 
	The instruction (the last one transferred with XferInstruction?) is executed."""

	self.__code += (self.JT2_WAIT_PE_RESP, )

    def Pic32WaitPEResponseNoExec(self):
	"""Perform the Microchip specific Pic32 Wait for Programming Executive Response NoExec operation: 
	Waits for the PE to return a response, but does not actually store it anywhere. 
	It does not trigger execution of the instruction (the last one transferred with XferInstruction?)."""

	self.__code += (self.JT2_PE_PROG_RESPONSE, )







  
    def CoreInst18(self):
	# FIXME
	pass

    def CoreInst24(self):
	# FIXME
	pass

    def Nop24(self):
	# FIXME
	pass

    def Visi24(self):
	# FIXME
	pass

    def RD2ByteBuffer(self):
	# FIXME
	pass

    def RD2BitsBuffer(self):
	# FIXME
	pass

    def WriteBufWordW(self):
	# FIXME
	pass

    def WriteBufByteW(self):
	# FIXME
	pass
