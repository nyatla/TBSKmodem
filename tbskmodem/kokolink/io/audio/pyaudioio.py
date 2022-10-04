import pyaudio
import numpy as np
from enum import Enum
from threading import Thread,Lock
import logging
log = logging.getLogger(__name__)

from .audioif import IAudioInputInterator
from ...types import Sequence,Empty, Queue

class PyAudioInputIterator(IAudioInputInterator):
    class Status(Enum):
        STARTED=0
        IDLE=1
        CLOSED=2
    """pyaudioを経由してFloat値のデータストリームを取り込みます。
    値は非同期に取り込まれ、読み出されるまでキューに溜まります。
    キューイングはstart,または__enter__で開始され、stopで停止します。stopしたイテレータはcloseしない限りstartで再開できます。再開すると、その時点でのキューの内容は破棄されます。
    close,__exit__によりストリームを閉じます。
    """
    def __init__(self,framerate:int=8000,device_id=0,bits_par_sample:int=16,frames_per_buffer=None):
        """
        Args:
            frames_per_buffer pyaudioから受け取るフレームのサイズです。rateの1/nで1秒間当たりの更新回数になります。
        """
        frames_per_buffer=frames_per_buffer if frames_per_buffer is not None else framerate//10 #指定がなければ0.1秒更新
        audio = pyaudio.PyAudio()
        self._device_id=device_id
        self._frames_per_buffer=frames_per_buffer
        self._rate=framerate
        self._audio=audio
        self._stream=None
        self._bits_per_sample=bits_par_sample
        self._q=Queue[float]()
        self._terminate=False
        self._lock = Lock()      
    def __enter__(self):
        self.start()
        return self
    def __exit__(self,exc_type=None, exc_value=None, traceback=None):
        self.close()
        log.error(traceback)
    def __next__(self) -> float:
        with self._lock:
            if self._terminate:
                raise StopIteration()
        r=self._q.get()
        with self._lock:
            if self._terminate:
                raise StopIteration()
        return r


    def start(self):
        """ PyAudioからデータの取り込みを開始します。
            取り込みキューは初期化されます。
        """
        def proc():
            nonlocal self
            while True:
                with self._lock:
                    if self._terminate:
                        break
                try:
                    fmt={8:"uint8",16:"int16"}[self._bits_per_sample]
                    d16=np.frombuffer(self._stream.read(self._frames_per_buffer),dtype=fmt)
                    for i in self.bytes2float(d16,self._bits_per_sample):
                        self._q.put(i)
                except KeyboardInterrupt:
                    return
                except OSError as e:
                    print(e.errno)
                    if e.errno==-9983:
                        return
                    else:
                        raise
    
        assert(self._stream is None)
        #キューを空にする
        try:
            while True:
                self._q.get_nowait()
        except Empty:
            pass
        fmt={8:pyaudio.paInt8,16:pyaudio.paInt16}[self._bits_per_sample]
        self._terminate=False
        stream = self._audio.open(
            format = fmt,
            rate = int(self._rate),
            channels = 1, 
            input_device_index = self._device_id,
            input = True, 
            frames_per_buffer = self._frames_per_buffer,
            # stream_callback=cb,
            start=True)
        self._stream=stream
        self._th = Thread(target=proc)
        self._th.start()
        return        

    def stop(self):
        """PyAudioからのデータの取り込みを停止します。
        既に取り込まれたデータの読み出しはできますが、終端に到達するとStopIterationが発生します。
        Startで再開できます。
        """
        assert(self._stream is not None)
        if not self._stream.is_stopped():
            self._terminate=True
            self._stream.stop_stream()
            self._stream.close()
            self._th.join()
            self._q.put(None) #stop Interlationの誘発
        self._stream=None
        log.info("Stop Capture")
    def close(self):
        if self._stream is not None:
            self.stop()
        self._audio.terminate()
        self._audio=None

    @staticmethod
    def bytes2float(bdata:bytes,bits:int)->Sequence[float]:
        """waveペイロードをfloatシーケンスへ変換します。
        """
        if bits==8:
            return np.frombuffer(bdata, dtype="int8")/255-0.5
        if bits==16:
            r=(2**16-1)//2 #Daisukeパッチ
            return np.frombuffer(bdata, dtype="int16")/r
        raise ValueError()


