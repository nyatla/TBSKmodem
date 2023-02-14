from math import sqrt
from typing import Union


from .ISelfCorrcoefIterator import ISelfCorrcoefIterator
from ....types import Deque, Iterable, Iterator
from ...recoverable import RecoverableStopIteration

class SelfCorrcoefIterator(ISelfCorrcoefIterator):
    """ src[:]とsrc[shift:]の相関を返すストリームです。
        n番目に区間[n,n+window]と[n+shift,n+shift+window]の相関値を返します。
        開始からwindow-shift個の要素は0になります。
        このクラスは誤差が蓄積する不具合があります。
    """
    def __init__(self,window:int,src:Union[Iterator[float],Iterable[float]],shift:int=0):
        self.xyi=[None]*window #Xi
        self.c=0 #エントリポイント
        self.n=0 #有効なデータ数
        self.sumxi=0
        self.sumxi2=0
        self.sumyi=0
        self.sumyi2=0
        self.sumxiyi=0
        self._srcx=src if isinstance(src,Iterator) else iter(src)
        self._srcy=Deque[float]()
        """初期化
        """
        self._srcy.extend([0]*shift)
        
        # for i in range(window-1):
        #     next(self)

    def __next__(self)->float:
        c=self.c
        l=len(self.xyi)
        m=c%l
        vx:float
        try:
            vx=next(self._srcx)
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)

        self._srcy.append(vx)
        vy=self._srcy.popleft()

        if self.xyi[m] is None:
            #値追加
            self.n+=1-0
            self.sumxi+=vx-0
            self.sumxi2+=vx**2-0
            self.sumyi+=vy-0
            self.sumyi2+=vy**2-0 
            self.sumxiyi+=vx*vy-0
        else:
            #値削除
            lxi,lyi=self.xyi[m]
            self.n+=1-1
            self.sumxi+=vx-lxi
            self.sumxi2+=vx**2-lxi**2
            self.sumyi+=vy-lyi
            self.sumyi2+=vy**2-lyi**2
            self.sumxiyi+=vx*vy-lxi*lyi

        self.xyi[m]=(vx,vy)

        self.c+=1
        assert(self.n>0)
        # if self.n==0:
        #     return None
        if self.n==1:
            return 1.

        sumxi=self.sumxi
        meanx_=sumxi/(self.n)
        sumxi2=self.sumxi2
        v=(sumxi2+(meanx_**2)*self.n-2*meanx_*sumxi)
        if v<0:
            v=0
        stdx=sqrt(v/(self.n-1))

        sumyi=self.sumyi
        meany_=sumyi/(self.n)
        sumyi2=self.sumyi2
        v=(sumyi2+(meany_**2)*self.n-2*meany_*sumyi)
        if v<0:
            v=0
        stdy=sqrt(v/(self.n-1))
        
        v=self.sumxiyi+self.n*meanx_*meany_-meany_*sumxi-meanx_*sumyi
        covxy=v/(self.n-1)
        r=0 if stdx*stdy==0 else covxy/(stdx*stdy)
        return 1. if r>1 else (-1 if r<-1 else r) 




# if __name__ == '__main__':
#     import math
#     import numpy as np


#     def original(l,d1,d2):
#         r=[]
#         for i in range(len(d1)-l):
#             r.append(np.corrcoef(d1[i:i+l],d2[i:i+l])[0][1])
#         return r
#     def manual(l,d1,d2):
#         r=[]
#         for i in range(len(d1)-l):
#             # s1=np.std(d1[i:i+l],ddof=1)
#             # s2=np.std(d2[i:i+l],ddof=1)
#             s=np.cov(d1[i:i+l],d2[i:i+l])[0][1]
#             # r.append(s/(s1*s2))
#             r.append(s)
#         return r

#     def optimized(l,d1,d2):
#         r=[]
#         c=CorrcoefStream(l,iter(d1),iter(d2))
#         # c=SelfCorrcoefStream(l,iter(d1),90)
#         c=[i for i in c]
#         print(len(c))
#         return c
#     def optimizeds(l,d1,s):
#         r=[]
#         c=SelfCorrcoefStream(l,iter(d1),s)
#         c=[i for i in c]
#         print(len(c))
#         return c
#     src=[math.sin(math.pi*2/360*i) for i in range(3600)]
#     d1=src[20:]
#     d2=src[:-20]
#     # [d*abs(math.cos(math.pi*2/360*i)) for i,d in enumerate(d1)]

#     import matplotlib.pyplot as plot


#     fig = plot.figure()
#     ax1 = fig.add_subplot(4, 1, 1)
#     ax2 = fig.add_subplot(4, 1, 2)
#     ax3 = fig.add_subplot(4, 1, 3)
#     ax4 = fig.add_subplot(4, 1, 4)
#     ax1.plot(d1)
#     ax1.plot(d2)
#     # ax2.plot(optimized(10,d1,d2))
#     ax2.plot(original(10,d1,d2))

#     import time
#     time_sta = time.perf_counter()
#     original(10,d1,d2)
#     time_end = time.perf_counter()
#     print("original",time_end- time_sta)

#     time_sta = time.perf_counter()
#     ax3.plot(optimized(10,d1,d2))
#     time_end = time.perf_counter()
#     print("oprimized",time_end- time_sta)

#     time_sta = time.perf_counter()
#     ax3.plot(optimizeds(10,d1,20))
#     time_end = time.perf_counter()
#     print("oprimizeds",time_end- time_sta)

#     plot.draw()
#     plot.show()