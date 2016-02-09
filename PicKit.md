There are three classes in this library:

| **PicKit2LibUsbTransport** | This encapsulates all the libusb-specific code. Theoretically it would be possible to support a different USB library system by reimplementing this class. |
|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **PicKit2**                | The main pickit API for executing immediate operations.                                                                                                    |
| **PicKit2ScriptBuilder**   | The PicKit firmware actually implements a small virtual machine; this class allows scripts for this VM to be conveniently built.                           |

PicKit pinout:

![http://pypickit.googlecode.com/svn/wiki/pickit.png](http://pypickit.googlecode.com/svn/wiki/pickit.png)
_[svg](http://pypickit.googlecode.com/svn/wiki/pickit.svg)_

|Vpp|Programming voltage _(Note: you can read an input voltage on this line if VddVoltageOff and VddGndOff are both set)_|
|:--|:-------------------------------------------------------------------------------------------------------------------|
|Vdd|Supply voltage _(Note: if you set VddVoltageOff and VddGndOff, then you can **supply** an external voltage to the pickit on the Vdd pin, and it will use it as the + logic level for the DAT/CLK/AUX pins. You can also read the input voltage level)_|
|GND|Ground                                                                                                              |
|DAT|I/O pin "DAT" - GPIO generally used as the main data pin                                                            |
|CLK|I/O pin "CLK" - GPIO generally used as a clock pin                                                                  |
|AUX|I/O pin "AUX" - GPIO generally used as an auxiliary data pin                                                        |