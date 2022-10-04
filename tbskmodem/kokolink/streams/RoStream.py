from typing import Union,Generic,TypeVar

from ..utils.recoverable import RecoverableStopIteration
from .rostreams import BasicRoStream
from ..types import Iterable, Iterator

T=TypeVar("T")





class RoStream(BasicRoStream[T],Generic[T]):
    """T型のRoStreamです。
    """
    def __init__(self,src:Union[Iterable[T],Iterator[T]]):
        def toIterator(s):
            if isinstance(s,Iterator):
                return s
            if isinstance(s,Iterable):
                return iter(s)
            raise Exception()
        super().__init__()
        self._src=toIterator(src)
        self._pos=0
    def __next__(self)->T:
        try:
            r= next(self._src) #RecoverableStopInterationを受け取っても問題ない。
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        self._pos+=1
        return r
    @property
    def pos(self):
        return self._pos

