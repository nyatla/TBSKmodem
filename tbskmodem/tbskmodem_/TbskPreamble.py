from ..kokolink.protocol.tbsk.toneblock import TraitTone
from ..kokolink.protocol.tbsk.preamble import Preamble,CoffPreamble
from ..kokolink.utils.functions import isinstances
from typing import overload

class TbskPreamble:
    @classmethod
    @overload
    def createCoff(cls,tone:TraitTone)->Preamble:
        ...
    @classmethod
    @overload
    def createCoff(cls,tone:TraitTone,threshold:float,cycle:int):
        ...
    @classmethod
    def createCoff(cls,*args,**kwds):
        if isinstances(args,(TraitTone,)):
            return cls.createCoff(args[0],CoffPreamble.DEFAULT_TH, CoffPreamble.DEFAULT_CYCLE)
        elif isinstances(args,(TraitTone,float,int)):
           return CoffPreamble(args[0],args[1],args[2])
        else:
            raise TypeError()
