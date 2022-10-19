from typing import overload,TypeVar,Generic

from ..types import List,Sequence,Iterable,Tuple
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
    def sublist(self,pos:int,size:int)->Tuple[int,...]:
        """ リストの一部を切り取って返します。
            この関数はバッファの再配置を行いません。
        """
        l:int=len(self._buf)
        if pos>=0:
            p:int=self._p+pos
            if size>=0:
                assert(pos+size<=l)
                return tuple([self._buf[(p+i)%l] for i in range(size)])
            else:
                assert(pos+size+1>=0)
                return tuple([self._buf[(p+size+i+1)%l] for i in range(-size)])
        else:
            p:int=self._p+l+pos
            if size>=0:
                assert(l+pos+size<=l)
                return tuple([self._buf[(p+i)%l] for i in range(size)])
            else:
                assert(l+pos+size+1>=0)
                return tuple([self._buf[(p-i+l)%l] for i in range(-size)])



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
            必要に応じて再配置します。再配置せずに取り出す場合はsublistを使用します。
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