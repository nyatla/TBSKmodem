import struct
from .BitsWidthFilter import BitsWidthFilter
from ..utils.recoverable import RecoverableStopIteration


class Bits2BytesFilter(BitsWidthFilter):
    """ nBit intイテレータから1バイト単位のbytesを返すフィルタです。
    """
    def __init__(self,input_bits:int=1):
        super().__init__(input_bits=input_bits,output_bits=8)
    def __next__(self) -> bytes:
        try:
            d=super().__next__()
        except RecoverableStopIteration:
            raise
        return struct.pack("1B",d)