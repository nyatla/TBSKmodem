
from typing import Union,Iterable,Iterator,Deque, overload,List
import struct
from ..interfaces import IByteStream
from ..utils.functions import isinstances
from .bytestreams import BasicByteStream



class ByteStream(BasicByteStream,IByteStream):
    """ iterをラップするByteStreamストリームを生成します。
        bytesの場合は1バイトづつ返します。
        strの場合はbytesに変換してから1バイトづつ返します。
    """
    @overload
    def __init__(self,src:Iterator[int],inital_pos:int=0):
        pass
    @overload
    def __init__(self,src:Iterable[int],inital_pos:int=0):
        pass
    @overload
    def __init__(self,src:bytes,inital_pos:int=0):
        pass
    @overload
    def __init__(self,src:str,inital_pos:int=0,encoding="utf-8"):
        pass



    def __init__(self,*args,**kwds):
        super().__init__()
        self._pos:int #現在の読み出し位置
        self._iter:Iterator[int]
        self._q:List #読み出しバッファ。
        def __init__A(src:Iterator[int],inital_pos:int=0):
            self._pos=inital_pos #現在の読み出し位置
            self._iter:Iterator[int]=src
            self._q=list() #読み出しバッファ。
        def __init__B(src:Iterable[int],inital_pos:int=0):
            __init__A(iter(src),inital_pos)
        def __init__C(src:bytes,inital_pos:int=0):
            s=struct.unpack("%dB"%(len(src)),src)
            __init__A(iter(s),inital_pos)
        def __init__D(src:str,inital_pos:int=0,encoding:str="utf-8"):
            __init__C(src.encode(encoding),inital_pos)
        if isinstances(args,[bytes],(kwds,{"inital_pos":int})):
            __init__C(*args,**kwds)
        elif isinstances(args,[str],(kwds,{"inital_pos":int,"encoding":str})):
            __init__D(*args,**kwds)
        elif isinstances(args,[Iterator],(kwds,{"inital_pos":int})):
            __init__A(*args,**kwds)
        elif isinstances(args,[Iterable],(kwds,{"inital_pos":int})):
            __init__B(*args,**kwds)
        else:
            raise Exception("Invalid type %s"%(type(args)))
    def __next__(self)->int:
        r=next(self._iter)
        self._pos=self._pos+1
        return r
    @property
    def pos(self):
        return self._pos
