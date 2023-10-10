
from typing import TypeVar,Union

from tbskmodem.kokolink.protocol.tbsk.toneblock import TraitTone

from ....types import NoneType
from ....interfaces import IRoStream
from ....utils.recoverable import RecoverableStopIteration
from ....utils import RingBuffer,BufferedIterator,AsyncMethod
from ....streams import BitStream
from ..traitblockcoder import TraitBlockEncoder
from .Preamble import Preamble
from .PreambleDetector import PreambleDetector
from ..AlgorithmSwitch import AlgorithmSwitch


T=TypeVar("T")
class CoffPreamble(Preamble):
    @property
    def ticks(self):
        """ PreambleのTickサイズ
        """
        return len(self._symbol)
    DEFAULT_TH:float=1.0
    DEFAULT_CYCLE:int=4
    class PreambleBits(TraitBlockEncoder):
        def __init__(self,symbol:TraitTone,cycle:int):
            super().__init__(symbol)
            b=[1]*cycle
            c=[i%2 for i in range(cycle)]
            d=[(1+c[-1])%2,(1+c[-1])%2,c[-1],]
            self.setInput(BitStream(iter([0,1]+b+[1]+c+d),bitwidth=1))
            # return enc.setInput(BitStream(iter([0,1]+[1,1]+[1]+[0,1]+[0,0,1]),1))
            # return enc.setInput(BitStream(iter([0,1,1,1,1,0,1,0,0,1]),1))


    """ 台形反転信号プリアンブルです。
    """
    def __init__(self,tone:TraitTone,cycle:int=DEFAULT_CYCLE):
        self._symbol=tone
        self._cycle=cycle #平坦部分のTick数
    def getPreamble(self)->IRoStream[float]:
        return self.PreambleBits(self._symbol,self._cycle)




class AveLog(RingBuffer):
    """ 過去N個の平均値をM個記録します。
    """
    def __init__(self,nofave,nofbuf):
        super().__init__(nofbuf,0) #記録
        self._rb=RingBuffer[float](nofave,0) #平均値のためのキャッシュ
        self._sum=0.
    def append(self,v):
        a=self._rb.top
        self._rb.append(v)
        self._sum=self._sum+v-a
        super().append(self._sum/len(self._rb))


class TickLog(RingBuffer):
    """ 過去nofave個の平均値をnofbuf個記録します。
    """
    def __init__(self,nofbuf):
        super().__init__(nofbuf,0)
    def indexOfSum3Max(self,size_back):
        """ 過去N個の中で3値平均の最大の値とインデクスを探す.
            探索範囲は,+1,n-1となる。
            戻り値は[-(size_back-1),0]
        """
        assert(size_back>0)
        buflen=len(self)
        # 探索開始位置 RBの後端からsize_back戻ったところ
        siter=self.subIter(buflen-size_back,size_back)
        a=[next(siter),next(siter),next(siter)]        
        max_i=0
        max_v=sum(a)
        n=0
        for i in siter:
            s=sum(a)
            print(n,s)
            if s>max_v:
                max_i=n+1
                max_v=s
            a[n%3]=i
            n=n+1
        return max_i+1,max_v
    def max(self,start,size):
        """ 過去N個の中で最大の値とインデクスを探す.
            探索範囲は,+1,n-1となる。
            戻り値は[-(size_back-1),0]
        """
        assert(size>0)
        siter=self.subIter(start,size)
        max_v=next(siter)
        for i in siter:
            if i>max_v:
                max_v=i
        return max_v
    def min(self,start,size):
        """ 過去N個の中で最大の値とインデクスを探す.
            探索範囲は,+1,n-1となる。
            戻り値は[-(size_back-1),0]
        """
        assert(size>0)
        # 探索開始位置 RBの後端からsize_back戻ったところ
        siter=self.subIter(start,size)
        min_v=next(siter)
        for i in siter:
            if i<min_v:
                min_v=i
        return min_v    
    def ave(self,start,size):
        assert(size>0)
        # 探索開始位置 RBの後端からsize_back戻ったところ
        s=sum(self.subIter(start,size))
        return s/size


