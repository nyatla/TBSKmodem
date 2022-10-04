from typing import Union
import struct
from abc import ABC

from .rostreams import BasicRoStream,FlattenRoStream
from ..interfaces import IByteStream,IBytesProvider
from ..types import Iterator,Deque

class BasicByteStream(BasicRoStream[int],IByteStream,ABC):
    def getAsUInt32be(self)->int:
        """BigEndianのUint32を読み出す
        """
        r=0
        for i in self.gets(4):
            r=r<<8|i
        return r
    def getAsByteArray(self,maxsize)->bytearray:
        """gets関数をラップします。
        """
        r=bytearray()
        # print(self.gets(maxsize))
        # return struct.pack("B",self.gets(maxsize))
        for i in self.gets(maxsize):
            r.append(i)
        return r
    





class FlattenByteStream(BasicByteStream):
    """bytes型の再帰構造Iteratorを直列化するストリームです。
    最上位以外にあるイテレータは値の取得時に全て読み出されます。
    """
    def __init__(self,src:Iterator[Union[IBytesProvider,bytes,int]]):
        super().__init__()
        self._pos=0
        self._src=FlattenRoStream[Union[IBytesProvider,bytes,int]](src)
        self._q=Deque()
    def __next__(self):
        q=self._q        
        if len(q)<1:
            s=next(self._src)
            # print(type(s),isinstance(s,IBytesProvider))
            if isinstance(s,bytes):
                q.extend(struct.unpack("%dB"%(len(s)),s))        
            elif isinstance(s,IBytesProvider):
                s=s.toBytes()
                q.extend(struct.unpack("%dB"%(len(s)),s))
            elif isinstance(s,int):
                assert(s<256 and s>=0)
                q.append(s)
            else:
                raise Exception("Invalid type:"+str(type(s)))
        self._pos+=1 #posのインクリメント
        return q.popleft()
    @property
    def pos(self):
        return self._pos

# class ConstByteStream(BasicByteStream):
#     """指定数の0を返すbyteStream
#     """
#     def __init__(self,size:int,value=0):
#         super().__init__()
#         self._size=size
#         self._value=value
#     def __next__(self)->int:
#         if self._size>0:
#             self._size-=1
#             return self._value
#         print(self._size)
#         self._pos+=1 #posのインクリメント

#         raise StopIteration()
#     @property
#     def pos(self):
#         return self._pos