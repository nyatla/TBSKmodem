from itertools import chain
from typing import overload,Union


from ...types import NoneType, Iterable, Iterator,Generator,Tuple
from ...utils.recoverable import AsyncMethodRecoverException, RecoverableException, RecoverableStopIteration
from ...utils import AsyncMethod
from ...utils.functions import isinstances
from ...interfaces import IBitStream, IFilter,IRoStream,IRecoverableIterator
from ...filter import BitsWidthFilter,Bits2BytesFilter,Bits2StrFilter
from ...streams import ByteStream
from ...streams.rostreams import BasicRoStream
from ...streams import BitStream
from ...streams import RoStream


from .toneblock import TraitTone
from .preamble import Preamble,CoffPreamble



import struct
class Bits2HexStrFilter(IFilter[IRoStream[int],str],BasicRoStream[str]):
    """ nBit intイテレータから1バイト単位のhex stringを返すフィルタです。
    """
    def __init__(self,input_bits:int=1):
        self._src=BitsWidthFilter(input_bits=input_bits,output_bits=8)
    def __next__(self) -> str:
        while True:
            try:
                d=self._src.__next__()
            except RecoverableStopIteration:
                raise
            return bytes.hex(struct.pack("1B",d))
    def setInput(self,src:IRoStream[int])->"Bits2HexStrFilter":
        self._src.setInput(src)
        return self
    @property
    def pos(self)->int:
        return self._src.pos







from .traitblockcoder import TraitBlockEncoder,TraitBlockDecoder



