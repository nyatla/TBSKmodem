from itertools import chain
from typing import Callable, Union,Generic,TypeVar


from ...types import Iterable, Iterator
from ...utils.recoverable import  RecoverableException, RecoverableStopIteration
from ...utils import AsyncMethod
from ...interfaces import IBitStream, IRoStream,IRecoverableIterator
from ...streams.rostreams import BasicRoStream
from ...streams import BitStream,RoStream


from .toneblock import TraitTone
from .preamble import Preamble,CoffPreamble










from .traitblockcoder import TraitBlockEncoder,TraitBlockDecoder



class TbskModulator_impl:
    """ TBSKの変調クラスです。
        プリアンブルを前置した後にビットパターンを置きます。
    """
    class DiffBitEncoder(IBitStream,BasicRoStream[int]):
        """ ビット配列を差動ビットに変換します。
        """
        def __init__(self,firstbit:int,src:IRoStream[int]):
            super().__init__()
            self._last_bit=firstbit
            self._src=src
            self._is_eos=False
            self._pos=0
        def __next__(self)->int:
            if self._is_eos:
                raise StopIteration()
            if self._pos==0:
                self._pos=self._pos+1
                return self._last_bit #1st基準シンボル
            try:
                n=next(self._src)
            except StopIteration as e:
                self._is_eos=True
                raise StopIteration(e)

            if n==1:
                pass
            else:
                self._last_bit=(self._last_bit+1)%2
            self._pos=self._pos+1
            return self._last_bit
        @property
        def pos(self)->int:
            return self._pos

    def __init__(self,tone:TraitTone,preamble:Preamble=None):
        """
        """
        self._tone=tone
        self._preamble=preamble if preamble is not None else CoffPreamble(self._tone)
        self._enc=TraitBlockEncoder(tone)
        
    def modulateAsBit(self,src:Union[Iterable[int],Iterator[int]],suffix:Iterable[float]=None,suffix_pad:bool=True)->Iterator[float]:
        """
        Args:

        suffix
        ペイロードシンボルに続く任意振幅値。
        suffix_pad
        解析機に必要なパディング
        """
        ave_window_shift=max(int(len(self._tone)*0.1),2)//2 #検出用の平均フィルタは0.1*len(tone)//2だけずれてる。ここを直したらTraitBlockDecoderも直せ
        if isinstance(src,Iterable):
            src=iter(src)
        ch=[
            self._preamble.getPreamble(),
            self._enc.setInput(self.DiffBitEncoder(0,BitStream(src,1))),
        ]
        if suffix is not None:
            ch.append(suffix)
        #demodulatorが平均値で補正してる関係で遅延分を足してる。
        if suffix_pad:
            ch.append([0]*ave_window_shift)
        return chain.from_iterable(ch)


            


DSTTYPE=TypeVar("DSTTYPE")
class TbskDemodulator_impl:
    class AsyncDemodulate(AsyncMethod[IRecoverableIterator[DSTTYPE]],Generic[DSTTYPE]):
        def __init__(self,parent:"TbskDemodulator",src:Union[IRoStream[float],Iterable[float],Iterator[float]],builder:Callable[[TraitBlockDecoder],IRecoverableIterator[DSTTYPE]]):
            super().__init__()
            self._tone_ticks=len(parent._tone)
            self._result:IRecoverableIterator[DSTTYPE]=None
            self._stream=src if isinstance(src,IRoStream) else RoStream(src)
            self._peak_offset:int=None
            self._parent=parent
            self._wsrex:AsyncMethod[IRecoverableIterator[DSTTYPE]]=None
            self._co_step=0
            self._builder:Callable[[TraitBlockDecoder],IRecoverableIterator[DSTTYPE]]=builder
            self._closed=False
        @property
        def result(self)->IRecoverableIterator[DSTTYPE]:
            assert(self._co_step>=4)
            return self._result            
        def close(self):
            if not self._closed:
                try:
                    if self._wsrex is not None:
                        self._wsrex.close()
                finally:
                    self._wsrex=None
                    self._parent._asmethod_lock=False
                    self._closed=True
        def run(self)->bool:
            assert(not self._closed)
            # print("run",self._co_step)
            if self._co_step==0:
                try:
                    self._peak_offset=self._parent._pa_detector.waitForSymbol(self._stream) #現在地から同期ポイントまでの相対位置
                    assert(self._wsrex is None)
                    self._co_step=2
                except RecoverableException as rexp:
                    self._wsrex=rexp.detach()
                    self._co_step=1
                    return False



            if self._co_step==1:
                if self._wsrex.run()== False:
                    return False
                else:
                    self._peak_offset = self._wsrex.result
                    self._wsrex = None
                    self._co_step = 2

            if self._co_step==2:
                if self._peak_offset is None:
                    self._result=None
                    self._co_step=4
                    self.close()
                    return True
                # print(self._peak_offset)
                self._co_step=3

            if self._co_step==3:
                try:
                    # print(">>",self._peak_offset+self._stream.pos)
                    self._stream.seek(self._tone_ticks+self._peak_offset) #同期シンボル末尾に移動
                    # print(">>",stream.pos)
                    tbd=TraitBlockDecoder(self._tone_ticks)
                    self._result=self._builder(tbd.setInput(self._stream))
                    self.close()
                    self._co_step=4
                    return True
                except RecoverableStopIteration as e:
                    return False
                except StopIteration as e:
                    self._result=None
                    self.close()
                    self._co_step=4
                    return True
            raise RuntimeError()



    def __init__(self,tone:TraitTone,preamble:Preamble=None):
        self._tone=tone
        self._pa_detector=preamble if preamble is not None else CoffPreamble(tone,threshold=1.0)
        self._asmethod_lock:bool=False

    def demodulateAsBit(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[int]:
        """ TBSK信号からビットを復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
            RecoverExceptionが搬送するクラスは、AsyncDemodulate[AsyncMethod[IRecoverableIterator[int]]です。
        """
        assert(self._asmethod_lock==False)
        asmethod=self.AsyncDemodulate[int](self,src,lambda s:s)
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod_lock=True #解放はAsyncDemodulateXのcloseで
            raise RecoverableException(asmethod) 

