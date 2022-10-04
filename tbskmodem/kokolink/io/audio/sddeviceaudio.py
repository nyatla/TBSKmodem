"""sounddeviceをラップします。

sounddeviceをインストールしてください。

    conda install -c conda-forge python-sounddevice
    or
    python3 -m pip install sounddevice

このコードはsounddeviceの非公開APIにアクセスします。version '0.4.1'以外では動作しないかもしれませんぞ。
https://python-sounddevice.readthedocs.io/
"""


from queue import Empty, Queue
from time import sleep
import sounddevice as sd
import numpy as np
from typing import overload,Union
import sys
from threading import Lock,Event


import logging
log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
from .audioif import IAudioPlayer,IAudioInputInterator
from ...utils.functions import isinstances
from ...utils.wavefile import PcmData
from ...types import Sequence,BinaryIO

class SoundDeviceAudioPlayer(IAudioPlayer):
    """SoundDeviceをラップしたプレイヤーです。
    """
    @overload
    def __init__(self,fp):
        ...
    @overload
    def __init__(self,filepath:str,devide_id:int=0):
        ...
    @overload
    def __init__(self,pcm:PcmData):
        ...
    @overload
    def __init__(self,data:bytes,samplebits:int=8,framerate:int=8000,channels:int=1,device_id:int=None):
        ...
    def __init__(self,*args,**kwd):
        def __init__A(fp,device_id:int=None):
            __init__D(PcmData.load(fp),device_id)
        def __init__C(filepath:str,device_id:int=None):
            with open(filepath,"rb") as fp:
                __init__A(fp,device_id)
        def __init__D(pcm:PcmData,device_id:int=None):
            __init__B(pcm.data,samplebits=pcm.sample_bits,framerate=pcm.frame_rate,channels=1,device_id=device_id)
        def __init__B(data:bytes,samplebits:int=8,framerate:int=8000,channels:int=1,device_id:int=None):
            assert(channels==1)
            if samplebits==8:
                self._data=(np.frombuffer(data, dtype="uint8").astype("int16")-128).astype("int8")
                # print(self._data[0:500])
            else:
                self._data=np.frombuffer(data, dtype="int16")
            self._framerate=framerate
            self._current_pos=None
            self._device_id=device_id if device_id is not None else sd.default.device
        if isinstances(args,(BinaryIO,int,int,int,int)):
            __init__B(*args)
        elif isinstances(args,(str,int)) or isinstances(args,(str,)):
            __init__C(*args)
        elif isinstances(args,[PcmData,]):
            __init__D(*args)
        elif len(args) in [1,2]:
            __init__A(*args)
        else:
            raise ValueError(args)
        self._framerate:float
        self._data:np.ndarray
        self._current_pos:int
        self._device_id:int
        self._stream:sd.Stream=None
        self._finish_event = Event()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def play(self):
        assert(self._stream is None)
        self._finish_event.clear()        
        self._current_pos=0
        def callback(outdata, frames, time, status):
            if status:
                print(status)
            chunksize = min(len(self._data) - self._current_pos, frames)
            # print(chunksize,len(outdata))
            # print(len(outdata),len(self._data),chunksize)
            for i in range(chunksize):
                outdata[i]=self._data[self._current_pos+i]
            for i in range(chunksize,frames):
                outdata[i]=0
            if chunksize<1:
                raise sd.CallbackStop()


            # outdata = np.reshape(self._data[self._current_pos:self._current_pos + chunksize],[chunksize,1])
            
            # outdata[:chunksize]=[[i] for i in self._data[self._current_pos:self._current_pos + chunksize]]
            # outdata[:chunksize] = np.reshape(self._data[self._current_pos:self._current_pos + chunksize],[chunksize,1])
            # print(chunksize,len(outdata),outdata)
            # if chunksize < frames:
            #     outdata[chunksize:] = [[0] for i in range(chunksize)]
            # self._current_pos += chunksize


            # chunksize = min(len(self._data) - self._current_pos, frames)
            # if chunksize<1:
            #     raise sd.CallbackStop()
            # outdata[:chunksize] = np.reshape(self._data[self._current_pos:self._current_pos + chunksize],[chunksize,1])
            # if chunksize < frames:
            #     outdata[chunksize:] = 0
            self._current_pos += chunksize
        stream = sd.OutputStream(
            dtype=self._data.dtype,
            samplerate=self._framerate, device=self._device_id, channels=1,
            callback=callback, finished_callback=self._finish_event.set)
        stream.start()
        self._stream=stream
    def stop(self):
        if self._stream is None:
            return
        if not self._stream.stopped:
            self._stream.stop()
            self._stream.close()
        self._ctx=None
    def wait(self):
        if self._stream is None:
            return
        self._finish_event.wait()
        self._stream=None
    def close(self):
        if self._stream is not None:
            self.stop()



    

