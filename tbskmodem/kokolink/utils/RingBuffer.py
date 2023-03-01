from typing import overload,TypeVar,Generic

from ..types import List,Iterable,Iterator
T=TypeVar("T")
class RingBuffer(Generic[T]):
    """ スライス可能なリングバッファ。
    """
    @overload
    def __init__(self,length:int,pad:T):
        ...
    def __init__(self,*args,**kwds):
        if len(args)==2: #2引数の時だけにした
            self._buf=[args[1]]*args[0]
        else:
            raise TypeError()
        assert(len(self._buf)>0)
        self._p=0 #次の書き込み位置. データの先頭位置.+1でデータの末尾

    def append(self,v:T)->T:
        length=len(self._buf)
        ret=self._buf[self._p]
        self._buf[self._p]=v
        self._p=(self._p+1)%length
        return ret
    def extend(self,v:Iterable[T]):
        for i in v:
            self.append(i)
    
    class SubIter(Iterator[T]):
        def __init__(self,buf,pos,size):
            assert(size<len(buf))
            self._size=size
            self._pos=pos
            self._buf=buf
        def __next__(self):
            if self._size<1:
                raise StopIteration()
            self._size=self._size-1
            p=self._pos
            self._pos=(self._pos+1)%len(self._buf)
            return self._buf[p]

    def subIter(self,pos:int,size:int)->Iterator[int]:
        """ 現在のpos位置からsize個の要素を返すイテレータを生成して返します。
            返却値はバッファを直接参照します。内容が変更された場合、イテレータの返却値は影響を受けます。
            内容変更の可能性がある関数は、__getitem__,append,extendです。
        """
        return self.SubIter(self._buf,(pos+self._p)%len(self._buf),size)

    @property
    def tail(self)->T:
        """ バッファの末尾 もっとも新しい要素"""
        length=len(self._buf)
        return self._buf[(self._p-1+length)%length]
    @property
    def top(self)->T:
        """ バッファの先頭 最も古い要素"""
        return self._buf[self._p]
    # def __iter__(self)->List:
    #     return self[:] #いらないとおもう。

    def __getitem__(self,s)->List[T]:
        """ 通常のリストにして返します。
            必要に応じて再配置します。再配置せずに取り出す場合はsubIterを使用します。
        """
        b=self._buf
        if self._p!=0:
            self._buf= b[self._p:]+b[:self._p]
        self._p=0
        return self._buf[s]

    def __len__(self)->int:
        return len(self._buf)
    def __repr__(self)->str:
        return str(self._buf)


# rb=RingBuffer(10)
# for i in range(11):
#     rb.append(i)
# # print(rb.top,rb.tail)

# # rb.append(12)
# print(rb[:])
# print(rb.sublist(0,3))
# # print(rb.sublist(0,-1))
# # print(rb.top,rb.tail)
# # print(rb[:])