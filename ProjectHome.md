# Introduction #

This project provides a collection of utilities for talking to [Microchip](http://www.microchip.com) PicKit ICD programming devices from python.

It also has interface code supporting SPI Flash devices, [Cambridge Silicon Radio](http://www.csr.com) Bluetooth devices, and [Elantech](http://www.emc.com.tw) EKT8210 touchpads.

It requires the [pyusb](http://pyusb.berlios.de/) library.

Currently only the [PicKit2](http://www.microchip.com/stellent/idcplg?IdcService=SS_GET_PAGE&nodeId=1406&dDocName=en023805) is supported.


# Details #

The directory structure is as follows:


| **/** | [Command line programs.](CommandLineApps.md) |
|:------|:---------------------------------------------|
| **/pickit** | [Core interface code to the PicKit itself.](PicKit.md) |
| **/pickit/csr** | [Cambridge Silicon Radio Bluetooth chips support.](PicKit_Csr.md) |
| **/pickit/elantech** | [Elantech Touchpad support.](PicKit_Elantech.md) |
| **/pickit/spiflash** | [SPI Flash chip support.](PicKit_SpiFlash.md) |
| **/pickit/utils** | [Support libraries.](PicKit_Utils.md)        |