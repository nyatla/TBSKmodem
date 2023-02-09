from itertools import chain
from typing import overload

from ..kokolink.types import Iterable,Iterator,Union
from ..kokolink.protocol.tbsk.tbskmodem import TbskModulator_impl
from ..kokolink.protocol.tbsk.toneblock import TraitTone
from ..kokolink.protocol.tbsk.preamble import Preamble
from ..kokolink.streams import BitStream,RoStream,ByteStream
from ..kokolink.filter import BitsWidthFilter
from ..kokolink.utils.functions import isinstances

class TbskModulator(TbskModulator_impl):
    def __init__(self,tone:TraitTone,preamble:Preamble=None):
        """
            Args:
                tone
                    特徴シンボルのパターンです。
        """
        super().__init__(tone,preamble)
        
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