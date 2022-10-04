""" デバック用のイベントログを記録するクラスです。
"""
from typing import TypeVar,Generic

import json
from abc import ABC, abstractmethod

from ..types import Sequence,List
from ..utils.serializable import ISerializable, Serialized



T=TypeVar("T")
class BaseDeserializer(ABC,Generic[T]):
    """ SerializedからT型のオブジェクトを復元するクラスのベースクラスです。
    """
    def __init__(self,target:str):
        self._target=target
    @property
    def taeget(self)->str:
        return self._target
    @abstractmethod
    def deserialize(self,src:Serialized)->T:
        """ シリアライズされたsrcを復元します。
        """
        pass

class EventItem(ISerializable):
    """ イベント１回分のフラグメントを格納します。
        イベントは、[name:str,value:serialized]なデータです。
        nameはそのイベントリストの中で固有な文字列でなければなりません。
    """
    class Deserializer(BaseDeserializer["EventItem"]):
        def __init__(self):
            super().__init__("EventItem")
        def deserialize(self,src:Serialized)->"EventItem":
            return EventItem(src[0],src[1])
    deserializer=Deserializer()

    def __init__(self,name:str,v:Serialized):
        self._serialized=[name,v]
    def __str__(self):
        return str(self._serialized)
    @property
    def value(self):
        return self._serialized[1]
    @property
    def name(self):
        return self._serialized[0]
    def serialize(self)->Serialized:
        return self._serialized
    

default_map=[EventItem.deserializer]

class EventLog(List[EventItem]):
    _root=None
    @staticmethod
    def getRoot():
        
        if EventLog._root is None:
            EventLog._root=EventLog()
        return EventLog._root
    def __init__(self):
        super().__init__()

    @classmethod
    def load(cls,fp,eventset:Sequence[BaseDeserializer]):
        eventset=eventset if eventset is not None else default_map
        map={i.taeget:i for i in eventset}
        r=EventLog()
        
        for i in fp.readlines():
            j=json.loads(i)
            if j[0] in map:
                r.append(map[j[0]].deserialize(j))
            else:
                r.append(EventItem.deserializer.deserialize(j))
        return r
    def __str__(self):
        return "\n".join([str(i) for i in self])
    @classmethod
    def loadf(cls,fpath:str,eventset:Sequence[BaseDeserializer]=None):
        eventset=eventset if eventset is not None else default_map
        with open(fpath) as fp:
            return cls.load(fp,eventset)
    @classmethod
    def dump(cls,fp,v:"EventLog"):
        """ リストをファイルに出力します。
            ファイルはイベント毎に１行の要素を持つテキストファイルです。
        """        
        for i in v:
            fp.write(Serialized.dumps(i.serialize(),ensure_ascii=False)+"\n")
    @classmethod
    def dumpf(cls,path:str,v:"EventLog"):
        with open(path,"w") as fp:
            cls.dump(fp,v)
    @classmethod
    def dumps(cls,v:"EventLog"):
        """ リストをファイルに出力します。
            ファイルはイベント毎に１行の要素を持つテキストファイルです。
        """
        s=""  
        for i in v:
            s=s+(Serialized.dumps(i.serialize(),ensure_ascii=False)+"\n")
        return s
class Position(EventItem):
    """ ストリームの位置を記録します。
    """
    class Deserializer(BaseDeserializer["Position"]):
        def __init__(self):
            super().__init__("Position")
        def deserialize(self,src:Serialized)->"Position":
            return Position(src[1])
    deserializer=Deserializer()

    def __init__(self,pos:int):
        super().__init__(self.__class__.__name__,pos)
        pass
    @property
    def pos(self):
        return self.value[0]




# el=EventList()
# el.append(EventItem("test",1))
# # el.dumpf("./test.txt",el)
# a=el.loadf("./test.txt")
# print(a)





