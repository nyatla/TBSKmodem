from typing import TypeVar
from .SumIterator import SumIterator
from ...types import Iterator
from ..recoverable import RecoverableStopIteration
T=TypeVar("T")


class AverageInterator(SumIterator[T]):
    """ ticks個の入力値の平均値を返します。
        このイテレータはRecoverableStopInterationを利用できます。
    """
    def __init__(self,src:Iterator[T],ticks:int):
        super().__init__(src,ticks)
        self._length=ticks
    def __next__(self) -> T:
        try:
            r=super().__next__()
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        return r/self._length