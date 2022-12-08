from asyncio.constants import DEBUG_STACK_DEPTH
from itertools import chain
from typing import Callable, overload,Union,Generic,TypeVar


from ...types import NoneType, Iterable, Iterator,Generator,Tuple
from ...utils.recoverable import  RecoverableException, RecoverableStopIteration
from ...utils import AsyncMethod
from ...utils.functions import isinstances
from ...interfaces import IBitStream, IFilter,IRoStream,IRecoverableIterator
from ...filter import BitsWidthFilter,Bits2BytesFilter,Bits2StrFilter
from ...streams import ByteStream
from ...streams.rostreams import BasicRoStream
from ...streams import BitStream,RoStream


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
            


DSTTYPE=TypeVar("DSTTYPE")
class TbskDemodulator:
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
    
    def demodulateAsInt(self,src:Union[Iterator[float],Iterator[float]],bitwidth:int=8)->IRecoverableIterator[int]:
        """ TBSK信号からnビットのint値配列を復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
            RecoverExceptionが搬送するクラスは、AsyncDemodulate[AsyncMethod[IRecoverableIterator[int]]です。
        """
        assert(self._asmethod_lock==False)
        asmethod=self.AsyncDemodulate[int](self,src,lambda s:BitsWidthFilter(input_bits=1,output_bits=bitwidth).setInput(s))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod_lock=True #解放はAsyncDemodulateXのcloseで
            raise RecoverableException(asmethod) 

    def demodulateAsBytes(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[bytes]:
        """ TBSK信号からnビットのint値配列を復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
            RecoverExceptionが搬送するクラスは、AsyncDemodulate[AsyncMethod[IRecoverableIterator[int]]です。
        """
        assert(self._asmethod_lock==False)
        asmethod=self.AsyncDemodulate[int](self,src,lambda s:Bits2BytesFilter(input_bits=1).setInput(s))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod_lock=True #解放はAsyncDemodulateXのcloseで
            raise RecoverableException(asmethod) 

    def demodulateAsStr(self,src:Union[Iterator[float],Iterator[float]],encoding:str="utf-8")->IRecoverableIterator[str]:
        """ TBSK信号からsize文字単位でstrを返します。
            途中でストリームが終端した場合、既に読みだしたビットは破棄されます。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
            RecoverExceptionが搬送するクラスは、AsyncDemodulate[AsyncMethod[IRecoverableIterator[str]]です。
        """
        assert(self._asmethod_lock==False)
        asmethod=self.AsyncDemodulate[str](self,src,lambda s:Bits2StrFilter(encoding=encoding).setInput(s))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod_lock=True #解放はAsyncDemodulateXのcloseで
            raise RecoverableException(asmethod) 
    def demodulateAsHexStr(self,src:Union[Iterator[float],Iterator[float]])->IRecoverableIterator[str]:
        """
            RecoverExceptionが搬送するクラスは、AsyncDemodulate[AsyncMethod[IRecoverableIterator[str]]です。
        """
        assert(self._asmethod_lock==False)
        asmethod=self.AsyncDemodulate[str](self,src,lambda s:Bits2HexStrFilter().setInput(s))
        if asmethod.run():
            return asmethod.result
        else:
            self._asmethod_lock=True #解放はAsyncDemodulateXのcloseで
            raise RecoverableException(asmethod) 

