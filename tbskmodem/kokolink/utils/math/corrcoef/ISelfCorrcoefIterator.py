from ....interfaces import IRecoverableIterator
from ....types import Iterator
from .SelfCorrcoefIterator2 import SelfCorrcoefIterator2
from .SelfCorrcoefIterator import SelfCorrcoefIterator

class ISelfCorrcoefIterator(IRecoverableIterator[float]):
    def createNormalized(window:int,src:Iterator[float],shift:int):
        """正規化したdouble値の自己相関関数を返す。
        """
        return SelfCorrcoefIterator2(window,src,shift)
