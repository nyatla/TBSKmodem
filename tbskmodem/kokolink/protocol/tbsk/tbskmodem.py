from itertools import chain
from typing import overload,Union

from ...types import NoneType, Iterable, Iterator,Generator
from ...utils.recoverable import GeneratorRecoverException, RecoverableException, RecoverableStopIteration,RecoverableIterator
from ...utils.functions import isinstances
from ...interfaces import IBitStream, IFilter,IRoStream
from ...filter import BitsWidthFilter,Bits2BytesFilter,Bits2StrFilter
from ...streams import ByteStream
from ...streams.rostreams import BasicRoStream
from ...streams import BitStream
from ...streams import RoStream


from .toneblock import TraitTone
from .preamble import Preamble,CoffPreamble



import struct
class Bits2HexStrFilter(BitsWidthFilter):
    """ nBit intイテレータから1バイト単位のhex stringを返すフィルタです。
    """
    def __init__(self,input_bits:int=1):
        super().__init__(input_bits=input_bits,output_bits=8)
    def __next__(self) -> str:
        while True:
            try:
                d=super().__next__()
            except RecoverableStopIteration:
                raise
            return bytes.hex(struct.pack("1B",d))





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
            print(sstr)
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
    def __init__(self,tone:TraitTone,preamble:Preamble=None):
        self._tone=tone
        self._pa_detector=preamble if preamble is not None else CoffPreamble(tone,threshold=1.0)
        self._recover_lock=0
    def _common_gen(self,src:Union[IRoStream[int],Iterable[int],Iterator[int]],filter:IFilter[IRoStream[int],any])->Generator[TraitBlockDecoder,NoneType,NoneType]:
        assert(self._recover_lock==0)        
        tone_ticks=len(self._tone)
        stream=src if isinstance(src,IRoStream) else RoStream(src)
        peak_offset=None
        self._recover_lock=self._recover_lock+1
        try:
            try:
                peak_offset=self._pa_detector.waitForSymbol(stream) #現在地から同期ポイントまでの相対位置
            except RecoverableException as rexp:
                yield RecoverableStopIteration(),None
                while True:
                    try:
                        peak_offset=rexp.recover()
                        break #成功
                    except RecoverableException as e:
                        rexp=e
                        yield RecoverableStopIteration(),None
                        continue
                    except:
                        rexp.close()
                        import traceback
                        traceback.print_exception(e)
                        raise
            except StopIteration as e:
                yield e,None
            while True:
                try:
                    # print(">>",peak_offset+stream.pos)
                    stream.seek(tone_ticks+peak_offset) #同期シンボル末尾に移動
                    # print(">>",stream.pos)
                    break
                except RecoverableStopIteration as e:
                    yield e,None
                    continue
            tbd=TraitBlockDecoder(tone_ticks)
            if filter is None:
                yield None,tbd.setInput(stream)
            else:
                yield None,filter.setInput(tbd.setInput(stream))
        finally:
            self._recover_lock=self._recover_lock-1

    def demodulateAsBit(self,src:Union[Iterator[float],Iterator[float]])->TraitBlockDecoder:
        """ TBSK信号からビットを復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はNoneを返します。
        """
        g:Generator=self._common_gen(src,None)
        e,r=next(g)
        if e is None:
            g.close()
            return r
        raise GeneratorRecoverException(e,g)

    def demodulateAsInt(self,src:Union[Iterator[float],Iterator[float]],bitwidth:int=8)->RecoverableIterator[int]:
        """ TBSK信号からnビットのint値配列を復元します。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はStopInterationをraiseします。
        """
        g:Generator=self._common_gen(src,BitsWidthFilter(1,bitwidth))
        e,r=next(g)
        if e is None:
            g.close()
            return r
        raise GeneratorRecoverException(e,g)

    


    def demodulateAsBytes(self,src:Union[Iterator[float],Iterator[float]])->RecoverableIterator[bytes]:
        """ TBSK信号からバイト単位でbytesを返します。
            途中でストリームが終端した場合、既に読みだしたビットは破棄されます。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はStopInterationをraiseします。         
        """
        g:Generator=self._common_gen(src,Bits2BytesFilter())
        e,r=next(g)
        if e is None:
            g.close()
            return r
        raise GeneratorRecoverException(e,g)


    def demodulateAsStr(self,src:Union[Iterator[float],Iterator[float]],encoding:str="utf-8")->RecoverableIterator[str]:
        """ TBSK信号からsize文字単位でstrを返します。
            途中でストリームが終端した場合、既に読みだしたビットは破棄されます。
            関数は信号を検知する迄制御を返しません。信号を検知せずにストリームが終了した場合はStopInterationをraiseします。
        """
        g:Generator=self._common_gen(src,Bits2StrFilter(encoding=encoding))        
        e,r=next(g)
        if e is None:
            g.close()
            return r
        raise GeneratorRecoverException(e,g)        

    def demodulateAsHexStr(self,src:Union[Iterator[float],Iterator[float]])->RecoverableIterator[str]:
        g:Generator=self._common_gen(src,Bits2HexStrFilter())        
        e,r=next(g)
        if e is None:
            g.close()
            return r
        raise GeneratorRecoverException(e,g)        