class CoffPreambleDetector(PreambleDetector[CoffPreamble,"CoffPreambleDetector.DetectedPreamble"]):
    """ このクラスはイテレータから１度だけPreambleを検出します。
    """
    DEFAULT_TH:float=1.0
    def __init__(self,src:IRoStream[float],preamble:CoffPreamble,threshold:float=DEFAULT_TH):
        super().__init__(src,preamble)
        symbol_ticks=preamble.ticks
        cycle=preamble._cycle
        sample_width=cycle+1
        #後で見直すから10シンボル位記録しておく。
        cofbuf_len=symbol_ticks*(6+cycle*2)
        self._cof=AlgorithmSwitch.createSelfCorrcoefIterator(symbol_ticks,self._src,symbol_ticks)
        self._average1=AveLog(symbol_ticks,symbol_ticks*sample_width)     #シンボル単位の平均値
        self._tickbuf=TickLog(cofbuf_len) #再度平均値

        self._sample_width=sample_width
        self._cofbuf_len=cofbuf_len
        self._symbol_ticks=symbol_ticks
        # self._rb=RingBuffer[float](symbol_ticks*sample_width,0)
        self._gap=0 #gap
        self._nor=0 #ストリームから読みだしたTick数
        self._pmax:float
        self._co_step=0
        self._cycle=cycle
        self._threshold=threshold

    class DetectedPreamble(int):
        def __new__(cls,v:int):
            r=super().__new__(cls,v)
            return r

    def __next__(self)->DetectedPreamble:
        # print("wait",self._co_step)
        #ローカル変数の生成
        cof=self._cof
        ave1=self._average1
        tickbuf=self._tickbuf
        try:
            while True:
                # ギャップ探索
                if self._co_step==0:
                    self._gap=0
                    self._co_step=1
                #ASync #1
                if self._co_step==1:
                    while True:
                        try:
                            a=next(cof)
                            ave1.append(a)
                            tickbuf.append(a)
                        except RecoverableStopIteration as e:
                            raise #nextやりなおし
                        # print(rb.tail)
                        self._nor=self._nor+1
                        self._gap=ave1.top-ave1.tail
                        if self._gap<0.5:
                            continue
                        if ave1.top<0.1:
                            continue
                        if ave1.tail>-0.1:
                            continue
                        break
                    print(ave1.tail,ave1.top) #-0.25432290820230913 0.27101677789788603
                    self._co_step=2 #Co進行
                if self._co_step==2:
                    # print(1,self._nor,rb.tail,rb.top,self._gap)
                    # ギャップ最大化
                    while True:
                        try:
                            a=next(cof)
                            ave1.append(a)
                            tickbuf.append(a)
                        except RecoverableStopIteration as e:
                            raise #nextやりなおし
                        self._nor=self._nor+1
                        w=ave1.top-ave1.tail
                        if w>=self._gap:
                            # print(w,self._gap)
                            self._gap=w
                            continue
                        break
                    if self._gap<self._threshold:
                        self._co_step=0 #コルーチンをリセット
                        continue
                    # print(2,nor,self._gap)
                    self._pmax=ave1.tail
                    print(ave1.tail,ave1.top) #-1.0 0.9995798842588445

                    self._co_step=3
                if self._co_step==3:
                    #同期シンボルピーク検出
                    while True:
                        try:
                            a=next(cof)
                            ave1.append(a)
                            tickbuf.append(a)
                            n=ave1.tail
                            self._nor=self._nor+1
                            if n>self._pmax:
                                self._pmax=n
                                continue
                            if self._pmax>0.1:
                                break
                        except RecoverableStopIteration as e:
                            raise #nextやりなおし
                    self._co_step=4 #END
                    symbol_ticks=self._symbol_ticks
                    sample_width=self._sample_width
                    cofbuf_len=self._cofbuf_len
                    cycle=self._cycle

                    # print(4,self._nor,rb.tail,rb.top,self._gap)
                    # print(3,self._nor)
                    # #ピーク周辺の読出し
                    # [next(cof) for _ in range(symbol_ticks//4)]
                    #バッファリングしておいた相関値に3値平均フィルタ
                    iom=tickbuf.indexOfSum3Max(symbol_ticks)



                    #ピークを基準に詳しく様子を見る。
                    peak_pos2=iom[0]+self._nor-symbol_ticks-1
                    # assert(peak_pos==peak_pos2)
                    #print("peak_pos2",peak_pos2)# 2:1299
                    # print(peak_pos-symbol_ticks*3,(self._nor-(peak_pos+symbol_ticks*3)))
                    #Lレベルシンボルの範囲を得る
                    # s=peak_pos-symbol_ticks*3-(self._nor-cofbuf_len)
                    s=peak_pos2-symbol_ticks*sample_width-(self._nor-cofbuf_len)
                    #lw=lw[:len(lw)*3//2+1]#効いてないので一時的にコメントアウト
                    # lw=list(tickbuf.subIter(s,cycle*symbol_ticks))
                    # print("lw",sum(lw)/len(lw),tickbuf.ave(s,cycle*symbol_ticks))#2:-399.6595476442715
                    # lw.sort()
                    # print("lw",sum(lw))#2:-399.6595476442715
                    # print("lw",lw[0],tickbuf.min(s,cycle*symbol_ticks))#2:-399.6595476442715
                    # if sum(lw)/len(lw)>lw[0]*0.66:
                    #     # print("ERR(L",peak_pos+src.pos,sum(lw)/len(lw),min(lw))
                    #     self._co_step=0#co_step0からやり直す。
                    #     continue #バラツキ大きい
                    if tickbuf.ave(s,cycle*symbol_ticks)>tickbuf.min(s,cycle*symbol_ticks)*0.66:
                        self._co_step=0#co_step0からやり直す。
                        continue #バラツキ大きい

                    #Hレベルシンボルの範囲を得る
                    # s=peak_pos-symbol_ticks*6-(self._nor-cofbuf_len)
                    s=peak_pos2-symbol_ticks*sample_width*2-(self._nor-cofbuf_len)
                    #lh=lh[:len(lh)*3//2+1] 効いてないので一時的にコメントアウト
                    # lh=list(tickbuf.subIter(s,cycle*symbol_ticks))
                    # print("lh",sum(lh)/len(lh),tickbuf.ave(s,cycle*symbol_ticks))#2:-399.6595476442715
                    # lh.sort(reverse=True)
                    # print("lh",sum(lh)) #2:399.63887917843374
                    # print("lh",lh[0],tickbuf.max(s,cycle*symbol_ticks))#2:-399.6595476442715
                    # if sum(lh)/len(lh)<lh[0]*0.66:
                    #     # print("ERR(H",peak_pos+src.pos,sum(lh)/len(lh),max(lh))
                    #     self._co_step=0 #co_step0からやり直す。
                    #     continue #バラツキ大きい
                    if tickbuf.ave(s,cycle*symbol_ticks)<tickbuf.max(s,cycle*symbol_ticks)*0.66:
                        self._co_step=0 #co_step0からやり直す。
                        continue #バラツキ大きい

                    #値の高いのを抽出してピークとする。
                    print(peak_pos2-self._nor)#-54,2=-55
                    return self.DetectedPreamble(peak_pos2-self._nor)#現在値からの相対位置
                raise RuntimeError("Invalid co_step",self._co_step)
        except StopIteration as e:
            raise e
            # print("END")
        except:
            self._co_step=4 #END
            raise
    

