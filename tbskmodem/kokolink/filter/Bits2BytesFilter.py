import struct
from ..streams.rostreams import BasicRoStream
from ..interfaces import IFilter,IRoStream
from ..utils import BitsWidthConvertIterator


class Bits2BytesFilter(IFilter[IRoStream[int],bytes],BasicRoStream[bytes]):
    """ nBit intイテレータから1バイト単位のbytesを返すフィルタです。
    """
    def __init__(self,input_bits:int=1):
        """
        """
        super().__init__()
        self._pos=None
        self._input_bits=input_bits
        self._iter=None


    def setInput(self,src:IRoStream[int])->"Bits2BytesFilter":
        self._pos=0
        self._iter=None if src is None else BitsWidthConvertIterator(src,self._input_bits,8)
        return self

    def __next__(self)->bytes:
        if self._iter is None:
            raise StopIteration()
        r=next(self._iter)
        self._pos=self._pos+1
        return struct.pack("1B",r)
    @property
    def pos(self)->int:
        return self._pos


