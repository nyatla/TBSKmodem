from typing import overload,TypeVar

from ...utils.recoverable import RecoverableStopIteration
from ...streams.rostreams import BasicRoStream
from ...interfaces import IDecoder, IEncoder,IBitStream,IRoStream
from ...utils.functions import isinstances
from ...utils.math.corrcoef import SelfCorrcoefIterator
from ...utils import SumIterator
from .toneblock import TraitTone
from ...types import Deque, Iterator,Tuple

class WaitForInputException(Exception):
    ...




T=TypeVar("T")





class AverageInterator(SumIterator[T]):
    """ 末尾からticksまでの平均値を連続して返却します。
        このイテレータはRecoverableStopInterationを利用できます。
    """
    @overload
    def __init__(self,src:Iterator[T],ticks:int):
        ...
    def __init__(self,*args,**kwds):
        self._length:int
        def __init__B(src:Iterator[T],ticks:int):
            super(self.__class__,self).__init__(src,ticks)
            self._length=ticks
        if isinstances(args,(Iterator,int,)):
            __init__B(*args,**kwds)
        else:
            raise TypeError()
    def __next__(self) -> T:
        try:
            r=super().__next__()
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)
        return r/self._length


class TraitBlockEncoder(IEncoder[IBitStream,int],BasicRoStream[float]):
    """ ビット列をTBSK変調した振幅信号に変換します。出力レートは入力のN倍になります。
        N=len(trait_block)*2*len(tone)
        このクラスは、toneを一単位とした信号とtrail_blockとの積を返します。
    """
    @overload
    def __init__(self,tone:TraitTone):
        ...
        ...
    def __init__(self,*args,**kwds):
        self._sblock:Tuple[int]
        self._btone:TraitTone
        # self._symbol_tone_size:int
        def __init__B(tone:TraitTone):
            self._sblock=[-1] #-1,1にする
            self._btone=tone
            # self._symbol_tone_size=len(self._btone)*2
        if isinstances(args,(TraitTone,)):
            __init__B(*args,**kwds)
        else:
            raise TypeError()
        self._q=None
        super().__init__()
    """
        Kビットは,N*K+1個のサンプルに展開されます。
    """
    def setInput(self,src:IBitStream)->"TraitBlockEncoder":
        self._is_eos=True if src is None else False
        self._pos=0
        self._src=src
        self._tone_q=Deque[float]()
        # print(len(self._tone_q))
        return self
    def __next__(self)->float:
        if len(self._tone_q)==0:
            if self._is_eos:
                raise StopIteration()
            try:
                sign=1 if next(self._src)!=0 else -1
                for i in self._sblock:
                    self._tone_q.extend([sign*i*j for j in self._btone])
            except StopIteration as e:
                self._is_eos=True
                raise StopIteration(e)

        r=self._tone_q.popleft()
        self._pos+=1 #posのインクリメント
        return r
    @property
    def pos(self):
        return self._pos


