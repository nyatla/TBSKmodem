
from typing import Type,NewType,Union
import binascii

from ..types import Sequence,Tuple,Dict,List
"""isinstancesがintかfloatでtrueを返す特別な型です。
"""
Number=NewType('Number', int)

def isinstances(args:any,types:Union[List[Type],Tuple[Type],Type],optional:Tuple[any,Dict[str,Type]]=None):
    """argsに対して一括で型チェックします.
    この関数は低速です。頻繁に呼び出される場所に使うべきではありません。
    optionalがある場合はキーワード引数の存在と、あれば型の一致判定を行います。
    isinstances(args,[int,int])
    isinstances(args,[int,int],(kwds,{"a":int,"b":str}))
    isinstances(args,[int,[int,NoneType]],(kwds,{"a":int,"b":[str,int]}))
    """
    if isinstance(types,List) or isinstance(types,Tuple):
        pass
    else:
        types=[types]

    ltypes=len(types)
    largs=len(args)

    if optional is None:
        #optionalが無くて引数の数が違うならエラー
        if largs!=ltypes:
            return False
    else:
        #無名オプション引数のための再配置。
        if largs>ltypes:
            #typesの方が少ない場合はキーワード引数に編入する。この処理はおぱいそん3.7移行でないと死ぬ。
            odict=optional[0].copy()
            okwds=[i for i in optional[1].keys()]
            for k,v in zip(okwds,args[ltypes:]):
                if k in odict:
                    return False
                if v is not None:
                    odict[k]=v
            optional=(odict,optional[1])
            args=args[:ltypes]

    ltypes=len(types)
    largs=len(args)
    if largs!=ltypes:
        #再配置後の必須引数チェック
        return False


    for i,j in zip(args,types):
        #Numberの場合はFloat/IntのどちらかでOK
        if j==Number:
            if isinstance(i,int) or isinstance(i,float):
                continue
            else:
                return False
        elif isinstance(j,Sequence):
            if True not in [isinstance(i,k) for k in j]:
                return False
        elif not isinstance(i,j):
            return False

    if optional is None:
        #optionalがなければここまで
        return True
    
    #optionalの判定
    for k in optional[0]:
        if k not in optional[1]:
            #知らない引数があれば対象外
            return False
        if isinstance(optional[1][k],Sequence):
            if True not in [isinstance(optional[0][k],l) for l in optional[1][k]]:
                return False
        elif not isinstance(optional[0][k],optional[1][k]):
            return False
    return True


def escapeBytes(s:Union[bytes,Sequence,Dict]):
    """ bytes,又はSequence,Dictを文字列形式にエスケープします。
        オブジェクトの要素にstrが存在しないようにしてください。
    """
    if isinstance(s,bytes):
        return str(binascii.hexlify(s), 'utf-8')
    elif isinstance(s,Sequence):
        return [escapeBytes(i) for i in s]
    elif isinstance(s,Dict):
        return {i:escapeBytes(s[i]) for i in s}
    elif isinstance(s,int) or isinstance(s,float):
        return s
    else:
        return TypeError()
def unescapeBytes(s:Union[str,Sequence,Dict]):
    """ escapeBytesで生成したstr,又はSequence,Dictをbytesに戻します。
        オブジェクトの要素にbytesが存在しないようにしてください。
    """
    if isinstance(s,str):
        return binascii.unhexlify(s)
    elif isinstance(s,Sequence):
        return [unescapeBytes(i) for i in s]
    elif isinstance(s,Dict):
        return {i:unescapeBytes(s[i]) for i in s}
    elif isinstance(s,int) or isinstance(s,float):
        return s
    else:
        return TypeError()



if __name__ == '__main__':
    print(isinstances([1,1.0,"str",[]],[int,float,str,Sequence],({"a":1,"b":"str","c":1},{"a":int,"b":str,})))#option多すぎ FALSE
    print(isinstances([1,1.0,"str",[]],[int,float,str,Sequence],({"a":1,"b":"str"},{"a":int,"b":str,})))#丁度 TRUE
    print(isinstances([1,1.0,"str",[]],[int,float,str,Sequence],({"a":1},{"a":int,"b":str,})))#足りない TRUE 
    print(isinstances([1,1.0,"str",[]],[int,float,str,Sequence],({"a":1},{"a":str,"b":str,})))#型が違う FALSE
    print(isinstances([1],int))#TRUE
    print(isinstances([1],str))#FALSE
    print(isinstances([1,1.0,"str2",[]],[int,float],({},{"a":str})))#型が違う FALSE
    