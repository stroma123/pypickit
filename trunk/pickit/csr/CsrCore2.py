# -*- coding: utf-8 -*-


class CsrCore2():

    def __init__(self, transport):
        """Create a new CsrCore2 instance.

	Arguments:
	transport -- CSR transport instance to use."""
	self.__transport = transport

    def IsPresent(self):
	"""Determine if there is a device connected"""

	try:
	    self.__transport.ReadWord(0xFFa9)
	except:
	    return False
	return True

    def IsRunning(self):
	tmp = self.__transport.IsRunning()	
	if not tmp:
	    self.ReadWord(0xFFa9) # this ensures there actually *is* a chip present - exception if there's a problem
	return tmp

    def Stop(self):
	"""Try and stop the XAP processor."""

	for i in xrange(0, 4):
	    # FIXME: call that mysterious function

	    # Original does that weird spi_summat stuff with the shift period
	    self.__transport.Write(0x6a, 2)
	    self.__transport.Write(0xFFDE, 0)
	    if not self.IsRunning():
		return

	raise Exception("Could not stop XAP")

    def ResetAndGo(self):
	"""Reset the XAP processor and start it running."""

	# FIXME: call mysterious function
	self.__transport.WriteVerified(0xA000, 0)
	self.__transport.WriteVerified(0xA001, 0)
	self.__transport.WriteVerified(0xA002, 0xe0)
	self.__transport.ReadWordVerified(0xFFE9)
	self.__transport.WriteVerified(0xFFe9, 0x54)

	self.__transport.WriteVerified(0xFFEA, 0)
	self.__transport.WriteVerified(0xFF7e, self.__transport.ReadWordVerified(0xff7e) & 0xefff)
	self.__transport.WriteVerified(0xFFDE, 0)
	self.__transport.WriteVerified(0xFFE8, 0)
	self.__transport.WriteVerified(0x76, 2)
	self.__transport.WriteVerified(0xFF91, 1)
	self.__transport.WriteVerified(0x77, 1)
	self.__transport.WriteVerified(0x6a, 0)

    def ResetAndStop(self):
	"""Reset the XAP processor and stop it."""

	self.ResetAndGo()
	endtime = time() + 1.0
	while self.__transport.ReadWord(0xff91) == 1 || time() < endtime:
	    pass
	if self.__transport.ReadWord(0xff91) == 1:
	    raise Exception("Unable to stop XAP processor")

	for i in xrange(0, 20):
	    self.__transport.Write(0x6a, 2)

	self.__transport.WriteAll(0, (0x00, ) * 107)
	self.__transport.Write(0x6a, 2)
	self.__transport.Write(0x6a, 2)
	self.__transport.WriteAll(0xffe0, (0x00, ) * 16)

    def Go(self):
	"""Start the XAP processor running."""

	self.__transport.Write(0x6a, 2)
	self.__transport.Write(0x6a, 3)
	self.__transport.Write(0x6a, 2)
	self.__transport.Write(0x6a, 1)

    def GoIrqOnBreakpoint(self):
	"""Start the XAP processor running and cause an IRQ when a breakpoint is hit?"""

	self.__transport.Write(0x6a, 2)
	self.__transport.Write(0x6a, 3)
	self.__transport.Write(0x6a, 0)


    def GetProcType(self):
      
	return 2

    def SetProcType(self, type):
	
	pass
