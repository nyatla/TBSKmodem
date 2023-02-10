from ...types import List
import math

class Rms:
    """ [-1,1]の値のRMSを計算します。
    値は31ビット固定小数点で計算し、結果は16bitIntです。
    """
    FP = 30
    def __init__(self,length:int):
        assert(length < (1 << self.FP)) #31bitまで
        self._buf:List[int]=[0]*length
        self._ptr:int=0
        self._sum:int=0

    def update(self, d:float)->"Rms":
        v:float = min(1,max(d,-1))
        iv:int = round(v * v * (1 << self.FP)) #31bit int
        buf = self._buf
        self._sum = self._sum + iv - buf[self._ptr] #Σx^2
        buf[self._ptr] = iv
        self._ptr = (self._ptr + 1) % len(buf)
        return self

    def getLastRms(self)->float:
        #√(Σx^2/0x7fffffff/n)
        return math.sqrt(float(self._sum) / (1 << self.FP) / len(self._buf))