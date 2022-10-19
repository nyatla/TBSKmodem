
from typing import TypeVar,Union

from tbskmodem.kokolink.protocol.tbsk.toneblock import TraitTone

from ....types import NoneType,Generator, Tuple,Sequence
from ....interfaces import IRoStream
from ....utils.recoverable import GeneratorRecoverException, RecoverableStopIteration
from ....utils import RingBuffer,BufferedIterator
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


    def waitForSymbol(self,src:IRoStream[float])->Union[waitForSymbolResultAsInt,NoneType]:
        """ 尖形のピーク座標を返します。座標は[0:-1],[1:1],[2:1],[3:-1]の[2:1]の末尾に同期します。
            値はマイナスの事もあります。
            @raise
                入力からRecoverableStopInterationを受信した場合、RecoverableExceptionを送出します。
                呼び出し元がこの関数を処理しない限り,次の関数を呼び出すことはできません。
                終端に到達した場合は、Noneを返します。
        """
        def gen(src:IRoStream[float])->Tuple[Exception,Union[NoneType,self.waitForSymbolResultAsInt]]:
            self._recover_lock=self._recover_lock+1
            symbol_ticks=len(self._symbol)
            #後で見直すから10シンボル位記録しておく。
            cycle=self._cycle
            cofbuf_len=symbol_ticks*(6+cycle*2)
            # cofbuf_len=symbol_ticks*10
            cof=BufferedIterator[float](SelfCorrcoefIterator(symbol_ticks,src,symbol_ticks),cofbuf_len,0)
            avi=AverageInterator[float](cof,symbol_ticks)
            sample_width=cycle+1
            # rb=RingBuffer(symbol_ticks*3,0)
            rb=RingBuffer[float](symbol_ticks*sample_width,0)
            th=self._threshold
            nor=0 #ストリームから読みだしたTick数
            try:
                while True:
                    # ギャップ探索
                    gap:int=0
                    while True:
                        try:
                            n=next(avi)
                        except RecoverableStopIteration as e:
                            yield e,None
                            continue
                        rb.append(n)
                        # print(rb.tail)
                        nor=nor+1
                        gap=rb.top-rb.tail
                        if gap<0.5:
                            continue
                        if rb.top<0.1:
                            continue
                        if rb.tail>-0.1:
                            continue
                        break
                    # print(1,nor,rb.tail,rb.top,gap)
                    # ギャップ最大化
                    while True:
                        try:
                            n=next(avi)
                        except RecoverableStopIteration as e:
                            yield e,None
                            continue
                        rb.append(n)
                        nor=nor+1
                        w=rb.top-rb.tail
                        if w>=gap:
                            # print(w,gap)
                            gap=w
                            continue
                        break
                    # print(2,nor,rb.tail,rb.top,gap)
                    # continue
                    if gap<th:
                        continue
                    # print(3,nor,rb.tail,rb.top,gap)
                    # print(2,nor,gap)
                    #同期シンボルピーク検出
                    pmax=rb.tail
                    while True:
                        try:
                            n=next(avi)
                        except RecoverableStopIteration as e:
                            yield e,None
                            continue
                        nor=nor+1
                        if n>pmax:
                            pmax=n
                            continue
                        if pmax>0.1:
                            break
                    # print(4,nor,rb.tail,rb.top,gap)
                    # print(3,nor)
                    # #ピーク周辺の読出し
                    # [next(cof) for _ in range(symbol_ticks//4)]
                    #バッファリングしておいた相関値に3値平均フィルタ
                    buf=cof.buf[-symbol_ticks:]
                    b=[(i+nor-symbol_ticks+1,buf[i]+buf[i+1]+buf[2]) for i in range(len(buf)-2)] #位置,相関値
                    b.sort(key=lambda x: x[1],reverse=True)
                    #ピークを基準に詳しく様子を見る。
                    peak_pos=b[0][0]
                    # print(peak_pos-symbol_ticks*3,(nor-(peak_pos+symbol_ticks*3)))
                    #Lレベルシンボルの範囲を得る
                    # s=peak_pos-symbol_ticks*3-(nor-cofbuf_len)
                    s=peak_pos-symbol_ticks*sample_width-(nor-cofbuf_len)
                    lw=cof.buf[s:s+cycle*symbol_ticks]
                    lw.sort()
                    lw=lw[:len(lw)*3//2+1]
                    if sum(lw)/len(lw)>lw[0]*0.66:
                        # print("ERR(L",peak_pos+src.pos,sum(lw)/len(lw),min(lw))
                        continue #バラツキ大きい
                    #Hレベルシンボルの範囲を得る
                    # s=peak_pos-symbol_ticks*6-(nor-cofbuf_len)
                    s=peak_pos-symbol_ticks*sample_width*2-(nor-cofbuf_len)
                    lh=cof.buf[s:s+cycle*symbol_ticks]
                    lh.sort(reverse=True)
                    lh=lh[:len(lh)*3//2+1]
                    if sum(lh)/len(lh)<lh[0]*0.66:
                        # print("ERR(H",peak_pos+src.pos,sum(lh)/len(lh),max(lh))
                        continue #バラツキ大きい

                    #閾値
                    # if b[0][1]<self._threshold:
                    #     continue
                    #値の高いのを抽出してピークとする。
                    # print(peak_pos)
                    yield None,self.waitForSymbolResultAsInt(
                        peak_pos-nor #現在値からの相対位置
                    )
                    return
            except StopIteration as e:
                # print("END")
                yield None,None
            finally:
                self._recover_lock=self._recover_lock-1
                # print("Generator closed")
                pass
        assert(self._recover_lock==0)
        g:Generator=gen(src)
        e,r=next(g)
        if e is None:
            g.close()
            return r
        #エラー処理
        elif isinstance(e,RecoverableStopIteration):
            raise GeneratorRecoverException(g)
        else:
            g.close()
            raise RuntimeError(e)
