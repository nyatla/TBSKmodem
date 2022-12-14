"""sounddeviceをラップします。

sounddeviceをインストールしてください。

    conda install -c conda-forge python-sounddevice
    or
    python3 -m pip install sounddevice

このコードはsounddeviceの非公開APIにアクセスします。version '0.4.1'以外では動作しないかもしれませんぞ。
https://python-sounddevice.readthedocs.io/
"""


from time import sleep
import sounddevice as sd
from typing import Iterable, Iterator, overload,Union
import sys
from threading import Lock,Event
import itertools


import logging
log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
from .audioif import IAudioPlayer,IAudioInputInterator
from ...utils.functions import isinstances
from ...utils.wavefile import PcmData
from ...types import Sequence,BinaryIO,Queue,Empty,NoneType



import struct
from typing import Union
from ...types import Iterator
class Bytes8to2FloatIterator(Iterator[float]):
    def __init__(self,src:bytes):
        self._src=iter(src)
    def __next__(self) -> float:
        return next(self._src)/255-0.5

class Bytes16to2FloatIterator(Iterator[float]):
    def __init__(self,src:bytes):
        self._src=iter(src)
    def __next__(self) -> float:
        r=(2**16-1)//2 #Daisukeパッチ
        # b=struct.pack("2B",next(self._src),next(self._src))
        # d=struct.unpack("<h",b)[0]
        # return struct.unpack("<h",b)[0]/r
        # f=next(self._src)
        # g=next(self._src)
        # c=g<<8 | f
        # k=c if 0x8000 & c == 0 else c-0xffff-1
        # h=struct.unpack("<h",struct.pack("2B",f,g))[0]
        # assert(h==k)
        # return h/r
        c=next(self._src) | next(self._src)<<8
        k=c if 0x8000 & c == 0 else c-0xffff-1
        return k/r






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
    def __init__(self,pcm:PcmData,devide_id:int=0):
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
                self._data=tuple(Bytes8to2FloatIterator(data))
                # print(self._data[0:500])
            else:
                self._data=tuple(Bytes16to2FloatIterator(data))
            self._framerate=framerate
            self._current_pos=None
            self._device_id=device_id if device_id is not None else sd.default.device
        if isinstances(args,(BinaryIO,int,int,int,int)):
            __init__B(*args)
        elif isinstances(args,(str,),(kwd,{"device_id":(int,NoneType)})):
            __init__C(*args,**kwd)
        elif isinstances(args,[PcmData,],(kwd,{"device_id":(int,NoneType)})):
            __init__D(*args,**kwd)
        elif len(args) in [1,2]:
            __init__A(*args)
        else:
            raise ValueError(args)
        self._framerate:float
        self._data:Iterator[float]
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
        diter=iter(self._data)      
        self._current_pos=0
        def callback(outdata, frames, time, status):
            if status:
                print(status)
            d=list(itertools.islice(diter,0,frames))
            for i in range(len(d)):
                outdata[i]=d[i]
            for i in range(frames-len(d)):
                outdata[i+len(d)]=0
            self._current_pos=self._current_pos+len(d)
            if len(d)==0:
                raise sd.CallbackStop()

        stream = sd.OutputStream(
            dtype="float32",latency="high",
            samplerate=self._framerate, device=self._device_id, channels=1,
            callback=callback, finished_callback=self._finish_event.set)
        stream.start()
        self._stream=stream
    @property
    def pos(self)->float:
        return self._current_pos/(len(self._data))
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
    def __init__(self,framerate:int=8000,bits_par_sample:int=16,device_id:Union[int,str]=0):
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
                print("[WARN] "+status, file=sys.stderr)
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

__all__=[SoundDeviceAudioPlayer,SoundDeviceInputIterator]

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