class SoundDeviceInputIterator(IAudioInputInterator):
    """SoundDeviceの録音デバイスをラップしたイテレータです。
    値は非同期に取り込まれ、読み出されるまでキューに溜まります。
    キューイングはstart,または__enter__で開始され、stopで停止します。stopしたイテレータはcloseしない限りstartで再開できます。再開すると、その時点でのキューの内容は破棄されます。
    close,__exit__によりストリームを閉じます。
    """
    def __init__(self,framerate:int=8000,device_id:Union[int,str]=0,bits_par_sample:int=16):
        """
        Args:
            frames_per_buffer pyaudioから受け取るフレームのサイズです。framerateの1/nで1秒間当たりの更新回数になります。
        """
        log.debug(str({"frametate":framerate}))

        # q=Deque[float]()
        self._dtype={8:"uint8",16:"int16"}[bits_par_sample]
        self._rate=framerate
        self._stream:sd.Stream=None
        self._q=Queue[float]()
        self._device=device_id
        self._terminate=None
        self._lock = Lock()
        self._samplebits=bits_par_sample


        def audio_callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            a=self.array2float(indata[::, 0],self._samplebits)
            for i in a:
                self._q.put(i)

        self._stream = sd.InputStream(dtype=self._dtype,
            device=self._device, channels=1,
            samplerate=self._rate,callback=audio_callback)
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
        """ データの取り込みを開始します。
            取り込みキューは初期化されます。
        """
        assert(self._stream is not None)
        assert(self._stream.stopped)
        #キューのリセット
        if self._q.qsize()>0:
            log.info("以前のデータを削除します。")
            try:
                while self._q.qsize()>0:
                    self._q.get_nowait()
            except Empty:
                pass
        with self._lock:
            self._terminate=False
        self._stream.start()
        log.info("Start Capture")
    def stop(self):
        """PyAudioからのデータの取り込みを停止します。既に取り込まれている値は無効です。
        Startで再開できます。
        """
        assert(self._stream is not None)
        if not self._stream.stopped:
            with self._lock:
                self._terminate=True
            self._q.put(None)#ダミー君
            self._stream.stop()
        #ここでスピンロックしてマツケンサンバでも良いけどゴミの入ったself._qを抱え続けることにする。
    def close(self):
        if self._stream is None:
            return
        self.stop()
        if not self._stream.closed:
            self._stream.close()
        self._stream=None
    @staticmethod
    def array2float(src:Sequence[int],bits:int)->Sequence[float]:
        """waveペイロードをfloatシーケンスへ変換します。
        """
        if bits==8:
            return src/255-0.5
        if bits==16:
            r=(2**16-1)//2 #Daisukeパッチ
            return src/r
        raise ValueError()


if __name__ == '__main__':
    with SoundDeviceInputIterator() as audio:
        print("222")
        sleep(10)


# if __name__ == '__main__':
#     with SoundDeviceAudioPlayer("test.wav") as audio:
#         audio.play()
#         sleep(1)
#         with SoundDeviceAudioPlayer("test.wav") as audio2:
#             audio2.play()
#             audio.wait()
#             audio2.wait()

