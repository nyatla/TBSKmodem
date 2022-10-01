""" BitStreamクラスを宣言します。
    
"""
from typing import Iterator
from ..utils.recoverable import RecoverableStopIteration


class StopIteration_BitsWidthConvertIterator_FractionalBitsLeft(StopIteration):
    ...

class BitsWidthConvertIterator(Iterator[int]):
    """ 任意ビット幅のintストリームを任意ビット幅のint値に変換するイテレータです。
    """
    def __init__(self,src:Iterator[int],input_bits:int=8,output_bits:int=1):
        """
        """
        super().__init__()
        self._src=src
        self._is_eos=False
        self._input_bits=input_bits
        self._output_bits=output_bits
        self._bits  =0#byte値
        self._n_bits=0 #読み出し可能ビット数
    def __next__(self)->int:
        if self._is_eos:
            raise StopIteration()
        n_bits=self._n_bits
        bits  =self._bits
        while n_bits<self._output_bits:
            try:
                d=next(self._src)
            except RecoverableStopIteration as e:
                self._bits=bits
                self._n_bits=n_bits
                raise RecoverableStopIteration(e)
            except StopIteration as e:
                self._is_eos=True
                if n_bits!=0:
                    # print("Fraction")
                    raise StopIteration_BitsWidthConvertIterator_FractionalBitsLeft(e)
                raise StopIteration(e)
            bits=(bits<<self._input_bits) | d
            n_bits=n_bits+self._input_bits

        r:int=0
        for _ in range(self._output_bits):
            r=(r<<1) | ((bits>>(n_bits-1))&0x01)
            n_bits=n_bits-1

        self._n_bits=n_bits
        self._bits=bits
        return r
