from typing import Union,Generic,TypeVar
from abc import ABC



from ..types import Iterable, Iterator, List,Tuple
from ..interfaces import IRoStream,IPeekableStream
from ..utils.recoverable import  RecoverableStopIteration


T=TypeVar("T")

class BasicRoStream(IRoStream[T],Generic[T],ABC):
    """ IRoStreamの基本実装です。
    __next__,posメソッドを実装することで機能します。seek,getsはgetをラップしてエミュレートします。
    __next__メソッドの中でself#_posを更新してください。
    """
    def __init__(self):
        self._savepoint:List=None
    def get(self)->T:
        if self._savepoint is not None and len(self._savepoint)>0:
            #読出し済みのものがあったらそれを返す。
            r=self._savepoint[0]
            self._savepoint=self._savepoint[1:]
            if len(self._savepoint)==0:
                self._savepoint=None
            return r
        return next(self)
    def gets(self,maxsize:int,fillup:bool=False)->Tuple[T]:
        r=self._savepoint if self._savepoint is not None else []
        self._savepoint=None
        try:
            for _ in range(maxsize-len(r)):
                r.append(next(self))
        except RecoverableStopIteration as e:
            self._savepoint=r
            raise RecoverableStopIteration(e)
        except StopIteration as e:
            if fillup or len(r)==0:
                raise StopIteration(e)
        return tuple(r)
    def seek(self,size:int):
        try:
            self.gets(size,fillup=True)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        except StopIteration as e:
            raise StopIteration(e)
        return
        










class FlattenRoStream(BasicRoStream[T],Generic[T]):
    """T型の再帰構造のIteratorを直列化するストリームです。
    最上位以外にあるインレータは値の取得時に全て読み出されます。
    T型はIterator/Iterable/Noneな要素ではないことが求められます。
    """
    def __init__(self,src:Union[Iterator[T],Iterable[T]]):
        super().__init__()
        self._pos=0
        def toIterator(s):
            if isinstance(s,Iterable):
                return iter(s)
            else:
                return s
        def rextends(s:Union[Iterator[T],Iterable[T]]):
            while True:
                try:
                    i=next(s)
                except RecoverableStopIteration:
                    yield None
                    continue
                except StopIteration:
                    break
                if isinstance(i,(Iterable,Iterator)) and not isinstance(i,(str,bytes)):
                    yield from rextends(toIterator(i))
                    continue
                else:
                    yield i
                    continue

        self._gen=rextends(toIterator(src))
    def __next__(self):
        r=next(self._gen)
        if r is None:
            raise RecoverableStopIteration()
        self._pos+=1 #posのインクリメント
        return r
    @property
    def pos(self):
        return self._pos



class PeekRoStream(BasicRoStream[T],Generic[T]):
    """PeekableStreamをラップしてPeekを使ったRoStreamを生成します。
    ラップしているストリームを途中で操作した場合、このインスタンスの取得値は影響を受けます。
    """
    def __init__(self,src:IPeekableStream):
        self._src=src
        self._pos=0
    def __next__(self)->T:
        try:
            r=self._src.peek(self._pos)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        self._pos+=1
        return r
    def pos(self)->int:
        return self._pos
        


