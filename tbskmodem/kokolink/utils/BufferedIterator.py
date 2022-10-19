from typing import Iterator, TypeVar,Generic

from .recoverable import RecoverableStopIteration
from ..interfaces import IRecoverableIterator
from .RingBuffer import RingBuffer

T=TypeVar("T")
class BufferedIterator(IRecoverableIterator[T],Generic[T]):
    """ 任意範囲のログを取りながら返すイテレータ
        このイテレータはRecoverableStopInterationを利用できます。
    """
    def __init__(self,src:Iterator[T],size:int,pad:T):
        self._src=src
        self._buf=RingBuffer(size,pad)
    def __next__(self) -> T:
        try:
            d=next(self._src)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        self._buf.append(d)
        return d
    @property
    def buf(self)->RingBuffer:
        return self._buf