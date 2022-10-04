
from ..interfaces import IPeekableStream
from ..types import Sequence,List


class DebugInstance(List):
    def __init__(self,src:IPeekableStream):
        super().__init__()
        self._src=src
    def put(self,refpos,name,v):
        assert(self._src.pos is not None)
        self.append([self._src.pos+refpos,name,v])


_dbg:DebugInstance
def DEBUG_RESET(src:IPeekableStream):
    global _dbg
    _dbg=DebugInstance(src)
def DEBUG_LOG(name:str,p:int,v:Sequence[any]):
    if _dbg is not None:
        _dbg.put(p,name,v)

import json
def DEBUG_DUMP(fname:str)->DebugInstance:
    with open(fname,"w") as fp:
        for i in _dbg:
            json.dump(i,fp,ensure_ascii=False)
            fp.write("\n")
    return _dbg
