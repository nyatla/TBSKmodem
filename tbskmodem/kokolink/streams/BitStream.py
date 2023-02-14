""" BitStreamクラスを宣言します。
    
"""

from ..utils.recoverable import RecoverableStopIteration
from ..interfaces import IBitStream
from .rostreams import BasicRoStream
from ..utils import BitsWidthConvertIterator
from ..types import Iterable,Iterator

class BitStream(BasicRoStream[int],IBitStream):
    """ 任意ビット幅のintストリームを1ビット単位のビットストリームに展開します。
    """
    def __init__(self,src:Iterator[int],bitwidth:int=8):
        super().__init__()
        self._bw=BitsWidthConvertIterator(src,bitwidth,1)
        self._pos=0
    def __next__(self)->int:
        try:
            r=next(self._bw)
        except RecoverableStopIteration:
            raise
        self._pos=self._pos+1
        return r
    @property
    def pos(self):
        return self._pos

