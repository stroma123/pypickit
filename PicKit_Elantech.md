Currently there is only support for the Elantech eKT8210 touchpad in serial mode.

This touchpad can operate in either serial (9600 8N1) or SPI mode (where the touchpad is an SPI master and generates a clock signal). Serial mode is selected by wiring the SS# and SCK lines to ground.

Example pickit/touchpad wiring diagram:

![http://pypickit.googlecode.com/svn/wiki/pickit-touchpad.png](http://pypickit.googlecode.com/svn/wiki/pickit-touchpad.png)
_[svg](http://pypickit.googlecode.com/svn/wiki/pickit-touchpad.svg)_

|Vdd|3.3v supply|
|:--|:----------|
|GND|Ground     |
|SW1|Mouse button 1|
|SW2|Mouse button 2|
|SW3|Mouse button 3|
|INT#|Asserted by touchpad to indicate it has data ready to transmit|
|SDI\_RX|SPI in or serial RX pin|
|SDO\_TX|SPI out or serial TX pin|
|SCK|SPI clock, or wired to GND for serial mode|
|SS#|SPI chip select, or wired to GND for serial mode|