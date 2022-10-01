from types import NoneType
from typing import Callable, Generator, Iterator,TypeVar,Generic,Union,Any



T=TypeVar("T")

class RecoverableIterator(Iterator[T],Generic[T]):
    ...

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

class GeneratorRecoverException(RecoverableException[T],Generic[T]):
    """ generator[exception,any]]をラップするRecoverExceptionです。
        Recoverableをgeneratorで実装するときに使います。
        exceptionがNoneの場合、値を正常値として扱います。not Noneの場合はその値を例外オブジェクトとして扱います。
        Generatorの戻り値[0]は、None,StopException,RecoverableStopInterationのみが許されます。
    """
    def __init__(self,exception:Exception,g:Generator[T,NoneType,NoneType]):
        if isinstance(exception,RecoverableStopIteration):
            self._g:Generator[T,NoneType,NoneType]=g
        elif isinstance(exception,StopIteration):
            g.close()
            raise exception
        else:
            g.close()
            raise RuntimeError("Bad exception")
    def recover(self)->T:
        e,r=next(self._g) #戻り値,Exceptionを受取
        # print("R","e=",type(e),"g=",self._g,"r=",r)
        if e is None:
            # print("OK")
            self.close()
            return r
        if isinstance(e,RecoverableStopIteration):
            # print("raise self")
            raise self
        #未知のエラーならセッションを閉じてRaise
        self.close()
        if isinstance(e,StopIteration):
            raise e
        if isinstance(e,Exception):
            raise e
        raise RuntimeError()
    def close(self):
        # print("closed")
        if self._g is None:
            return
        self._g.close()
        self._g=None

class NoneRestrictIteraor(RecoverableIterator[T]):
    """ Noneの混在したストリームで、Noneを検出するたびにRecoverableStopInterationを発生します。
        None混在の一般IteratorをRecoverableIteratorに変換します。
    """
    def __init__(self,iter:Iterator[T]):
        self._iter=iter
    def __next__(self) ->T:
        r=next(self._iter)
        if r is None:
            raise RecoverableStopIteration()
        return r
class SkipRecoverIteraor(Iterator[T]):
    """ RecoverableIteratorを一般Iteratorをに変換します。
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

