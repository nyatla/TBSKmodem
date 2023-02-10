"""オーディオデバイス捜査のためのインタフェイスを定義します。

"""
from abc import ABC,abstractmethod,abstractproperty

from ...types import Iterator

import logging
log = logging.getLogger(__name__)

class IAudioPlayer(ABC):
    """Audioメディアプレイヤーの操作インタフェイスを定義します。
    """
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    @abstractmethod
    def play(self):
        """先頭から再生します。再生中の場合は失敗します。
        """
        ...
    @abstractmethod
    def stop(self):
        """再生を停止します。既に停止している場合は無視します。
        """
        ...
    @abstractmethod
    def wait(self):
        """再生が終わるまでブロックします。既に停止中なら何もしません。
        """
        ...
    @abstractmethod
    def close(self):
        """セッションを閉じます。
        """
        ...


class IAudioInputInterator(Iterator[float],ABC):
    """Audioデバイスからサンプリング値を取り込むイテレータです。
    サンプリング値は[-1,1]範囲のfloatです。
    """
    def __enter__(self):
        self.start()
        return self
    def __exit__(self,exc_type=None, exc_value=None, traceback=None):
        self.close()
        if traceback is not None:
            log.error(traceback)
    @abstractmethod
    def __next__(self) -> float:
        ...
    @abstractmethod
    def start(self):
        """データの取り込みを開始します。
        取り込みキューは初期化されます。
        """
        ...
    @abstractmethod
    def stop(self):
        """データの取り込みを停止します。
        待機している__next__は直ちに例外を発生させて停止します。
        Startで再開できます。
        """
    @abstractmethod
    def close(self):
        """デバイスの利用を終了します。以降、デバイスの再利用はできません。
        """
        ...
    @abstractproperty
    def rms(self):
        """入力値のRMSを返します。RMSは、min(フレームレート/100,10)サンプルから計算します。
        """
        ...
