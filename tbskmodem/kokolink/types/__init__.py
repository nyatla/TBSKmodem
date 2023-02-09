""" pythonの標準クラス名の解決

"""
from typing import Generic, Tuple,List,Iterable, Iterator,Generator,Sequence,Deque,BinaryIO,Dict, TypeVar,Union

try:
    from types import  NoneType    
except ImportError:
    NoneType=type(None)

import sys
pyver=((sys.version_info[0]*1000)+sys.version_info[1])*1000+sys.version_info[2]
# print("ver",pyver)

if pyver>=(((3*1000)+9)*1000)+1: #3.9.1未満だとキューのジェネリックができないらしい
    from queue import Queue as Queue
else:
    from queue import Queue as _Queue
    T=TypeVar("T")
    class Queue(_Queue,Generic[T]):
        ...
from queue import Empty
