from typing import Union, overload

from ...types import Sequence,Tuple

from ...utils.functions import isinstances
from ...utils import FloatConverter
from .riffio import Chunk, RawChunk, WaveFile,fmtChunk



import logging
log = logging.getLogger(__name__)

def float2bytes(fdata:Sequence[float],bits:int)->bytes:
    """-1<n<1をWaveファイルペイロードへ変換
    """
    if bits==8:
        #return b"".join([struct.pack("B",int(i*127+128)) for i in fdata]) #unsigned byte        
        return b"".join([FloatConverter.doubleToByte(i).to_bytes(1,'little',signed=False) for i in fdata]) #unsigned byte
    elif bits==16:
        #r=(2**16-1)//2 #Daisukeパッチ
        #return b"".join([struct.pack("<h",int(i*r)) for i in fdata]) #signed short
        return b"".join([FloatConverter.doubleToInt16(i).to_bytes(2,'little',signed=True) for i in fdata]) #unsigned byte
    raise ValueError()

class PcmData:
    """ wavファイルのラッパーです。1chモノラルpcmのみ対応します。
    """
    @classmethod
    def load(cls,fp,chunks:Sequence[bytes]=None)->Union["PcmData",Tuple["PcmData",Sequence[Chunk]]]:
        """ ファイルからPCMインスタンスを生成します。
            Args:
                fp  ファイルポインタ
                chunks  同時に取得するチャンクのリスト。定義順に取得します。
            Returns:
                chunksがNoneの場合、PcmDataを返します。
                それ以外の場合、PcmData,Sequence[Chunk]です。

        """
        wav=WaveFile(fp)
        fmtc:fmtChunk=wav.chunk(b"fmt ")
        datac:RawChunk=wav.chunk(b"data")
        assert(fmtc is not None and datac is not None and fmtc.nchannels==1)
        bits=fmtc.samplewidth
        fs=fmtc.framerate
        if chunks is None:
            return cls(datac.data,bits,fs)
        else:
            return cls(datac.data,bits,fs),[wav.chunk(i) for i in chunks]
    @classmethod
    def dump(cls,src:"PcmData",fp,chunks:Sequence[Chunk]=None):
        # setting parameters
        wf=WaveFile(src.frame_rate,src.sample_bits//8,1,src.data,chunks)
        fp.write(wf.toChunkBytes())

    @overload
    def __init__(self,frames:bytes,sample_bits:int,frame_rate:int):
        ...
    @overload
    def __init__(self,frames:Sequence[float],sample_bits:int,frame_rate:int):
        ...
    def __init__(self,*args):
        self._sample_bits:int
        self._frame_rate:int
        self._frames:bytes
        def __init__A(frames:bytes,sample_bits:int,frame_rate:int):
            self._sample_bits=sample_bits
            self._frame_rate=frame_rate
            self._frames=frames
        def __init__B(frames:Sequence[float],sample_bits:int,frame_rate:int):
            __init__A(float2bytes(frames,sample_bits),sample_bits,frame_rate)
        if isinstances(args,(bytes,int,int)):
            __init__A(*args)
        elif isinstance(args,(Sequence,int,int)):
            __init__B(*args)
        else:
            raise ValueError(args)
        assert(len(self._frames)%(self._sample_bits//8)==0)   #srcの境界チェック

    @property
    def sample_bits(self)->int:
        """サンプリングビット数
        """
        return self._sample_bits
    @property
    def frame_rate(self)->int:
        """サンプリングのフレームレート
        """
        return self._frame_rate
    @property
    def timelen(self)->float:
        """データの記録時間
        """
        return len(self._frames)/(self._sample_bits//8*self._frame_rate)
    @property
    def byteslen(self)->int:
        """Waveファイルのデータサイズ
        Waveファイルのdataセクションに格納されるサイズです。
        """
        return len(self._frames)
    @property
    def data(self)->bytes:
        """ 振幅データ
        """
        return self._frames
    def dataAsFloat(self)->Sequence[float]:

        data=self._frames
        bits=self._sample_bits
        if bits==8:
            # a=[struct.unpack_from("B",data,i)[0]/256-0.5 for i in range(len(data))]
            # b=list(np.frombuffer(data, dtype="uint8")/256-0.5)
            # print(a==b)
            # return list(np.frombuffer(data, dtype="uint8")/256-0.5)
            return [FloatConverter.byteToDouble(int.from_bytes(data[i],signed=False)) for i in range(len(data))]
        elif bits==16:
            # assert(len(data)%2==0)
            # r=(2**16-1)//2 #Daisukeパッチ
            # a=[struct.unpack_from("<h",data,i*2)[0]/r for i in range(len(data)//2)]
            # b=list(np.frombuffer(data, dtype="int16")/r)
            # print(a==b)
            # return list(np.frombuffer(data, dtype="int16")/r)
            return [FloatConverter.int16ToDouble(int.from_bytes(data[i*2:i*2+2],'little',signed=True)) for i in range(len(data)//2)]
        raise ValueError()  


