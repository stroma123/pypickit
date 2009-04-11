# -*- coding: utf-8 -*-
from pickit.PicKit2ScriptBuilder import PicKit2ScriptBuilder

def CSLowScript():
    """Set the CS# line low"""

    s = PicKit2ScriptBuilder()

    s.VppVoltageOff()	
    s.VppGndOn()
    s.ShortDelay(1)

    return s

def CSHighScript():
    """Set the CS# line high"""

    s = PicKit2ScriptBuilder()

    s.VppGndOff()
    s.VppVoltageOn()	
    s.ShortDelay(1)

    return s

def SetupExternalPowerScript():
    """Setup the pickit for communicating with a device which is externally powered"""

    s = PicKit2ScriptBuilder()

    # Setup pins
    s.SetProgrammingSpeed(0)
    s.ConfigureIcspPins(1,0,0,0) # MISO + CLK
    s.ConfigureAuxPin(0,0) # MOSI

    # setup Vdd
    s.VddGndOff()
    s.VddVoltageOff()

    # setup Vpp (CS#)
    s.VppPwmOff()
    s.VppGndOff()
    s.VppVoltageOn()

    return s

def ShutdownScript():
    """Shutdown the pickit safely"""

    s = PicKit2ScriptBuilder()

    s.VddVoltageOff()
    s.VddGndOff()
    s.VppVoltageOff()
    s.VppGndOff()

    return s
