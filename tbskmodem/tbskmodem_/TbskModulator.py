from typing import overload

from ..kokolink.types import Iterable,Iterator,Union
from ..kokolink.utils.math import XorShiftRand31
from ..kokolink.protocol.tbsk.tbskmodem import TbskModulator_impl
from ..kokolink.protocol.tbsk.toneblock import TraitTone
from ..kokolink.protocol.tbsk.preamble import Preamble
from ..kokolink.streams import RoStream,ByteStream
from ..kokolink.filter import BitsWidthFilter
from ..kokolink.utils.functions import isinstances
from ..kokolink.protocol.tbsk.preamble import CoffPreamble

class TbskModulator(TbskModulator_impl):
    @overload
    def __init__(self,tone:TraitTone):
        ...
    @overload
    def __init__(self,tone:TraitTone,preamble_cycle:int):
        ...
    @overload
    def __init__(self,tone:TraitTone,preamble:Preamble):
        ...
    def __init__(self,*args,**kwds):
        if isinstances(args,(TraitTone,)):
            super().__init__(args[0],CoffPreamble(args[0]))
        elif isinstances(args,(TraitTone,int)):
            super().__init__(args[0],CoffPreamble(args[0],CoffPreamble.DEFAULT_TH,args[1]))
        elif isinstances(args,(TraitTone,Preamble)):
            super().__init__(args[0],args[1])
        else:
            raise ValueError()
        tone=args[0]
        self._suffix=[tone[i]*0.5 if i%2==0 else -tone[i]*0.5 for i in range(len(tone))]

    def modulateAsHexStr(self,src:Union[str,bytes],stopsymbol:bool=True):
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
        return self.modulate(bytes.fromhex(sstr),stopsymbol=stopsymbol)
    @overload
    def modulateAsBit(self,src:Iterable[int],stopsymbol:bool=True)->Iterator[float]:
        ...
    @overload
    def modulateAsBit(self,src:Iterator[int],stopsymbol:bool=True)->Iterator[float]:
        ...
    def modulateAsBit(self,*args,**kwds)->Iterator[float]:

        #stopsymbolが明示的にfalseの時だけ無効。
        suffix=None if "stopsymbol" in kwds and kwds["stopsymbol"]==False else self._suffix

        if isinstances(args,(Iterator,),(kwds,{"stopsymbol":bool})):
            return super().modulateAsBit(RoStream[int](args[0]),suffix=suffix)
        elif isinstances(args,(Iterable,),(kwds,{"stopsymbol":bool})):
            return super().modulateAsBit(RoStream[int](args[0]),suffix=suffix)


    @overload
    def modulate(self,src:Iterable[int],bitwidth:int=8,stopsymbol:bool=True)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:Iterator[int],bitwidth:int=8,stopsymbol:bool=True)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:bytes,stopsymbol:bool=True)->Iterator[float]:
        ...
    @overload
    def modulate(self,src:str,encoding="utf-8",stopsymbol:bool=True)->Iterator[float]:
        ...
    def modulate(self,*args,**kwds)->Iterator[float]:
        suffix=None if "stopsymbol" in kwds and kwds["stopsymbol"]==False else self._suffix

        if isinstances(args,(Iterator,),(kwds,{"bitwidth":int,"stopsymbol":bool})):
            bitwidth=8 if "bitwidth" not in kwds else kwds["bitwidth"]
            return super().modulateAsBit(BitsWidthFilter(bitwidth).setInput(RoStream[int](args[0])),suffix=suffix)
        elif isinstances(args,(bytes,),(kwds,{"stopsymbol":bool})):
            return super().modulateAsBit(BitsWidthFilter(8).setInput(ByteStream(args[0])),suffix=suffix)
        elif isinstances(args,(str,),(kwds,{"encoding":str,"stopsymbol":bool})):
            encoding="utf-8" if "encoding" not in kwds else kwds["encoding"]
            return super().modulateAsBit(BitsWidthFilter(8).setInput(ByteStream(args[0],encoding=encoding)),suffix=suffix)
        elif isinstances(args,(Iterable,),(kwds,{"bitwidth":int,"stopsymbol":bool})):
            bitwidth=8 if "bitwidth" not in kwds else kwds["bitwidth"]
            return super().modulateAsBit(BitsWidthFilter(bitwidth).setInput(RoStream[int](args[0])),suffix=suffix)
        else:
            raise ValueError()