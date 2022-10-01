import struct
from .BitsWidthFilter import BitsWidthFilter
from ..utils.recoverable import RecoverableStopIteration


class Bits2StrFilter(BitsWidthFilter):
    """ nBit intイテレータから1バイト単位のbytesを返すフィルタです。
    """
    def __init__(self,input_bits:int=1,encoding:str="utf-8"):
        super().__init__(input_bits=input_bits,output_bits=8)
        self._encoding=encoding
        self._savedata:bytes=b""
    def __next__(self) -> bytes:            
        while True:
            try:
                d=super().__next__()
            except RecoverableStopIteration:
                raise
            self._savedata=self._savedata+struct.pack("1B",d)
            try:
                r=self._savedata.decode(self._encoding)
                self._savedata=b""
                return r
            except UnicodeDecodeError:
                continue