from typing import TypeVar

from ..types import Deque,Iterator,List
from .recoverable import RecoverableStopIteration
from ..interfaces import IRecoverableIterator
T=TypeVar("T")
class RecordableIterator(IRecoverableIterator[T]):
    """ イテレータを通過した値を記録します。
        出力先には取得元のイテレータと同じ振る舞いをします。
        このイテレータはRecoverableStopInterationを利用できます。
        
        このクラスはデバック用途を想定しています。パフォーマンスはよくありません。
        特にgetitemの動作は緩慢です。
    """
    def __init__(self,src:Iterator[T],is_rec=True):
        self._src=src
        self._q=Deque[float]()
        self._is_rec=is_rec
        self._buf=[]
    def __next__(self) -> T:
        try:
            v=next(self._src)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        if self._is_rec:
            self._q.append(v)
        return v
    def __len__(self):
        """ 現在の記録サイズ
        """
        return len(self._buf)+len(self._q)
    def _render(self):
        """ キューの中身をバッファへコピー
        """
        q=self._q
        l=len(self._q)
        self._buf=self._buf+[q.popleft() for i in range(l)]
    def rec(self):
        self._is_rec=True
    def pause(self):
        self._is_rec=False
    def clear(self):
        self._q.clear()
    def __getitem__(self,s):
        self._render()
        return self._buf[s]
    def toBuffer(self)->List[T]:
        self._render()
        return self._buf