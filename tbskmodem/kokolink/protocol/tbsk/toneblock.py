import math
from typing import overload
from collections import UserList

from ...utils.math import MSequence
from ...utils.math import XorShiftRand31
from ...types import Iterator,Tuple,Sequence


class TraitTone(UserList):
    def __init__(self,d:Sequence[float]):
        super().__init__(d)
    def mul(self,v:float)->"TraitTone":
        """ 信号強度をv倍します。
        """
        for i in range(len(self)):
            self[i]=self[i]*v
        return self


class SinTone(TraitTone):
    """ Sin波形のトーン信号です。
        このトーン信号を使用したTBSKはDPSKと同じです。
    """
    def __init__(self,points:int,cycle:int=1):
        s=math.pi*2/points*0.5
        super().__init__([math.sin(s+i*math.pi*2/points) for i in range(points)]*cycle)


class MSeqTone(TraitTone):
    """ トーン信号を巡回符号でBPSK変調した信号です。
        2^bits-1*len(base_tone)の長さです。
    """
    @overload
    def __init__(self,mseq:MSequence,base_tone:TraitTone=None):
        self._sequence:Tuple(int)
        ms=mseq.getCyclesMap()
        tone=base_tone if base_tone is not None else SinTone(20,1)
        self._sequence=tuple(ms)
        a=sum([[j*(i*2-1) for j in tone] for i in ms],[]) #flatten
        super(type(self),self).__init__(a)
    @property
    def sequence(self):
        return self._sequence




class PnTone(TraitTone):
    """ トーン信号をPN符号でBPSK変調した信号です。
        intervalティック単位で変調します。
    """
    def __init__(self,seed:int,interval:int=2,base_tone:TraitTone=None):
        tone=base_tone if base_tone is not None else SinTone(20,8)
        pn=XorShiftRand31(seed,skip=29)
        c=0
        f:int=0
        d=[]
        for i in tone:
            if c%interval==0:
                f=(next(pn) & 0x02) -1
            c=c+1
            d.append(i*f)
        super(type(self),self).__init__(d)


class XPskSinTone(TraitTone):
    """ Sin波形をXPSK変調したトーン信号です。
        1Tick単位でshiftイテレータの返す値×2pi/divの値だけ位相をずらします。
    """
    def __init__(self,points:int,cycle:int=1,div:int=8,shift:Iterator[int]=None):
        """
            Args:
            shift   -1,0,1の3値を返すイテレータです。省略時は乱数値です。
        """
        delta=math.pi*2/points
        shift=self.DefaultIter() if shift is None else shift
        s=delta*0.5
        d=[]
        for i in range(points*cycle):
            s=s+delta+next(shift)*(math.pi*2/div)
            d.append(math.sin(s))
        super(type(self),self).__init__(d)
    class DefaultIter(Iterator[int]):
        def __init__(self):
            self._pn=XorShiftRand31(999,skip=299)
        def __next__(self)->int:
            return ((next(self._pn)&0x01)*2-1)

    



