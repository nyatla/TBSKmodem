




from ....utils import RingBuffer
from ....utils.math.corrcoef import ISelfCorrcoefIterator
from ....streams import RoStream,BitStream
from ....interfaces import IRoStream
from ..traitblockcoder import TraitBlockEncoder
from .Preamble import Preamble
from ....types import Sequence



class PointyPreamble(Preamble):
    """ 相関値が尖形の信号を待ちます。
        相関時系列値から尖形を検出し、そのピーク値を同期ポイントとします。
        tone長のシンボルを一単位として、-1,1,1,-1の4シンボルで判定します。
    """
    def __init__(self,tone:Sequence[float],threshold:float=0.5):
        self._threshold=threshold
        self._symbol=tone
    def getPreamble(self)->IRoStream[float]:
        enc=TraitBlockEncoder(self._symbol)
        return enc.setInput(BitStream([0,1,1,0],1))

    class waitForSymbolResultAsInt(int):
        def __new__(cls,v:int):
            r=super().__new__(cls,v)
            return r

    def waitForSymbol(self,src:RoStream[float])->waitForSymbolResultAsInt:
        """ 尖形のピーク座標を返します。座標は[0:-1],[1:1],[2:1],[3:-1]の[2:1]の末尾に同期します。
            値はマイナスの事もあります。
        """
        symbol_ticks=len(self._symbol)
        ave_window=(symbol_ticks//10)+3
        cof=ISelfCorrcoefIterator.createNormalized(symbol_ticks,src,symbol_ticks)
        nor=0
        rb=RingBuffer(symbol_ticks*2,0)
        th=self._threshold
        while True:
            rb.append(next(cof))
            nor=nor+1
            #中央要素の平均を取る
            mave=sum(rb.sublist(-ave_window,-ave_window))/ave_window
            #末尾要素の平均を取る
            lave=sum(rb.sublist(-ave_window-symbol_ticks,-ave_window))/ave_window

            #立ち上がり確認

            #正の相関確認
            if mave<th or lave>-th:
                continue
            #比率の確認
            if mave+lave>.1:
                continue
        
            #先頭要素の平均を取る
            rave=sum(rb.sublist(-1,-ave_window))/ave_window

            if rave>mave:
                continue
            print("pass")
            #探索範囲の先頭
            buf=rb[-ave_window*3:]
            # print(buf)

            l=len(buf)
            b=[(c,i) for c,i in enumerate(buf)]            
            b.sort(key=lambda x: x[1],reverse=True)
            #閾値
            if b[0][1]<self._threshold:
                continue
            #値の高いのを抽出してピークとする。
            peak_pos=b[0][0]+nor-l #位置
            # print(peak_pos)
            return self.waitForSymbolResultAsInt(
                peak_pos-nor #現在値からの相対位置
            )