class TbskModulator:
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
            Args:
                tone
                    特徴シンボルのパターンです。
        """
        self._tone=tone
        self._preamble=preamble if preamble is not None else CoffPreamble(self._tone)
        self._enc=TraitBlockEncoder(tone)
        
    def modulateAsBit(self,src:Union[Iterable[int],Iterator[int]])->Iterator[float]:
        ave_window_shift=max(int(len(self._tone)*0.1),2)//2 #検出用の平均フィルタは0.1*len(tone)//2だけずれてる。ここを直したらTraitBlockDecoderも直せ

        return chain(
            self._preamble.getPreamble(),
            self._enc.setInput(self.DiffBitEncoder(0,BitStream(src,1))),
            [0]*ave_window_shift    #demodulatorが平均値で補正してる関係で遅延分を足してる。
        )
    def modulateAsHexStr(self,src:Union[str,bytes]):
        """ hex stringを変調します。
            hex stringは(0x)?[0-9a-fA-F]{2}形式の文字列です。
            hex stringはbytesに変換されて送信されます。
        """
        sstr:str
        if isinstance(src,bytes):
            sstr=src.decode("utf-8")
        else:
            sstr=src
        if sstr[:2]=="0x":
            sstr=sstr[2:]
            # print(sstr)
        return self.modulate(bytes.fromhex(sstr))
    @overload
    def modulate(self,src:Iterable[int],bitwidth:int=8)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:Iterator[int],bitwidth:int=8)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:bytes)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:str,encoding="utf-8")->Iterator[float]:
        ...
    def modulate(self,*args,**kwds)->Iterator[float]:
        def __modulate_A(src:Iterator[int],bitwidth:int=8)->Iterator[float]:
            return self.modulateAsBit(BitsWidthFilter(bitwidth).setInput(RoStream[int](src)))
        def __modulate_B(src:Iterable[int],bitwidth:int=8)->Iterator[float]:
            return self.modulateAsBit(BitsWidthFilter(bitwidth).setInput(RoStream[int](src)))
        def __modulate_C(src:bytes)->Iterator[float]:
            return self.modulateAsBit(BitsWidthFilter(8).setInput(ByteStream(src)))
        def __modulate_D(src:str,encoding:str="utf-8")->Iterator[float]:
            return self.modulateAsBit(BitsWidthFilter(8).setInput(ByteStream(src,encoding=encoding)))
        if isinstances(args,(Iterator,),(kwds,{"bitwidth":int})):
            return __modulate_A(*args,**kwds)
        elif isinstances(args,(bytes,)):
            return __modulate_C(*args,**kwds)
        elif isinstances(args,(str,),(kwds,{"encoding":str})):
            return __modulate_D(*args,**kwds)
        elif isinstances(args,(Iterable,),(kwds,{"bitwidth":int})):
            return __modulate_B(*args,**kwds)
        else:
            raise TypeError()
            




class TbskDemodulator:
    class AsyncDemodulateX(AsyncMethod[IRoStream[any]]):
        def __init__(self,parent:"TbskDemodulator",src:Union[IRoStream[int],Iterable[int],Iterator[int]],filter:IFilter[IRoStream[int],any]):
            super().__init__()
            self._tone_ticks=len(parent._tone)
            self._result=None
            self._filter=filter
            self._stream=src if isinstance(src,IRoStream) else RoStream(src)
            self._peak_offset:int=None
            self._parent=parent
            self._wsrex:AsyncMethodRecoverException=None
            self._co_step=0
        def close(self):
            super().close()
            self._parent._asmethod=None
        def run(self)->bool:
            if self._closed:
                return True            
            if self._co_step==0:
                try:
                    self._peak_offset=self._parent._pa_detector.waitForSymbol(self._stream) #現在地から同期ポイントまでの相対位置
                    self._co_step=2
                except AsyncMethodRecoverException as rexp:
                    self._wsrex=rexp
                    self._co_step=1
                    return False
            if self._co_step==1:
                try:
                    self._peak_offset=self._wsrex.recover()
                    self._wsrex=None
                    self._co_step=2
                except AsyncMethodRecoverException as rexp:
                    self._wsrex=rexp
                    return False
            if self._co_step==2:
                if self._peak_offset is None:
                    self._result=None
                    self.close()
                    return True
                self._co_step=3
            if self._co_step==3:
                try:
                    # print(">>",peak_offset+stream.pos)
                    self._stream.seek(self._tone_ticks+self._peak_offset) #同期シンボル末尾に移動
                    # print(">>",stream.pos)
                    tbd=TraitBlockDecoder(self._tone_ticks)
                    if self._filter is None:
                        self._result=tbd.setInput(self._stream)
                    else:
                        self._result=self._filter.setInput(tbd.setInput(self._stream))
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
        @property
        def result(self)->IRoStream[any]:
            assert(self._closed)
            return self._result


    def __init__(self,tone:TraitTone,preamble:Preamble=None):
        self._tone=tone
        self._pa_detector=preamble if preamble is not None else CoffPreamble(tone,threshold=1.0)
        self._asmethod:self.AsyncDemodulateX=None



    def demodulateAsBit(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[int]:
        """ TBSK信号からビットを復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
        """
        assert(self._asmethod is None)
        asmethod=self.AsyncDemodulateX(self,src,None)
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod=asmethod #解放はAsyncDemodulateXのcloseで
            raise AsyncMethodRecoverException(asmethod) 

    def demodulateAsInt(self,src:Union[Iterator[float],Iterator[float]],bitwidth:int=8)->IRecoverableIterator[int]:
        """ TBSK信号からnビットのint値配列を復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
        """
        assert(self._asmethod is None)
        asmethod=self.AsyncDemodulateX(self,src,BitsWidthFilter(1,bitwidth))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod=asmethod #解放はAsyncDemodulateXのcloseで
            raise AsyncMethodRecoverException(asmethod) 

    def demodulateAsBytes(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[bytes]:
        """ TBSK信号からバイト単位でbytesを返します。
            途中でストリームが終端した場合、既に読みだしたビットは破棄されます。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。   
        """
        assert(self._asmethod is None)
        asmethod=self.AsyncDemodulateX(self,src,Bits2BytesFilter(input_bits=1))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod=asmethod #解放はAsyncDemodulateXのcloseで
            raise AsyncMethodRecoverException(asmethod) 

    def demodulateAsStr(self,src:Union[Iterator[float],Iterator[float]],encoding:str="utf-8")->IRecoverableIterator[str]:
        """ TBSK信号からsize文字単位でstrを返します。
            途中でストリームが終端した場合、既に読みだしたビットは破棄されます。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
        """
        assert(self._asmethod is None)
        asmethod=self.AsyncDemodulateX(self,src,Bits2StrFilter(input_bits=1,encoding=encoding))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod=asmethod #解放はAsyncDemodulateXのcloseで
            raise AsyncMethodRecoverException(asmethod) 


    def demodulateAsHexStr(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[str]:
        assert(self._asmethod is None)
        asmethod=self.AsyncDemodulateX(self,src,Bits2HexStrFilter())
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod=asmethod #解放はAsyncDemodulateXのcloseで
            raise AsyncMethodRecoverException(asmethod) 

