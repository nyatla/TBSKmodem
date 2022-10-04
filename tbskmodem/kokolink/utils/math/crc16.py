""" Copied from https://zenn.dev/plhr7/articles/aaefdba049abd6

"""
from typing import overload,Union

from ...types import Iterable, Iterator


class CRC16:
    ARC          = lambda: CRC16(0x8005, 0x0000,  True,  True, 0x0000)
    AUG_CCITT    = lambda: CRC16(0x1021, 0x1d0f, False, False, 0x0000)
    BUYPASS      = lambda: CRC16(0x8005, 0x0000, False, False, 0x0000)
    CCITT_FALSE  = lambda: CRC16(0x1021, 0xffff, False, False, 0x0000)
    CDMA2000     = lambda: CRC16(0xc867, 0xffff, False, False, 0x0000)
    CMS          = lambda: CRC16(0x8005, 0xffff, False, False, 0x0000)
    DDS_110      = lambda: CRC16(0x8005, 0x800d, False, False, 0x0000)
    DECT_R       = lambda: CRC16(0x0589, 0x0000, False, False, 0x0001)
    DECT_X       = lambda: CRC16(0x0589, 0x0000, False, False, 0x0000)
    DNP          = lambda: CRC16(0x3d65, 0x0000,  True,  True, 0xffff)
    EN_13757     = lambda: CRC16(0x3d65, 0x0000, False, False, 0xffff)
    GENIBUS      = lambda: CRC16(0x1021, 0xffff, False, False, 0xffff)
    GSM          = lambda: CRC16(0x1021, 0x0000, False, False, 0xffff)
    LJ1200       = lambda: CRC16(0x6f63, 0x0000, False, False, 0x0000)
    MAXIM        = lambda: CRC16(0x8005, 0x0000,  True,  True, 0xffff)
    MCRF4XX      = lambda: CRC16(0x1021, 0xffff,  True,  True, 0x0000)
    OPENSAFETY_A = lambda: CRC16(0x5935, 0x0000, False, False, 0x0000)
    OPENSAFETY_B = lambda: CRC16(0x755b, 0x0000, False, False, 0x0000)
    PROFIBUS     = lambda: CRC16(0x1dcf, 0xffff, False, False, 0xffff)
    RIELLO       = lambda: CRC16(0x1021, 0x554d,  True,  True, 0x0000)
    T10_DIF      = lambda: CRC16(0x8bb7, 0x0000, False, False, 0x0000)
    TELEDISK     = lambda: CRC16(0xa097, 0x0000, False, False, 0x0000)
    TMS37157     = lambda: CRC16(0x1021, 0x3791,  True,  True, 0x0000)
    USB          = lambda: CRC16(0x8005, 0xffff,  True,  True, 0xffff)
    CRC_A        = lambda: CRC16(0x1021, 0x6363,  True,  True, 0x0000)
    KERMIT       = lambda: CRC16(0x1021, 0x0000,  True,  True, 0x0000)
    MODBUS       = lambda: CRC16(0x8005, 0xffff,  True,  True, 0x0000)
    NRSC_5       = lambda: CRC16(0x080b, 0xffff,  True,  True, 0x0000)
    X_25         = lambda: CRC16(0x1021, 0xffff,  True,  True, 0xffff)
    XMODEM       = lambda: CRC16(0x1021, 0x0000, False, False, 0x0000)

    def __init__(self, poly:int, init:int, refin:bool, refout:bool, xorout:int):
        self.poly = poly
        self.init = init
        self.refin = refin
        self.refout = refout
        self.xorout = xorout
        if self.refin:
            self.init = self.__reflect(init, 16)

    def __reflect(self, x:int, bits:int):
        r = 0
        for i in range(bits):
            r = (r << 1) | ((x >> i) & 1)
        return r

    def _update(self,src:Union[Iterable[int],Iterator[int],bytes,str]):
        if isinstance(src,Iterator):
            init=self.init
            for x in src:
                init ^= (self.__reflect(x, 8) if self.refin else x) << 8
                for _ in range(8):
                    if init & 0x8000:
                        init = ((init << 1) ^ self.poly) & 0xffff
                    else:
                        init = (init << 1) & 0xffff
            # self.init=init #digestの子関数にしたから継承しない
            return init
        if isinstance(src,bytes):
            return self._update(iter(src))
        elif isinstance(src,str):
            return self._update(src.encode("utf-8"))
        elif isinstance(src,Iterable):
            return self._update(iter(src))
        else:
            raise TypeError()
    @overload
    def digest(self, data:bytes):
        ...
    @overload
    def digest(self, data:str):
        ...
    @overload
    def digest(self, data:Iterator[int]):
        ...
    @overload
    def digest(self, data:Iterable[int]):
        ...
    def digest(self, data:any)->int:
        x = self._update(data)
        if self.refout:
            x = self.__reflect(x, 16)
        return x ^ self.xorout

# c=CRC16.XMODEM()
# print("%x"%(c.digest(b"123456789")))
# print("%x"%(c.digest(b"123456789")))