from typing import Iterator, TypeVar,Generic

from .recoverable import RecoverableStopIteration,RecoverableIterator

from .RingBuffer import RingBuffer

T=TypeVar("T")
class BufferedIterator(RecoverableIterator[T],Generic[T]):
    """ 任意範囲のログを取りながら返すイテレータ
        このイテレータはRecoverableStopInterationを利用できます。
    """
    def __init__(self,src:Iterator[T],size:int):
        self._src=src
        self._buf=RingBuffer(size,0)
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