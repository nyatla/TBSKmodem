from doctest import DebugRunner
from typing import Generic,TypeVar,Union,Callable
from ..interfaces import IRecoverableIterator
from ..types import NoneType,Generator, Iterator,Tuple
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
    def __init__(self):
        ...
    
    def recover(self)->T:
        """ 関数を再試行します。再試行可能な状態で失敗した場合は、自分自信を返します。
        """
        ...
    def close(self):
        ...

# ASMETHOD=TypeVar("ASMETHOD",bound=AsyncMethod)
class AsyncMethodRecoverException(RecoverableException[AsyncMethod[T]],Generic[T]):
    """ AsyncMethodをラップするRecoverExceptionです。
        Recoverableをgeneratorで実装するときに使います。

        このクラスは、(exception,T)を返すgeneratorをラップして、recoverで再実行可能な状態にします。
        generatorはnextで再実行可能な状態でなければなりません。
    """
    def __init__(self,asmethod:AsyncMethod[T]):
        """
            Args:
        """
        self._asmethod:AsyncMethod[T]=asmethod
        return
    def recover(self)->T:
        """ 例外発生元のrunを再実行します。
            例外が発生した場合、closeを実行してそのまま例外を再生成します。
        """
        assert(self._asmethod is not None)
        try:
            if self._asmethod.run():
                # print("aaaa",self._asmethod.result)
                return self._asmethod.result
        except Exception as e:
            #runが例外を発生したときは内部closeに期待する。
            raise
        asmethod=self._asmethod
        self._asmethod=None
        raise AsyncMethodRecoverException(asmethod)
    def close(self):
        assert(self._asmethod is not None)
        try:
            self._asmethod.close()
        finally:
            self._asmethod=None



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

