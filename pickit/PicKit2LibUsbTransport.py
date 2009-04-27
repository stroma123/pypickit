# -*- coding: utf-8 -*-
import usb
from pickit.PicKit2 import PicKit2


class PicKit2LibUsbTransport():
    """Class defining a pickit2 USB transport using libusb."""
    
    USB_VENDOR = 0x04d8
    USB_DEVICE = 0x0033
    USB_BLOCK_SIZE = 64

    def __init__(self, device):
        """Create a new PicKitUsbTransport instance.
        
        Arguments:
        device -- USB device."""
        
        # Check the device is a PICKIT
        if (device.idVendor != self.USB_VENDOR) and (device.idProduct != self.USB_DEVICE):
            raise UsbException("Supplied USB device is not a PICKIT device")

        # Find the endpoints we need
        self.__irqin = None
        self.__irqout = None
        for ep in device.configurations[1].interfaces[0][0].endpoints:
            if ep.type == usb.ENDPOINT_TYPE_INTERRUPT:
                if (ep.address & usb.ENDPOINT_DIR_MASK) == usb.ENDPOINT_IN:
                    self.__irqin = ep.address
                elif (ep.address & usb.ENDPOINT_DIR_MASK) == usb.ENDPOINT_OUT:
                    self.__irqout = ep.address
        if  (self.__irqin == None) or (self.__irqout == None):
            raise RuntimeError("Unable to find all required endpoints")
                                                                                                                                                                            

        # Open the USB device
        self.__usb_handle = device.open()
        self.__usb_handle.setConfiguration(device.configurations[1])
        self.__usb_handle.claimInterface(device.configurations[1].interfaces[0][0])
    self.usb_read_timeout = 5000                                               
        self.usb_write_timeout = 5000

    def __del__(self):
        """Cleanup a PicKitUsbTransport structure."""
        
        try:
                self.__usb_handle.releaseInterface(self.__usb_interface)
                del self.__usb_handle
        except:
                pass
                
    def write(self, data):
        if len(data) > self.USB_BLOCK_SIZE:
            raise UsbException("Cannot write more than %i bytes in one transmission" % self.USB_BLOCK_SIZE)
        if len(data) < self.USB_BLOCK_SIZE:
        data += (PicKit2.CMD_END_OF_BUFFER, )
        if len(data) < self.USB_BLOCK_SIZE:
            data += (PicKit2.CMD_NOP, ) * (self.USB_BLOCK_SIZE - len(data))

    if self.__usb_handle.interruptWrite(self.__irqout, data, self.usb_write_timeout) != self.USB_BLOCK_SIZE:
            raise UsbException(usb.USBError)

    def read(self, length = -1, timeout = -1):
    if length == -1:
    length = self.USB_BLOCK_SIZE
    if timeout == -1:
    timeout = self.usb_read_timeout

    buf = self.__usb_handle.interruptRead(self.__irqin, self.USB_BLOCK_SIZE, timeout)
    if len(buf) != self.USB_BLOCK_SIZE:
            raise UsbException(usb.USBError)
    return buf[:length]

    def command(self, data, rxlen = -1):
    self.write(data)
    return self.read(rxlen)

    @classmethod
    def findpickits(cls):
    pickits = ()

        for bus in usb.busses():
        for device in bus.devices:
        if (device.idVendor == cls.USB_VENDOR) and (device.idProduct == cls.USB_DEVICE):
            pickits += (device, )

    return pickits



class UsbException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "USBException(%s)" % repr(self.value)
