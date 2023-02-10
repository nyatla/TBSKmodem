INT16_MAX=32767
INT16_MIN=-32768

class FloatConverter:
    """ 正規化された浮動小数点値と固定小数点値を相互変換します。
    """
    @staticmethod
    def byteToDouble(b:int)->float:
        return float(b) / 255 - 0.5

    @staticmethod
    def int16ToDouble(b:int)->float:
        if b >= 0:
            return (float(b)) / INT16_MAX
        else:
            return -float(b) / INT16_MIN

    @staticmethod
    def doubleToByte(b:float)->int:
        return int(b * 127 + 128)

    @staticmethod
    def doubleToInt16(b:float)->int:
        assert(1 >= b and b >= -1)
        if b >= 0:
            return int(INT16_MAX * b)
        else:
            return int(-INT16_MIN * b)
