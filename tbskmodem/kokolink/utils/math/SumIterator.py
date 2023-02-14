from typing import TypeVar
from ...types import Iterator
from .. import RingBuffer
from ..recoverable import RecoverableStopIteration
from ...interfaces import IRecoverableIterator

T=TypeVar("T")
class SumIterator(IRecoverableIterator[T]):
    """ ストリームの読み出し位置から過去N個の合計を返すイテレータです。
        このイテレータはRecoverableStopInterationを利用できます。
    """
    def __init__(self,src:Iterator[T],length:int):
        self._src=src
        self._buf=RingBuffer[T](length,0)
        self._sum:float=0
        # self._length=length
        # self._num_of_input=0
        self._gen=None
        return
    def __next__(self) -> T:
        try:
            s=next(self._src)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        d=self._buf.append(s)
        self._sum=self._sum+s-d
        # self._num_of_input=self._num_of_input+1
        return self._sum
    # @property
    # def num_of_input(self)->int:
    #     return self._num_of_input
    @property
    def buf(self)->RingBuffer[T]:
        return self._buf