class TraitBlockDecoder(IBitStream,IDecoder[IRoStream[float],int],BasicRoStream[int]):
    """ シンボル幅がNのTBSK相関信号からビットを復調します。

    """
    @overload
    def __init__(self,trait_block_ticks:int,threshold:float=0.2):
        ...
    def __init__(self,*args,**kwds):
        self._trait_block_ticks:int
        self._avefilter:AverageInterator[float]
        self._threshold:float
        self._is_eos:bool=True
        def __init__B(trait_block_ticks:int,threshold:float=0.2):
            self._trait_block_ticks=trait_block_ticks
            self._threshold=threshold
        if isinstances(args,(int,)):
            __init__B(*args,**kwds)
        else:
            raise TypeError()
        self._q=None
    class getResultAsint(int):
        def __new__(cls,v:int,ext:Tuple[int,float,int]):
            """
                Args:
                    元ストリームの位置,検出値,平均値を取得したTickのサイズ
            """
            r=super().__new__(cls,v)
            r._ext=ext #
            return r
        @property
        def pos(self)->int:
            """元ストリームの位置"""
            return self._ext[0]
        @property
        def rate(self)->int:
            """検出値"""
            return self._ext[1]
        @property
        def ticks(self)->int:
            """平均値を取得したTickのサイズ"""
            return self._ext[2]


    def setInput(self,src:IRoStream[float])->"TraitBlockDecoder":
        """ 
            Args:
                src
                    TBSK信号の開始エッジにポインタのあるストリームをセットします。
        """
        self._is_eos=True if src is None else False
        self._pos=0
        self._src=src
        self._cof=SelfCorrcoefIterator(self._trait_block_ticks,src,self._trait_block_ticks)
        ave_window=max(int(self._trait_block_ticks*0.1),2) #検出用の平均フィルタは0.1*len(tone)//2だけずれてる。個々を直したらtbskmodem#TbskModulatorも直せ
        self._avefilter=AverageInterator[float](self._cof,ave_window)
        self._last_data=0

        self._preload_size=self._trait_block_ticks+ave_window//2-1    #平均値フィルタの初期化サイズ。ave_window/2足してるのは、平均値の遅延分.
        self._block_skip_size=self._trait_block_ticks-1-2 #スキップ数
        self._block_skip_counter=self._block_skip_size #スキップ数
        self._samples=[] #観測値
        # try:
        #     [next(self._avefilter) for i in range(self._trait_block_ticks+ave_window//2)]
        # except StopIteration:
        #     self._is_eos=True
        return self
                    
    def __next__(self)->int:
        if self._is_eos:
            raise StopIteration()
        try:
            #この辺の妙なカウンターはRecoverableStopInterationのため


            #平均イテレータの初期化(初めの一回目だけ)
            while self._preload_size>0:
                next(self._avefilter)
                self._preload_size=self._preload_size-1
            #ブロックヘッダの読み出し(1ブロック読出しごとにリセット)
            while self._block_skip_counter>0:
                next(self._avefilter)
                self._block_skip_counter=self._block_skip_counter-1
            while len(self._samples)<3:
                self._samples.append(next(self._avefilter))




            r=self._samples[1]
            sample=self._samples
            if sample[0]*sample[1]<0 or sample[1]*sample[2]<0:
                #全ての相関値が同じ符号でなければ何もしない
                self._block_skip_counter=self._block_skip_size #リセット
            else:
                #全ての相関値が同じ符号
                samples=[abs(i) for i in self._samples]
                #一番大きかったインデクスを探す
                if samples[1]>samples[0] and samples[1]>samples[2]:
                    #遅れも進みもしてない
                    self._block_skip_counter=self._block_skip_size
                    # print(0)
                elif samples[0]>samples[2]:
                    #探索場所が先行してる
                    self._block_skip_counter=self._block_skip_size-1
                    # print(-1)
                else:
                    #探索場所が遅行してる
                    self._block_skip_counter=self._block_skip_size+1 
                    # print(+1)



            self._samples=[]

            # print(self._src.pos,r)
            th=self._threshold
            self._pos=self._pos+1
            if r>th:
                # print(1,1)
                self._last_data=r
                return self.getResultAsint(1,(self._src.pos,r,self._trait_block_ticks))
            elif r<-th:
                # print(2,0)
                self._last_data=r
                return self.getResultAsint(0,(self._src.pos,r,self._trait_block_ticks))
            elif self._last_data-r>th:
                # print(3,1)
                self._last_data=r
                return self.getResultAsint(1,(self._src.pos,r,self._trait_block_ticks))
            elif r-self._last_data>th:
                # print(4,0)
                self._last_data=r
                return self.getResultAsint(0,(self._src.pos,r,self._trait_block_ticks))
            else:
                self._is_eos=True
                raise StopIteration()
        except RecoverableStopIteration as e:
            raise RecoverableStopIteration(e)            
        except StopIteration as e:
            self._is_eos=True
            raise StopIteration(e)
    @property
    def pos(self):
        return self._pos
