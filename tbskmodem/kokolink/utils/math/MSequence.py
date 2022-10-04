from ...types import Dict,Iterator

class MSequence(Iterator[int]):
    """M系列シーケンスを返すイテレータを生成します。
    """
    def __init__(self,bits:int,tap:int=None,sr=1):
        assert(bits<64)
        assert(bits>=2)
        assert((tap is None) or tap<bits)
        assert(sr!=0)
        self._bits=bits-1 #最大ビット位置
        self._tap=tap if tap is not None else bits-2 #タップビット位置
        self._mask=(2**bits-1)
        self._sr=sr&self._mask
        ...
    def __next__(self)->int:
        b=self._bits
        t=self._tap
        sr=self._sr
        # type(sr)
        
        m=(sr>>b)
        n=(sr>>t)
        # print(sr,(sr<<1) , (n^m),(sr<<1)+ (n^m))
        bit=(n^m) & 1
        sr=(sr<<1) | bit
        self._sr=sr & self._mask
        return bit
    @property
    def maxcycle(self):
        """最大周期を返します。
        """
        return 2**(self._bits+1)-1
    def gets(self,n:int):
        """n個の成分を返します。
        """
        return tuple([next(self) for i in range(n)])
    def getOneCycle(self):
        """1サイクル分のシーケンスを得ます
        """
        return self.gets(self.cycles())
    def cycles(self)->int:
        """M系列の周期を計測します。
        """
        old_sr=self._sr
        l=self.maxcycle
        b=[]
        b.append(next(self))
        mv=0
        for i in range(l+1):
            b.append(next(self))
            #チェック
            if b[0:i]==b[i:i*2]:                
                mv=i
            b.append(next(self))
        # print("".join([str(i)for i in b]))
        self._sr=old_sr
        return mv
    @classmethod
    def getCyclesMap(cls,bits)->Dict[int,int]:
        """bitsのサイクル一覧を返します。
        n番目の要素にtap=nのサイクル数が返ります。
        """
        r={}
        for i in range(bits-1):
            m=MSequence(bits,i)
            r[i]=m.cycles()
        return r


if __name__ == '__main__':

    """タップ位置の一覧を計算すりゅ
    """
    for bits in range(2,8):
        m=MSequence.getCyclesMap(bits)
        for tap in m:
            s=MSequence(bits,tap)
            print(bits,tap,m[tap],"".join([str(i)for i in s.gets(m[tap])]))

