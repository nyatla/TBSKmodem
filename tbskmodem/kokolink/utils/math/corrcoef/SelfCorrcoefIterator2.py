from math import sqrt
from typing import Union


from .ISelfCorrcoefIterator import ISelfCorrcoefIterator
from ....types import Deque, Iterable, Iterator
from ...recoverable import RecoverableStopIteration


class SelfCorrcoefIterator2(ISelfCorrcoefIterator):
    """ 31bit固定小数点で相関値を計算します。
    誤差蓄積はありませんが、精度と入力値に限界があります。
    小数点精度は31ビット、整数部は16ビットです。（多分）
    """
    def __init__(self,window:int,src:Union[Iterator[float],Iterable[float]],shift:int=0):
        self.xyi=[None]*window #Xi
        self.c=0 #エントリポイント
        self.n=0 #有効なデータ数
        self.sumxi:int=0
        self.sumxi2:int=0
        self.sumyi:int=0
        self.sumyi2:int=0
        self.sumxiyi:int=0
        self._srcx=src if isinstance(src,Iterator) else iter(src)
        self._srcy=Deque[float]()
        """初期化
        """
        self._srcy.extend([0]*shift)
        
        # for i in range(window-1):
        #     next(self)
    FP=30   #Fixes float point

    def __next__(self)->float:
        FP=SelfCorrcoefIterator2.FP
        c=self.c
        l=len(self.xyi)
        m=c%l
        vx:int
        try:
            dv:float=next(self._srcx)
            assert(-1<=dv and dv<=1)
            vx=(int)(dv*(1<<FP))
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)

        self._srcy.append(vx)
        vy:int=self._srcy.popleft()
        #pythonはNbit intなのでintcastは省略できる

        if self.xyi[m] is None:
            #値追加
            self.n+=1-0
            self.sumxi+=vx-0
            self.sumxi2+=((vx**2)>>FP)-0
            self.sumyi+=vy-0
            self.sumyi2+=((vy**2)>>FP)-0 
            self.sumxiyi+=((vx*vy)>>FP)-0
        else:
            #値削除
            lxi,lyi=self.xyi[m]
            self.n+=1-1
            self.sumxi+=vx-lxi
            self.sumxi2+=((vx**2)>>FP)-((lxi**2)>>FP)
            self.sumyi+=vy-lyi
            self.sumyi2+=((vy**2)>>FP)-((lyi**2)>>FP)
            self.sumxiyi+=((vx*vy)>>FP)-((lxi*lyi)>>FP)

        self.xyi[m]=(vx,vy)

        self.c+=1
        assert(self.n>0)
        # if self.n==0:
        #     return None
        if self.n==1:
            return 1.
        sumxi_:float=float(self.sumxi)/(1<<FP)
        meanx_=sumxi_/self.n
        sumxi2_=float(self.sumxi2)/(1<<FP)
        v=(sumxi2_+(meanx_**2)*self.n-2*meanx_*sumxi_)
        if v<=0:
            return 0
        stdx:float=sqrt(v/(self.n-1))
        if(stdx<(1./(1<<FP))):
            return 0

        sumyi_=float(self.sumyi)/(1<<FP)
        meany_=sumyi_/(self.n)
        sumyi2_=float(self.sumyi2)/(1<<FP)
        v=(sumyi2_+(meany_**2)*self.n-2*meany_*sumyi_)
        if v<=0:
            return 0
        stdy=sqrt(v/(self.n-1))
        if(stdy<(1./(1<<FP))):
            return 0
        
        sumxiyi_:float=float(self.sumxiyi)/(1<<FP)
        v=sumxiyi_+self.n*meanx_*meany_-meany_*sumxi_-meanx_*sumyi_
        covxy=v/(self.n-1)
        r=covxy/(stdx*stdy)
        return 1. if r>1 else (-1 if r<-1 else r) 



