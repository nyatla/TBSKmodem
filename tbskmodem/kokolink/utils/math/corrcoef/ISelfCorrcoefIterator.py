from ....interfaces import IRecoverableIterator

class ISelfCorrcoefIterator(IRecoverableIterator[float]):
    """ 正規化したdouble値入力から自己相関関数を返すイテレータです。
    """
