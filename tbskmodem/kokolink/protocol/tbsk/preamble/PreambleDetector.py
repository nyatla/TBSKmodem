from typing import TypeVar,Generic
from ....types import Tuple,Iterator
from ....interfaces import IRoStream,IRecoverableIterator

PREAMBLE=TypeVar("PREAMBLE")
DETECTED=TypeVar("DETECTED")


class PreambleDetector(IRecoverableIterator[DETECTED],Generic[PREAMBLE,DETECTED]):
    """ イテレーションの先頭からPreambleを検出するイテレータです。
        __next__関数で同期的にプリアンブルを検出してください。
        入力したイテレータは検出のために消費します。
        検出結果は検出器ごとに定義してください。
    """
    def __init__(self,src:IRoStream[float],preamble:PREAMBLE):
        """
        """
        super().__init__()
        self._src=src
        self._preamble=preamble
    