"""
このモジュールには、ライブラリ全体で頻繁に使用する共通のインタフェイスを定義します。

"""
from typing import TypeVar,Generic
from abc import abstractmethod,ABC, abstractproperty


from .types import Tuple,Iterator
T=TypeVar("T")

class IRecoverableIterator(Iterator[T],Generic[T]):
    ...

class IRoStream(IRecoverableIterator[T],Generic[T],ABC):
    """gets/getを備えた読み出し専用ストリームです。Iteratorと互換性があります。
    このストリームは内部状態を持つ読み出しストリームに使用できます。
    """
    @abstractmethod
    def __next__(self)->T:
        pass
    @abstractmethod
    def seek(self,size:int):
        """ストリームの先頭を移動します。
        終端に到達するとStopIterationをスローします。
        """
        pass
    @abstractmethod
    def get(self)->T:
        """ストリームの先頭から1要素を要素を取り出します。
        終端に到達するとStopIterationをスローします。
        """
        pass
    @abstractmethod
    def gets(self,size:int,fillup:bool=False)->Tuple[T]:
        """ストリームから最大でsize個の要素を取り出します。戻り値はsizeに満たないこともあります。
        終端に到達するとStopIterationをスローします。
        """
        pass
    @abstractproperty
    def pos(self)->int:
        """ストリーム上の現在の読み出し位置です。get/getsで読み出した要素数+seekで読み出した要素数の合計です。
        """
        pass

class IPeekableStream(IRoStream[T],Generic[T],ABC):
    """Peek/Seek、及び任意サイズのPeek/Seek機能を備えたストリームインタフェイスです。
    Iteratorはgetのラッパーとして機能します。
    このストリームは内部状態を持つストリームに使わないでください。
    """
    @abstractmethod
    def peek(self,skip:int=0)->int:
        """読み出し位置を移動せずに1要素を取り出します。
        Args:
            skip 読み出し位置までのスキップ数です。
        """
        pass
    @abstractmethod
    def peeks(self,size:int,skip=0,fillup:bool=False):
        """読み出し位置を移動せずに最大でsize個の要素を取り出します。戻り値はsizeに満たないこともあります。
        Args:
            size 読み出しサイズです。
            skip 読み出し位置までのスキップ数です。
            fillup 戻り値のサイズをsizeに強制するフラグです。

        """
        pass


class IByteStream(IRoStream[int],ABC):
    """Byte値のストリームです。返却型はbyteの値範囲を持つintです。
    """
    def getAsUInt32be(self)->int:
        """byteStreamから32bit unsigned int BEを読み出します。
        """
        pass
    def getAsByteArray(self,size)->bytearray:
        """byteStreamから指定サイズのbytearrayを読み出します。
        """
        pass

class IBitStream(IRoStream[int],ABC):
    """ Bit値を返すストリームです。返却型は0,1の値範囲を持つintです。
    """

class IReader(Generic[T],ABC):
    """Tから値を読み出します。このクラスは分類であり関数を持ちません。
    """

class IScanner(Generic[T],ABC):
    """Tの読み出し位置を変更せずに値を抽出します。このクラスは分類であり関数を持ちません。
    """





S=TypeVar("S")
D=TypeVar("D")

class IFilter(IRoStream[D],Generic[S,D],ABC):
    """入力と出力の型が異なるストリームです。
    ソース値のプロバイダSからD型の値を生成します。
    """
    @abstractmethod
    def setInput(self,src:S)->"IFilter[S,D]":
        """新しいソースをインスタンスにセットします。
        関数が終了した時点で、インスタンスの状態は初期状態に戻ります。
        内部キューがある場合、既に読み出された入力側の内部キューと、未出力の出力側のキューがある場合は値を破棄します。 
        
        ・望ましい実装

            Noneがセットされた場合は、インスタンスは終端状態になり、ブロックしているget(s)/peek(s)関数があればStopInterationを発生させて終了するべきです。
        """
        pass

class IEncoder(IFilter[S,D],Generic[S,D],ABC):
    """より物理値に近い情報を出力するストリームです。
    """

class IDecoder(IFilter[S,D],Generic[S,D],ABC):
    """より抽象値に近い情報を出力するストリームです。
    """

class IGenerator(IRoStream[T],Generic[T],ABC):
    """T型のストリームを生成するクラスです。
    ストリームクラスの亜種ですが、主にパラメーターから数列を生成するクラスの分類です。
    """
    pass



T=TypeVar('T')
class IConverter(Generic[T]):
    """ 同一型で値交換をする関数を定義します。
    """
    @abstractmethod
    def convert(self,src:T)->T:
        """ srcを同一型の異なる値に変換します。
        """




class IBytesProvider(ABC):
    """インスタンスの値をbytesにシリアライズできるクラスです。廃止予定。
    """
    def toBytes(self)->bytes:
        pass
