from typing import overload
from ..kokolink.protocol.tbsk.tbskmodem import TbskDemodulator_impl
from ..kokolink.types import Iterator,Union
from ..kokolink.protocol.tbsk.toneblock import TraitTone
from ..kokolink.protocol.tbsk.preamble import Preamble,CoffPreamble
from ..kokolink.streams.rostreams import BasicRoStream

from ..kokolink.filter import BitsWidthFilter,Bits2StrFilter,Bits2BytesFilter
from ..kokolink.utils.functions import isinstances
from ..kokolink.utils.recoverable import RecoverableException,RecoverableStopIteration
from ..kokolink.interfaces import IRecoverableIterator,IFilter,IRoStream


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


class TbskDemodulator(TbskDemodulator_impl):
    @overload
    def __init__(self,tone:TraitTone):
        ...
    @overload
    def __init__(self,tone:TraitTone,preamble_th:float=CoffPreamble.DEFAULT_TH,preamble_cycle:int=CoffPreamble.DEFAULT_CYCLE):
        ...
    @overload
    def __init__(self,tone:TraitTone,preamble:Preamble):
        ...
    def __init__(self,*args,**kwds):
        if isinstances(args,(TraitTone,)):
            super().__init__(args[0],CoffPreamble(args[0]))
        elif isinstances(args,(TraitTone,float,int)):
            super().__init__(args[0],CoffPreamble(args[0],args[1],args[2]))
        elif isinstances(args,(TraitTone,Preamble)):
            super().__init__(args[0],args[1])
        else:
            raise ValueError()

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

