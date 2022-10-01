""" BitStreamクラスを宣言します。
    
"""

from typing import Iterable, Iterator, Union

from ..utils.recoverable import RecoverableStopIteration
from ..interfaces import IRoStream,IBitStream
from .rostreams import BasicRoStream
from ..utils import BitsWidthConvertIterator

class BitStream(BasicRoStream[int],IBitStream):
    """ 任意ビット幅のintストリームを1ビット単位のビットストリームに展開します。
    """
    def __init__(self,src:Union[Iterable[int],Iterator[int]],bitwidth:int=8):
        super().__init__()
        def toIterator(s):
            if isinstance(s,Iterator):
                return s
            if isinstance(s,Iterable):
                return iter(s)
            raise Exception()        
        self._bw=BitsWidthConvertIterator(toIterator(src),bitwidth,1)
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

