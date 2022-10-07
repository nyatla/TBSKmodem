from time import sleep
from threading import Thread




from ..io.audio.sddeviceaudio import SoundDeviceAudioPlayer, SoundDeviceInputIterator
from ..utils.wavefile import PcmData
from ..types import Sequence, Tuple





class SoundKit:
    """ サウンドテストをサクサク書くためのツール
    """
    @classmethod
    def play(cls,pcm:PcmData)->PcmData:
        with SoundDeviceAudioPlayer(pcm) as audio:
            audio.play()
            audio.wait()
    @classmethod
    def listenPcm(cls,sig:PcmData,silence:Tuple[float,float]=(0.5,0.5))->Sequence[float]:
        ret=[]
        with SoundDeviceInputIterator(sig.frame_rate) as stream:
            def proc():
                try:
                    ret.append([i for i in stream])
                finally:
                    pass
            th=Thread(target=proc)
            th.start()
            sleep(silence[0])
            cls.play(sig)
            sleep(silence[1])
            stream.close()
            th.join()
        return ret[0]