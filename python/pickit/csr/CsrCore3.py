# -*- coding: utf-8 -*-


class CsrCore3():

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
        return self.__transport.ReadWord(0xFE8D) == 0

    def Stop(self):
        """Try and stop the XAP processor."""

        for i in xrange(0, 4):
            self.__transport.WriteVerified(0xFE9C, 2)
            if not self.IsRunning():
                return

        raise Exception("Could not stop XAP")

    def ResetAndGo(self):
        """Reset the XAP processor and start it running."""

        self.Stop()
        self.__transport.WriteVerified(0xFDA0, 0)
        tmp = self.__transport.ReadWord(0xFE91)
        self.__transport.Write(0xFE92, 1)
        self.__transport.Write(0xFE91, tmp)

    def ResetAndStop(self):
        """Reset the XAP processor and stop it."""

        self.ResetAndGo()
        while self.__transport.ReadWordVerified(0xFE92):
            pass
        self.Stop()

    def Go(self):
        """Start the XAP processor running."""

        self.__transport.Write(0xFE9C, 2)
        self.__transport.Write(0xFE9C, 3)
        self.__transport.Write(0xFE9C, 2)
        self.__transport.Write(0xFE9C, 1)

    def GoIrqOnBreakpoint(self):
        """Start the XAP processor running and cause an IRQ when a breakpoint is hit?"""

        self.__transport.Write(0xFE9C, 2)
        self.__transport.Write(0xFE9C, 3)
        self.__transport.Write(0xFE9C, 0)

    def GetProcType(self):
    
        return self.__transport.ReadWordVerified(0xFE91)

    def SetProcType(self, type):
    
        if type < 0 or type > 3:
            raise Exception("Unknown proc type")
        self.__transport.WriteWordVerified(0xFE91, type)

