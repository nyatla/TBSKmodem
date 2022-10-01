
from typing import List, Union,Tuple,Dict, overload
from abc import ABC,abstractmethod






import json



class Serialized:
    """ 直列化した情報を保持するクラスです。

        objメンバ変数のSerializeableな階層化オブジェクトをラップします。
        データの書き出しと読み込み機能を提供します。
    """
    @staticmethod
    def _dumper(item):
        if isinstance(item,Serialized):
            return item.data
        if isinstance(item,ISerializable):
            return item.serialize().data
        # if isinstance(item,numpy.complexfloating):
        #     return complex(item.real,item.imag)
        return item
    SERIALIZEABLE_DATA=Union[int,float,str,bytes,Tuple["SERIALIZEABLE_DATA"],List["SERIALIZEABLE_DATA"],Dict[Union[str,bytes,int],"SERIALIZEABLE_DATA"]]
    SERIALIZEABLE_OBJECT=Union[Tuple[SERIALIZEABLE_DATA],List[SERIALIZEABLE_DATA],Dict[Union[str,bytes,int],SERIALIZEABLE_DATA]]
    def __init__(self,data:SERIALIZEABLE_OBJECT):
        self._data:Serialized.SERIALIZEABLE_OBJECT=data
    def __getitem__(self,key):
        r=self._data[key]
        if isinstance(r,tuple) or isinstance(r,dict) or isinstance(r,list):
            return Serialized(r) 
        else:
            return r
    def __setitem__(self,key,data):
        self._data[key]=data
        # if isinstance(r,tuple) or isinstance(r,dict) or isinstance(r,list):
        #     return Serialized(r) 
        # else:
        #     return r
    def __contains__(self,v:str)->bool:
        return v in self._data
    @property
    def data(self)->"Serialized.SERIALIZEABLE_OBJECT":
        """ラップせずに内部オブジェクトを返します。
        """
        return self._data

    def __str__(self)->str:
        return str(self._data)        
    @classmethod
    def loads(cls,s:Union[str,bytes]):
        return Serialized(json.loads(s))
    @classmethod
    def load(cls,fp):
        return Serialized(json.load(fp))
    @overload
    @classmethod
    def dumps(cls,src:Union["Serialized","ISerializable"],indent:int=None,*args,**kws)->str:
        ...
    @overload
    @classmethod
    def dump(cls,src:Union["Serialized","ISerializable"],fp,indent:int=None,*args,**kws):
        ...

    @classmethod
    def dumps(cls,src:Union["Serialized","ISerializable"],*args,**kws)->str:
        """オプションパラメータはjson.dumpsと互換性があります。
        """
        if isinstance(src,ISerializable):
            return cls.dumps(src.serialize(),*args,**kws)
        else:
            return json.dumps(src,*args,default=cls._dumper,**kws)
    @classmethod
    def dump(cls,src:Union["Serialized","ISerializable"],fp,*args,**kws):
        """オプションパラメータはjson.dumpsと互換性があります。
        """
        if isinstance(src,ISerializable):
            return cls.dump(src.serialize(),fp,*args,**kws)
        else:       
            return json.dump(src,fp,*args,default=cls._dumper,**kws)


class ISerializable(ABC):
    """直列化した情報を出力できるインタフェイスです。イミュータブルクラスとして実装してください。
    このクラスを継承したクラスのコンストラクタは、同一クラスが出力したSerializedを受けとり、インスタンスを復元できるようにしてください。
    """
    @abstractmethod
    def serialize(self)->Serialized:
        ...


