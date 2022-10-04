from ...types import List
class GrayCode:
    @classmethod
    def genArray(cls,n:int)->List[int]:
        """ nビットグレイコード生成します。
            Copied from https://qiita.com/b1ueskydragon/items/75cfee42541ea723080c

        """
        if n == 1:
            return [0, 1]

        codes = cls.genArray(n - 1)
        for k in reversed(codes):
            codes.append((1 << (n - 1)) + k)

        return codes


if __name__ == "__main__":
    print(GrayCode.genArray(1))
    print(GrayCode.genArray(2))
    print(GrayCode.genArray(3))


