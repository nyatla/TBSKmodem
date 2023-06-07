""" PreambleのwaitAForSymbolのアップデート実験用。
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tbskmodem.kokolink.utils.recoverable import RecoverableStopIteration




from tbskmodem.tbskmodem_ import TbskModulator
from tbskmodem.tbskmodem_ import XPskSinTone,CoffPreamble
from tbskmodem.tbskmodem_ import TbskDemodulator_impl
from tbskmodem.kokolink.interfaces import IRecoverableIterator
from tbskmodem.kokolink.utils.recoverable import SkipRecoverIteraor,RecoverableException





class NoneSplitIterator(IRecoverableIterator[float]):
    def __init__(self,src):
        self._src=src
        self._n=0
    def __next__(self):
        self._n+=1
        if self._n%2==0:
            raise RecoverableStopIteration()
        else:
            return next(self._src)



tone=XPskSinTone(10,10)
preamble=CoffPreamble(tone)






mod=TbskModulator(tone,preamble)
encd=[i for i in mod.modulate([4,5,6])]+[0]*1000
src=encd
print("Length of  encoded",len(src))

demod=TbskDemodulator_impl(tone)

ret=None
try:
    ret=demod.demodulateAsBit(NoneSplitIterator(iter(src)))
    # ret=demod.demodulateAsBit(iter(src))
except RecoverableException as e:
    # print("recover root")
    recover:TbskDemodulator_impl.AsyncDemodulate[int]=e.detach()
    while not recover.run():
        pass
    ret=recover.result
if ret is not None:
    print(ret.pos)
    print([i for i in SkipRecoverIteraor(ret)])
    print(ret.pos)
else:
    print("no ret")
