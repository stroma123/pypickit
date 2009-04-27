# -*- coding: utf-8 -*-
from zlib import crc32
from pickit.csr.CsrCore2 import CsrCore2
from pickit.csr.CsrCore3 import CsrCore3


class CsrFlash():

    def __init__(self, transport):
        """Create a new CsrFlash instance.

        Arguments:
        transport -- CSR transport instance to use."""
        
        self.__transport = transport
        if self.GetCoreType() == 2:
            self.__core = CsrCore2(transport)
        else:
            self.__core = CsrCore3(transport)

    def FlashWait(timeout_ms, pickit):
        """Waits till the boot program stops running, or a timeout of 2 seconds is reached."""

        timeout_ms = timeout_ms / 1000.0

        start = time.time()
        laststop = start
        while XapIsRunning(pickit) and (time.time() - start) < timeout_ms:
            time.sleep(0.01)

            if (time.time() - laststop) >= 0.300:
                if ReadWordVerified(0xb000, pickit) == 0:
                    XapStop(pickit)
                laststop = time.time()

        time.sleep(0.01)
        if ReadWordVerified(0xb000, pickit) != 0:
            raise Exception("Timed out")

    def FlashIdentify(pickit, crystal_speed):

        CrystalParams = {  0 => (0xff, 0x0d),
                        10 => (0x43, 0x0e),
                        16 => (0x04, 0x0e),
                        26 => (0x6f, 0x0e),
                        36 => (0x60, 0x0e) }

        # Stop the XAP
        XapResetAndStop(pickit)
        if XapIsRunning(pickit):
            raise Exception("Could not stop XAP")
        
        # Try and upload boot program
        failed = True
        for i in xrange(0, 2):

            # Upload boot program and adjust it for the crystal speed
            XapResetAndStop(pickit)
            WriteAllVerified(0xb400, BootProgram, pickit)
            WriteVerified(0xb650, (CrystalParams[crystal_speed][0] << 8) | 0x10, pickit)
            WriteVerified(0xb652, (CrystalParams[crystal_speed][1] << 8) | 0x10, pickit)
        
            # Run it and wait for it to finish
            WriteVerified(0xffe9, 0x14, pickit)
            WriteVerified(0xffea, 0x1650, pickit)
            XapGo(pickit)
            FlashWait(2000, pickit):

            # Read and process results
            tmp = ReadWordVerified(0xb009, pickit)
            if tmp == ReadWordVerified(0xb00a, pickit):
                print >>sys.stderr, "Ram reported bad starting at 0x%x" % tmp
            else:
                failed = False
                break

        if failed:
            raise Exception("Error during boot program upload")

        # Read details figured out by boot program
        flash_id = ReadWordVerified(0xb002, pickit)
        flash_manid = ReadWordVerified(0xa000, pickit)
        flash_devid = ReadWordVerified(0xa001, pickit)
        flash_offset = ReadWordVerified(0xb003, pickit)
        flash_size = 1 << (ReadWordVerified(0xb00c, pickit) - 1)
        ReadWordVerified(0xb005, pickit) #  why is this here?
        gbl_chip_version = ReadWordVerified(0xff9a, pickit)
        chip_version = ((gbl_chip_version >> 8) &0xf) -1

        # Figure out the type of MCU and flash
        mcu_type = "UNKNOWN"
        flash_type = "UNKNOWN"
        if chip_version < 2:
            mcu_type = "BC01"
            max_flash_size = 0x40000
            if flash_id == 1:
                flash_type = "AMD"
            elsif flash_id == 2:
                flash_type = "8BITPAIR"
            elsif flash_id == 3:
                flash_type = "INTEL"
            else:
                flash_type = "JEDEC"
        else:
            mcu_type = "BC02"
            max_flash_size = 0x80000
            if flash_id == 1:
                flash_type = "AMD"
            elsif flash_id == 2:
                flash_type ="8BITPAIR"
            elsif flash_id == 3:
                if hw_flags != 0x4428 or flash_manid != 32 or flash_devid != 0x882b:
                    flash_type ="INTEL"
                else:
                    flash_type ="BC2STACKED"
            elsif flash_id == 0x20:
                flash_type = "TMSC" 
            else:
                flash_type = "JEDEC"

        # Read the CFI data block
        cfi = tuple([i & 0xff for i in ReadAllVerified(0xa010, 96, pickit)])

        if cfi[0:3] != ('C', 'F', 'I'):
            # FIXME: non CFI flash detected

    def FlashReadSector(address, pickit):
        """Read a 4096 byte sector from given flash address.
        Verifies and returns the data read."""

        WriteVerified(0xb007, address >> 16, pickit)
        WriteVerified(0xb008, address, pickit)
        WriteVerified(0xb000, 5, pickit)
        XapGo(pickit)
        FlashWait(300, pickit)
        
        raw = ()
        for i in ReadAll(0xa000, 0x1000, pickit:
            raw += (chr(i >> 8), chr(i & 0xff))

        checksum = (ReadVerified(0xb009) << 16) | ReadVerified(0xb00a)
        checksum2 = crc32(''.join(raw))
        if checksum != checksum2:
            raise Exception("Checksum mismatch during sector read")

        return data

    def FlashGetCRC(pickit):
        """Returns a tuple of 32 bit crc32s, one for each 4096 byte sector in the flash."""

        WriteVerified(0xb000, 10, pickit)
        XapGo(pickit)
        FlashWait(12800, pickit)

        if ReadWordVerified(0xb00a, pickit) != 0x80:
            raise Exception("CRC failed to complete")

        raw = ReadAllVerified(0xa000, (flash_size / 4096) * 2, pickit)
        crcs = tuple([(a[i] << 16) | a[i+1] for i in xrange(0, len(raw), 2)])

        # This version appears to need some sort of fix for sector 0
        if mcu_type == 'BC01':
            WriteVerified(0xb007, 0, pickit)
            WriteVerified(0xb008, 0, pickit)
            WriteVerified(0xb000, 5, pickit)
            XapGo(pickit)
            FlashWait(300, pickit)

            WriteVerified(0xa000, (0xffff, ) * 256, pickit)
            WriteVerified(0xb000, 6, pickit)
            XapGo(pickit)
            FlashWait(300, pickit)

            crcs[0] = (ReadWordVerified(0xb009) << 16) | ReadWordVerified(0xb00a)

        return crcs
