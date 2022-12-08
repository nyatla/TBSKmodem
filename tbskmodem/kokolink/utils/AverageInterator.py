from typing import overload,TypeVar,Generic
from .functions import isinstances
from .SumIterator import SumIterator
from ..types import Iterator
from .recoverable import RecoverableStopIteration






T=TypeVar("T")





class AverageInterator(SumIterator[T]):
    """ 末尾からticksまでの平均値を連続して返却します。
        このイテレータはRecoverableStopInterationを利用できます。
    """
    @overload
    def __init__(self,src:Iterator[T],ticks:int):
        ...
    def __init__(self,*args,**kwds):
        self._length:int
        def __init__B(self:AverageInterator[T],src:Iterator[T],ticks:int):
            super().__init__(src,ticks)
            self._length=ticks
        if isinstances(args,(Iterator,int,)):
            __init__B(self,*args,**kwds)
        else:
            raise TypeError()
    def __next__(self) -> T:
        try:
            r=super().__next__()
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        return r/self._length