from ..kokolink.protocol.tbsk.toneblock import SinTone,XPskSinTone,PnTone,TraitTone,MSeqTone
from ..kokolink.utils.math import MSequence
from ..kokolink.utils.functions import isinstances
from typing import overload,Sequence

class TbskTone:
    @classmethod
    @overload
    def createSin(cls)->SinTone:
        ...
    @classmethod
    @overload
    def createSin(cls,points:int)->SinTone:
        ...
    @classmethod
    @overload
    def createSin(cls,points:int,cycle:int)->SinTone:
        ...
    @classmethod
    def createSin(cls,*args,**kwds):
        if len(args)==0:
            return SinTone(10, 10)
        elif isinstances(args,(int,)):
            return SinTone(args[0],1)
        elif isinstances(args,(int,int)):
            return SinTone(args[0],args[1])
        else:
            raise TypeError()

    @classmethod
    @overload
    def createXPskSin(cls)->XPskSinTone:
        ...
    @classmethod
    @overload
    def createXPskSin(cls,points:int)->XPskSinTone:
        ...
    @classmethod
    @overload
    def createXPskSin(cls,points:int,cycle:int)->XPskSinTone:
        ...
    @classmethod
    def createXPskSin(cls,*args,**kwds):
        if len(args)==0:
            return XPskSinTone(10, 10)
        elif isinstances(args,(int,)):
            return XPskSinTone(args[0],1)
        elif isinstances(args,(int,int)):
            return XPskSinTone(args[0],args[1])
        else:
            raise TypeError()

    @classmethod
    @overload
    def createPn(cls,seed:int,interval:int,base_tone:TraitTone)->PnTone:
        ...
    @classmethod
    @overload
    def createPn(cls,seed:int,interval:int)->PnTone:
        ...
    @classmethod
    @overload
    def createPn(cls,seed:int)->PnTone:
        ...
    @classmethod
    def createPn(cls,*args,**kwds)->PnTone:
        if isinstances(args,(int,)):
            return PnTone(args[0],2,None)
        elif isinstances(args,(int,int)):
            return PnTone(args[0],args[1],None)
        elif isinstances(args,(int,int,TraitTone)):
            return PnTone(args[0],args[1],args[2])
        else:
            raise TypeError()


    @classmethod
    @overload
    def createMSeq(cls,mseq:MSequence)->MSeqTone:
        ...
    @classmethod
    @overload
    def createMSeq(cls,bits:int,tap:int)->MSeqTone:
        ...
    @classmethod
    @overload
    def createMSeq(cls,bits:int,tap:int,TraitTone)->MSeqTone:
        ...
    @classmethod
    def createMSeq(cls,*args,**kwds)->MSeqTone:
        if isinstances(args,(MSequence,)):
            return MSeqTone(args[0],None)
        elif isinstances(args,(int,int)):
            return MSeqTone(MSequence(args[0],args[1]),None)
        elif isinstances(args,(int,int,TraitTone)):
            return MSeqTone(MSequence(args[0],args[1]),args[2])
        else:
            raise TypeError()
    @classmethod
    @overload
    def createCustom(cls,d:Sequence[float])->TraitTone:
        ...
    @classmethod
    def createCustom(cls,*args,**kwds)->TraitTone:
        if isinstances(args,(Sequence,)):
            return TraitTone(args[0])
        else:
            raise TypeError()
