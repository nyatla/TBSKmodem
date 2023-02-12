from typing import Generic,TypeVar
from ..interfaces import IRecoverableIterator
from ..types import Iterator
from .AsyncMethod import AsyncMethod
T=TypeVar("T")


class RecoverableStopIteration(StopIteration,Generic[T]):
    """ リカバリー可能なStopIterationです。
        イテレータチェーンのスループット調停などで、イテレータが再実行の機会を与えるために使います。
        この例外を受け取ったハンドラは、__next__メソッドを実行することで前回失敗した処理を再実行することができます。
        再実行を行わない場合はStopIterationと同じ振る舞いをしますが、異なる処理系ではセッションのファイナライズ処理が必要かもしれません。
    """

class RecoverableException(Exception,Generic[T]):
    """ リカバリー可能なメソッドが創出する例外です。
        送出元のメソッドはrecoverメソッドを呼び出すことで再実行できます。
        再実行した関数は、再びRecoverableExceptionをraiseする可能性もあります。

        再実行しない場合は、例外ハンドラでclose関数で再試行セッションを閉じてください。
    """
    def __init__(self,recover_instance:AsyncMethod[T]):
        self._recover_instance=recover_instance
    def detach(self)->AsyncMethod[T]:
        if self._recover_instance is None:
            raise RuntimeError()
        r = self._recover_instance
        self._recover_instance = None
        return r
    def close(self):
        if self._recover_instance is not None:
            self._recover_instance.close()






class NoneRestrictIteraor(IRecoverableIterator[T]):
    """ Noneの混在したストリームで、Noneを検出するたびにRecoverableStopInterationを発生します。
        None混在の一般IteratorをIRecoverableIteratorに変換します。
    """
    def __init__(self,iter:Iterator[T]):
        self._iter=iter
    def __next__(self) ->T:
        r=next(self._iter)
        if r is None:
            raise RecoverableStopIteration()
        return r
class SkipRecoverIteraor(Iterator[T]):
    """ IRecoverableIteratorを一般Iteratorをに変換します。
    """
    def __init__(self,iter:Iterator):
        self._iter=iter
    def __next__(self) ->T:
        while True:
            try:
                return next(self._iter)
            except RecoverableStopIteration:
                # print("skip")
                continue

