from abc import ABC, abstractmethod, abstractproperty
from ....interfaces import IRoStream


class Preamble(ABC):
    @abstractproperty
    def ticks(self):
        ...    
    @abstractmethod
    def getPreamble(self)->IRoStream[float]:
        ...


