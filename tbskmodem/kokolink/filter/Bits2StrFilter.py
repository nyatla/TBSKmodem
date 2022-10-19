import struct
from ..utils.recoverable import RecoverableStopIteration
from ..streams.rostreams import BasicRoStream
from ..interfaces import IFilter,IRoStream
from ..utils import BitsWidthConvertIterator


class Bits2StrFilter(IFilter[IRoStream[int],str],BasicRoStream[str]):
    """ nBit intイテレータから1文字単位のstrを返すフィルタです。
    """
    def __init__(self,input_bits:int=1,encoding:str="utf-8"):
        """
        """
        super().__init__()
        self._pos=None
        self._input_bits=input_bits
        self._encoding=encoding
        self._iter=None
        self._savedata:bytes=b""

    def setInput(self,src:IRoStream[int])->"Bits2StrFilter":
        self._pos=0
        self._iter=None if src is None else BitsWidthConvertIterator(src,self._input_bits,8)
        return self

    def __next__(self)->str:
        while True:
            try:
                d=next(self._iter)
            except RecoverableStopIteration:
                raise
            self._savedata=self._savedata+struct.pack("1B",d)
            try:
                r=self._savedata.decode(self._encoding)
                self._savedata=b""
                self._pos=self._pos+1
                return r
            except UnicodeDecodeError:
                continue
    @property
    def pos(self)->int:
        return self._pos