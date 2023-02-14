from ...types import Union,Iterable,Iterator
from ...utils.math.corrcoef import ISelfCorrcoefIterator
from ...utils.math.corrcoef import SelfCorrcoefIterator
from ...utils.math.corrcoef import SelfCorrcoefIterator2
class AlgorithmSwitch:
    """ 使用する実装を切り替えるスイッチ
    """
    @staticmethod
    def createSelfCorrcoefIterator(window:int,src:Union[Iterator[float],Iterable[float]],shift:int=0)->ISelfCorrcoefIterator:
        return SelfCorrcoefIterator2(window,src,shift=shift)
