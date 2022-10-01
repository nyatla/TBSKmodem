
from typing import Iterable, Iterator,Sequence,Tuple, overload,Dict,TypeVar,Generic,TypeVar
from .rostreams import BasicRoStream
from ..interfaces import IFilter, IRoStream

T=TypeVar("T")
class ChaindStream(BasicRoStream[T],IRoStream[T],Generic[T]):
    """ 指定tickを経過する毎に入力チェインを切り替えるストリームです。
        
    """
    def __init__(self,src:Sequence[Tuple[IRoStream[T],int]]):
        """
            src
                ストリームと、そのストリームの停止位置のタプルのリストです。
                何れかのストリームが停止した場合は、そこでストリームを終端させます。
        """
        self._src=src
        self._current_idx=0
        self._current_src=src[0][0]
        self._current_max=src[0][1]
        self._pos=0
        self._is_eos=False
    def __next__(self)->T:
        if self._is_eos:
            raise StopIteration()

        src=self._current_src
        try:
            if self._current_max is None or src.pos<self._current_max:
                r=next(src)
                self._pos=self._pos+1
                return r
            else:
                self._current_idx=self._current_idx+1 #次のストリームへ
                if self._current_idx<len(self._src):
                    self._current_src=self._src[self._current_idx][0]
                    self._current_max=self._src[self._current_idx][1]
                    return next(self)
                else:
                    raise StopIteration()
        except StopIteration as e:
            self._is_eos=True
            raise StopIteration(e)

    @property
    def pos(self)->int:
        return self._pos

# いらん気がするんだ。仕様も(src毎回セットするとか。それならStreamで足りる)２つ考えられるし。
# S=TypeVar("S")
# D=TypeVar("D")
# class ChaindFilter(BasicRoStream[D],IFilter[S,D],Generic[S,D]):
#     """ 指定tickを経過する毎に入力チェインを切り替えるストリームです。
        
#     """
#     def __init__(self,src:Sequence[Tuple[IFilter[S,D],int]]):
#         """
#             src
#                 ストリームと、そのストリームの停止位置のタプルのリストです。
#                 何れかのストリームが停止した場合は、そこでストリームを終端させます。
#         """
#         super().__init__(src)
#         self._src=src
#         self._current_idx:int
#         self._current_src:IFilter[S,D]
#         self._current_max:int
#         self._pos:int
#         self._is_eos=False
#     def setInput(self, src: S) -> "ChaindFilter[S,D]":
#         self._is_eos=True if src is None else False
#         self._current_idx=0
#         self._current_src=src[0][0]
#         self._current_max=src[0][1]
#         for i in self._src:
#             i.setInput(src)
#         self._pos=0

#         return super().setInput(src)
#     def __next__(self)->T:
#         if self._is_eos:
#             raise StopIteration()

#         src=self._current_src
#         try:
#             if self._current_max is None or src.pos<self._current_max:
#                 r=next(src)
#                 self._pos=self._pos+1
#                 return r
#             else:
#                 self._current_idx=self._current_idx+1 #次のストリームへ
#                 if self._current_idx<len(self._src):
#                     self._current_src=self._src[self._current_idx][0]
#                     self._current_max=self._src[self._current_idx][1]
#                     return next(self)
#                 else:
#                     raise StopIteration()
#         except StopIteration:
#             self._is_eos=True
#             raise

#     @property
#     def pos(self)->int:
#         return self._pos