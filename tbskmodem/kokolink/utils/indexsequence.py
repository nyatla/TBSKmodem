from typing import Sequence, Iterable, Tuple
from .math.XorShiftRand31 import XorShiftRand31
from .math.GrayCode import GrayCode






class IndexSequence(Tuple[int]):
    """ 長さNの0からN-1までの数値を格納したタプルです。
    """
    def __new__(cls,__iterable:Iterable[int]):
        r=super().__new__(cls,__iterable)
        return r
    def inverse(self)->"IndexSequence":
        """ 逆写像を返します。この数列は、元の数列で置換した要素を元の位置に戻すときに使います。
        """
        d=[None]*len(self)
        for i,s in enumerate(self):
            d[s]=i
        return IndexSequence(d)
    def replace(self,d:Sequence[any])->Sequence[any]:
        """ 配列dを再配置した新しい配列を返します。
        """
        assert(len(d)==len(self))
        return [d[i] for i in self]




class FisherYatesIndex(IndexSequence):
    """ FisherYatesのアルゴリズムを用いたインデクス配列です。
    """
    def __new__(cls,length:int,seed:int=25):
        rand=XorShiftRand31(seed)
        s=[i for i in  range(length)]
        #
        for i in range(length-1,0,-1):
            j = rand.randRange(i + 1)
            temp = s[i]
            s[i] = s[j]
            s[j] = temp
        return super().__new__(cls,s)

class RowColumnIndex(IndexSequence):
    """ RowColumnのアルゴリズムを用いたインデクス配列です。
    """
    def __new__(cls,m:int,n:int):
        x = [ x for x in range(n * m)]
        y = [ (i % m) * n + i // m for i in x]
        return super().__new__(cls,y)

class GrayCodeIndex(IndexSequence):
    """ GrayCodeのアルゴリズムを用いたインデクス配列です。
    """   
    def __new__(cls,bit:int):
        return super().__new__(cls,GrayCode.genArray(bit))
      
      

# f=RowColumn(2,5)
# print(f)
