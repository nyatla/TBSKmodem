from ...types import Iterator
class XorShiftRand31(Iterator[int]):
    """ https://ja.wikipedia.org/wiki/Xorshift
    """
    def __init__(self,seed:int,skip:int=0):
        self._seed=seed
        for i in range(skip):
            next(self)
    def __next__(self) -> int:
        y=self._seed
        y = y ^ (y << 13)
        y = y ^ (y >> 17)
        y = y ^ (y << 5)
        y=y & 0x7fffffff
        self._seed=y
        return y
    def randRange(self,limit:int)->int:
        """ 0<=n<limit-1の値を返します。
        """
        return next(self) % limit