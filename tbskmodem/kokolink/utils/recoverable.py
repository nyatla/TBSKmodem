from typing import Generic,TypeVar,Union

from ..types import NoneType,Generator, Iterator,Tuple

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

        このクラスは、(exception,T)を返すgeneratorをラップして、recoverで再実行可能な状態にします。
        generatorはnextで再実行可能な状態でなければなりません。
    """
    def __init__(self,g:Generator[Tuple[Union[StopIteration,RecoverableStopIteration],T],NoneType,NoneType]):
        """ ジェネレータをラップしたインスタンスを生成します。
        ラップするジェネレータは、nextでe,T型の例外種別と戻り値を返す必要があります。

        generatorの戻り値[0]は、None,StopException,RecoverableStopInterationのみが許されます。
        """
        self._g:Generator[T,NoneType,NoneType]=g
        return



    def recover(self)->T:
        """ 例外発生元のジェネレータを再実行します。
        """
        e,r=next(self._g) #戻り値,Exceptionを受取
        # print("R","e=",type(e),"g=",self._g,"r=",r)
        if e is None:
            #例外なし→成功
            # print("OK")
            self.close()
            return r
        if isinstance(e,RecoverableStopIteration):
            #再実行依頼→変化なしでRaise
            # print("raise self")
            raise self
        #何らかの例外があればGeneratorを閉じる
        self.close()
        if isinstance(e,StopIteration):
            # print("raise stop")
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

