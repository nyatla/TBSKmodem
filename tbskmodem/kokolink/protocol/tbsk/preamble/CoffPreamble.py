
from typing import TypeVar,Union

from tbskmodem.kokolink.protocol.tbsk.toneblock import TraitTone

from ....types import NoneType
from ....interfaces import IRoStream
from ....utils.recoverable import AsyncMethodRecoverException, RecoverableStopIteration
from ....utils import RingBuffer,BufferedIterator,AsyncMethod
from ....utils.math.corrcoef import SelfCorrcoefIterator
from ....streams import BitStream
from ..traitblockcoder import AverageInterator, TraitBlockEncoder
from .Preamble import Preamble



T=TypeVar("T")
class CoffPreamble(Preamble):
    """ 台形反転信号プリアンブルです。
    """
    def __init__(self,tone:TraitTone,threshold:float=1.0,cycle:int=4):
        self._threshold=threshold
        self._symbol=tone
        self._cycle=cycle #平坦部分のTick数
        self._recover_lock=0
        self._asmethtod:self.ASwaitForSymbol=None
    def getPreamble(self)->IRoStream[float]:
        enc=TraitBlockEncoder(self._symbol)
        b=[1]*self._cycle
        c=[i%2 for i in range(self._cycle)]
        d=[(1+c[-1])%2,(1+c[-1])%2,c[-1],]
        return enc.setInput(BitStream([0,1]+b+[1]+c+d,1))
        # return enc.setInput(BitStream([0,1]+[1,1]+[1]+[0,1]+[0,0,1],1))
        # return enc.setInput(BitStream([0,1,1,1,1,0,1,0,0,1],1))

    class waitForSymbolResultAsInt(int):
        def __new__(cls,v:int):
            r=super().__new__(cls,v)
            return r
    class ASwaitForSymbol(AsyncMethod[Union[waitForSymbolResultAsInt,NoneType]]):
        def __init__(self,parent:"CoffPreamble",src:IRoStream[float]):
            super().__init__()
            symbol_ticks=len(parent._symbol)
            #後で見直すから10シンボル位記録しておく。
            cofbuf_len=symbol_ticks*(6+parent._cycle*2)
            # cofbuf_len=symbol_ticks*10
            self._parent=parent
            self._cof=BufferedIterator[float](SelfCorrcoefIterator(symbol_ticks,src,symbol_ticks),cofbuf_len,0)
            self._avi=AverageInterator[float](self._cof,symbol_ticks)
            sample_width=parent._cycle+1
            # rb=RingBuffer(symbol_ticks*3,0)
            self._sample_width=sample_width
            self._cofbuf_len=cofbuf_len
            self._symbol_ticks=symbol_ticks
            self._rb=RingBuffer[float](symbol_ticks*sample_width,0)
            self._gap=0 #gap
            self._nor=0 #ストリームから読みだしたTick数
            self._pmax:float
            self._co_step=0
            self._result=None
        @property
        def result(self)->Union["CoffPreamble.waitForSymbolResultAsInt",NoneType]:
            assert(self._closed)
            return self._result           
        def close(self):
            self._parent._asmethtod=None
            super().close()
        def run(self)->bool:
            # print("wait",self._co_step)
            if self._closed:
                return True
            #ローカル変数の生成
            avi=self._avi
            cof=self._cof
            rb=self._rb
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
                                rb.append(next(avi))
                                # print(rb.tail)
                                self._nor=self._nor+1
                                self._gap=rb.top-rb.tail
                                if self._gap<0.5:
                                    continue
                                if rb.top<0.1:
                                    continue
                                if rb.tail>-0.1:
                                    continue
                                break
                            except RecoverableStopIteration as e:
                                return False
                        self._co_step=2 #Co進行
                    if self._co_step==2:
                        # print(1,self._nor,rb.tail,rb.top,self._gap)
                        # ギャップ最大化
                        while True:
                            try:
                                rb.append(next(avi))
                                self._nor=self._nor+1
                                w=rb.top-rb.tail
                                if w>=self._gap:
                                    # print(w,self._gap)
                                    self._gap=w
                                    continue
                                break
                            except RecoverableStopIteration as e:
                                return False
                        # print(2,nor,rb.tail,rb.top,self._gap)
                        # continue
                        if self._gap<self._parent._threshold:
                            self._co_step=0 #コルーチンをリセット
                            continue
                        # print(3,nor,rb.tail,rb.top,self._gap)
                        # print(2,nor,self._gap)
                        self._pmax=rb.tail
                        self._co_step=3
                    if self._co_step==3:
                        #同期シンボルピーク検出
                        while True:
                            try:
                                n=next(avi)
                                self._nor=self._nor+1
                                if n>self._pmax:
                                    self._pmax=n
                                    continue
                                if self._pmax>0.1:
                                    break
                            except RecoverableStopIteration as e:
                                return False
                        self._co_step=4
                        symbol_ticks=self._symbol_ticks
                        sample_width=self._sample_width
                        cofbuf_len=self._cofbuf_len
                        cycle=self._parent._cycle

                        # print(4,self._nor,rb.tail,rb.top,self._gap)
                        # print(3,self._nor)
                        # #ピーク周辺の読出し
                        # [next(cof) for _ in range(symbol_ticks//4)]
                        #バッファリングしておいた相関値に3値平均フィルタ
                        buf=cof.buf[-symbol_ticks:]
                        b=[(i+self._nor-symbol_ticks+1,buf[i]+buf[i+1]+buf[2]) for i in range(len(buf)-2)] #位置,相関値
                        b.sort(key=lambda x: x[1],reverse=True)
                        #ピークを基準に詳しく様子を見る。
                        peak_pos=b[0][0]
                        # print(peak_pos-symbol_ticks*3,(self._nor-(peak_pos+symbol_ticks*3)))
                        #Lレベルシンボルの範囲を得る
                        # s=peak_pos-symbol_ticks*3-(self._nor-cofbuf_len)
                        s=peak_pos-symbol_ticks*sample_width-(self._nor-cofbuf_len)
                        lw=cof.buf[s:s+cycle*symbol_ticks]
                        lw.sort()
                        lw=lw[:len(lw)*3//2+1]
                        if sum(lw)/len(lw)>lw[0]*0.66:
                            # print("ERR(L",peak_pos+src.pos,sum(lw)/len(lw),min(lw))
                            self._co_step=0#co_step0からやり直す。
                            continue #バラツキ大きい
                        #Hレベルシンボルの範囲を得る
                        # s=peak_pos-symbol_ticks*6-(self._nor-cofbuf_len)
                        s=peak_pos-symbol_ticks*sample_width*2-(self._nor-cofbuf_len)
                        lh=cof.buf[s:s+cycle*symbol_ticks]
                        lh.sort(reverse=True)
                        lh=lh[:len(lh)*3//2+1]
                        if sum(lh)/len(lh)<lh[0]*0.66:
                            # print("ERR(H",peak_pos+src.pos,sum(lh)/len(lh),max(lh))
                            self._co_step=0 #co_step0からやり直す。
                            continue #バラツキ大きい
                        #値の高いのを抽出してピークとする。
                        # print(peak_pos)
                        self._result=CoffPreamble.waitForSymbolResultAsInt(peak_pos-self._nor)#現在値からの相対位置
                        self.close()
                        return True
                    raise RuntimeError("Invalid co_step")
            except StopIteration as e:
                self.close()
                self._result=None
                return True
                # print("END")
            except:
                self.close()
                raise

    def waitForSymbol(self,src:IRoStream[float])->Union[waitForSymbolResultAsInt,NoneType]:
        """ 尖形のピーク座標を返します。座標は[0:-1],[1:1],[2:1],[3:-1]の[2:1]の末尾に同期します。
            値はマイナスの事もあります。
            @raise
                入力からRecoverableStopInterationを受信した場合、RecoverableExceptionを送出します。
                呼び出し元がこの関数を処理しない限り,次の関数を呼び出すことはできません。
                終端に到達した場合は、Noneを返します。
        """

        assert(self._asmethtod is None)
        asmethtod=self.ASwaitForSymbol(self,src)
        if asmethtod.run():
            return asmethtod.result
        else:
            #ロックする（解放はASwaitForSymbolのclose内で。）
            self._asmethtod=asmethtod
            raise AsyncMethodRecoverException(asmethtod)


