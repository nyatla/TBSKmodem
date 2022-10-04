"""Amodem互換のマルチチャンネルOFDMモデム送受信クラスを定義します。
振幅信号とシンボルストリームを相互に変換します。
"""


from typing import Generic,TypeVar


from ..types import Sequence
from ..interfaces import IRoStream,IFilter
from ..streams.rostreams import BasicRoStream





T=TypeVar("T")
class AggregateFilter(IFilter[IRoStream[T],Sequence[T]],BasicRoStream[Sequence[T]],Generic[T]):
    """ T型のストリームから、length個づつ要素を読み出します。
        読み出し元が終端した場合、lengthまでパディングします。
    """
    def __init__(self,length:int,pad:T):
        """
            Args:
            pad パディングに使う要素
        """
        super().__init__()
        self._pad=pad
        self._pos=None
        self._src=None
        self._length=length
        self._is_eos=None
    def setInput(self,src:IRoStream[T])->"AggregateFilter[T]":
        self._is_eos=True if src is None else False
        self._pos=0
        self._src=src
        return self
    def __next__(self)->Sequence[T]:
        if self._is_eos:
            raise StopIteration()
        r=None
        try:
            r=self._src.gets(self._length)
            if len(r)<self._length:
                r=[i for i in r]
                while len(r)<self._length:
                    r.append(self._pad)
            self._pos+=1 #posのインクリメント
            return r
        except StopIteration as e:
            #1個も取れなかった時しか発生しないハズ。
            self._is_eos=True
            raise StopIteration(e)
    @property
    def pos(self):
        return self._pos