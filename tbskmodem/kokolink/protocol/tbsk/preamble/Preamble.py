from abc import ABC, abstractmethod
from ....interfaces import IRoStream


class Preamble(ABC):
    @abstractmethod
    def getPreamble(self)->IRoStream[float]:
        ...
    @abstractmethod
    def waitForSymbol(self,src:IRoStream[float])->int:
        ...