""" BitStreamクラスを宣言します。
    
"""
from ..streams.rostreams import BasicRoStream
from ..interfaces import IFilter,IRoStream
from ..utils import BitsWidthConvertIterator






class BitsWidthFilter(IFilter[IRoStream[int],int],BasicRoStream[int]):
    """ 任意ビット幅のintストリームを任意ビット幅のint値にエンコードします。
    """
    def __init__(self,input_bits:int=8,output_bits:int=1):
        """
        """
        super().__init__()
        self._pos=None
        self._input_bits=input_bits
        self._output_bits=output_bits
        self._iter=None


    def setInput(self,src:IRoStream[int])->"BitsWidthFilter":
        self._pos=0
        self._iter=None if src is None else BitsWidthConvertIterator(src,self._input_bits,self._output_bits)
        return self

    def __next__(self)->int:
        if self._iter is None:
            raise StopIteration()
        r=next(self._iter)
        self._pos=self._pos+1
        return r
    @property
    def pos(self)->int:
        return self._pos

