from itertools import repeat
from typing import Deque, Iterator, Sequence,Generic, Union,TypeVar
from ..utils.indexsequence import IndexSequence






# class IndexSequence(Tuple[int]):
#     """ 長さNの0からN-1までの数値を格納したタプルです。
#     """
#     def __new__(cls,__iterable:Iterable[int]):
#         r=super().__new__(cls,__iterable)
#         return r
#     def inverse(self)->"IndexSequence":
#         """ 逆写像を返します。この数列は、元の数列で置換した要素を元の位置に戻すときに使います。
#         """
#         d=[None]*len(self)
#         for i,s in enumerate(self):
#             d[s]=i
#         return IndexSequence(d)


# class FisherYates(IndexSequence):
#     """ FisherYatesのアルゴリズムを用いたインデクス配列です。
#     """
#     def __new__(cls,length:int,seed:int=25):
#         rand=XorShiftRand31(seed)
#         s=[i for i in  range(length)]
#         #
#         for i in range(length-1,0,-1):
#             j = rand.randRange(i + 1)
#             temp = s[i]
#             s[i] = s[j]
#             s[j] = temp
#         return super().__new__(cls,s)

# class RowColumn(IndexSequence):
#     """ RowColumnのアルゴリズムを用いたインデクス配列です。
#     """
#     def __new__(cls,m:int,n:int):
#         x = [ x for x in range(n * m)]
#         y = [ (i % m) * n + i // m for i in x]
#         return super().__new__(cls,y)



      
      

# f=RowColumn(2,5)
# print(f)


from ..interfaces import IRoStream,IFilter
from ..streams.rostreams import BasicRoStream


T=TypeVar("T")
class ReplaceFilter(IFilter[IRoStream[T],Sequence[T]],BasicRoStream[Sequence[T]],Generic[T]):
    """ T型のストリームをIndexSequenceに従って再配置して返します。
        このストリームの返す要素数は常にIndexSequenceの倍数です。
        インデクスリストに満たない数で終端した場合、ストリームはpadで不足分を埋めます。

    """
    def __init__(self,index_seq:IndexSequence,pad:Union[T,Iterator[T]]):
        """
            Args:
            pad パディングに使う要素
        """
        super().__init__()
        self._pad=pad if isinstance(pad,Iterator) else repeat(pad)
        self._pos=None
        self._src=None
        self._is_eos=None
        self._q:Deque[T]
        self._index_seq=index_seq
    def setInput(self,src:IRoStream[T])->"ReplaceFilter[T]":
        self._is_eos=True if src is None else False
        self._pos=0
        self._src=src
        self._q=Deque[T]()
        return self
    def __next__(self)->Sequence[T]:
        if len(self._q)<1:
            if self._is_eos:
                raise StopIteration()
            r:None
            try:
                pack_len=len(self._index_seq)
                r=self._src.gets(pack_len)
                if len(r)==pack_len:
                    ...
                else:
                    # r=r+[cmath.rect(1,cmath.pi/16*i)for i in range(pack_len-len(r))]
                    r=r+tuple([next(self._pad)]*(pack_len-len(r)))
                self._q.extend(self._index_seq.replace(r))
            except StopIteration as e:
                #1個も取れなかった時しか発生しないハズ。
                self._is_eos=True
                raise StopIteration(e)
        r=self._q.popleft()
        self._pos+=1 #posのインクリメント
        return r
    @property
    def pos(self):
        return self._pos