"""
Copyright (C) 2022, nyatla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""

References:
https://www.recordingblogs.com/wiki/list-chunk-of-a-wave-file
"""

import struct
from typing import Union,overload
from abc import ABC, abstractproperty
from io import BytesIO,RawIOBase

from ...types import Sequence,Tuple,List

class Chunk(ABC):
    """チャンクのベースクラス。
    """
    def __init__(self,name:bytes,size:int):
        assert(len(name)==4)
        self._name=name
        self._size=size
    @property
    def name(self)->bytes:
        return self._name
    @property
    def size(self)->int:
        """チャンクのsizeフィールドの値。このサイズはワード境界ではありませぬ。
        ワード境界にそろえるときは、size+size%2を使います。
        """
        return self._size
    @abstractproperty
    def data(self)->bytearray:
        """チャンクデータ部分です。このサイズはワード境界ではありませぬ。
        """
        raise NotImplementedError ()
    def toChunkBytes(self)->bytes:
        """チャンクのバイナリ値に変換します。このデータはワード境界です。
        """
        d=self.data
        if len(d)%2!=0:
            #word境界
            d=d+b"\0"
        return struct.pack("<4sL",self._name,self._size)+d
    def _summary_dict(self)->dict:
        return {"name":self.name,"size":self.size}
    def __str__(self)->str:
        return str(self._summary_dict())

class ChunkHeader(Chunk,ABC):
    """Formatフィールドを含むChunk構造を格納するクラス
    """
    @overload
    def __init__(self,fp:RawIOBase):
        ...
    @overload
    def __init__(self,name:bytes,size:int,form:bytes):
        ...
    def __init__(self,*args):
        self._size:int
        self._form:bytes        
        def __init__1(fp:RawIOBase):
            name,size,form=struct.unpack_from('<4sL4s',fp.read(12))
            super(ChunkHeader,self).__init__(name,size)
            self._form=form
            return
        def __init__3(name:str,size:int,form:bytes):
            # print(name,size,form)
            super(ChunkHeader,self).__init__(name,size)
            self._form=form
            return
        if len(args)==1:
            __init__1(*args)
        elif len(args)==3:
            __init__3(*args)
        else:
            ValueError()            
    @property
    def data(self)->bytes:
        return struct.pack("<4s",self._form)
    @property
    def form(self)->int:
        return self._form
    def _summary_dict(self)->dict:
        return dict(super()._summary_dict(),**{"form":self.form})
    # def __str__(self)->str:
        
    #     return str({"name":self.name,"size":self.size,"form":self.form})


class RawChunk(Chunk):
    """ペイロードをそのまま格納するチャンクです.    
    """
    @overload
    def __init__(self,name:bytes,size:int,fp:RawIOBase):
        ...
    @overload
    def __init__(self,name:bytes,rawdata:bytes):
        ...
    def __init__(self,*args):
        self._data:bytes
        def __init__2(name:bytes,data:bytes):
            super(RawChunk,self).__init__(name,len(data))
            self._data=data
        def __init__3(name:bytes,size:int,fp:RawIOBase):
            super(RawChunk,self).__init__(name,size)
            # data=bytearray()
            # data.extend(fp.read(size))
            data=fp.read(size)
            if size%2!=0:
                fp.read(1) #padding
            self._data=data
            # assert(self.size==len(rawdata)-8)
        if len(args)==2:
            __init__2(*args)
        elif len(args)==3:
            __init__3(*args)
        else:
            ValueError()
    @property
    def data(self)->bytes:
        return self._data

WAVE_FORMAT_PCM = 0x0001
class fmtChunk(RawChunk):
    """fmtチャンクを格納するクラス.
    """
    @overload
    def __init__(self,size:int,fp:RawIOBase):
        ...
    @overload
    def __init__(self,framerate:int,samplewidth:int,nchannels:int):
        ...
    def __init__(self,*args):
        def __init__2(size:int,fp:RawIOBase):
            super(fmtChunk,self).__init__(b"fmt ",size,fp)
            fmt,ch=struct.unpack("<HH",self._data[0:4])
            if fmt!=WAVE_FORMAT_PCM:
                raise TypeError("Invalid Format FORMAT=%d,CH=%d"%(fmt,ch))
            # print(self.samplewidth)
        def __init__3(framerate:int,samplewidth:int,nchannels:int):
            # print(framerate,samplewidth,nchannels)
            d=struct.pack(
                '<HHLLHH',
                WAVE_FORMAT_PCM, nchannels, framerate,
                nchannels * framerate * samplewidth,
                nchannels * samplewidth,samplewidth * 8)
            super(fmtChunk,self).__init__(b"fmt ",d)
        if len(args)==2:
            __init__2(*args)
        elif len(args)==3:
            __init__3(*args)
        else:
            raise ValueError()
    @property
    def nchannels(self):
        return struct.unpack("<H",self.data[2:4])[0]
    @property
    def framerate(self):
        return struct.unpack("<L",self.data[4:8])[0]
    @property
    def samplewidth(self):
        """1サンプルに必要なビット数"""
        return struct.unpack("<H",self.data[14:16])[0]
    def _summary_dict(self)->dict:
        return dict(super()._summary_dict(),**{"frametate":self.framerate,"samplewidth":self.samplewidth})

class dataChunk(RawChunk):
    """dataチャンクを格納するクラス
    """
    @overload
    def __init__(self,size:int,fp:RawIOBase):
        ...
    @overload
    def __init__(self,data:bytes):
        ...
    def __init__(self,*args):
        def __init__1(data:bytes):
            super(dataChunk,self).__init__(b"data",data)
        def __init__2(size:int,fp:RawIOBase):
            super(dataChunk,self).__init__(b"data",size,fp)
        if len(args)==1:
            __init__1(*args)
        elif len(args)==2:
            __init__2(*args)
        else:
            ValueError()            

class RiffHeader(ChunkHeader):
    @overload
    def __init__(self,fp:RawIOBase):
        ...
    @overload
    def __init__(self,size:int,form:bytes):
        ...
    def __init__(self,*args):
        def __init__2(size:int,form:bytes):
            super(RiffHeader,self).__init__(b"RIFF",size,form)

        if len(args)==1:
            super().__init__(*args)
            assert(self.name==b"RIFF")
        elif len(args)==2:
            __init__2(*args)
        else:
            ValueError(args)

class RawListChunk(ChunkHeader):
    """下位構造をそのまま格納するLIST
    """
    @overload
    def __init__(self,size:int,form:bytes,fp:RawIOBase):
        ...
    # @overload
    # def __init__(self,size:int,form:bytes):
    #     ...
    def __init__(self,*args):
        self._payload:bytes
        # def __init__1(self,fp):
        #     super().__init__(*args)
        #     self._payload=fp.read(self.size)
        def __init__3(size:int,form:bytes,fp:RawIOBase):
            super(RawListChunk,self).__init__(b"LIST",size,form)
            self._payload=fp.read(size)
        # if len(args)==2:
        #     pass
        #     # __init__1(self,*args)
        if len(args)==3:
            __init__3(*args)
        else:
            ValueError()            
        assert(self._name==b"LIST")
    @property
    def data(self)->bytes:
        return super().data+self._payload

class InfoItemChunk(RawChunk):
    """Info配下のチャンクを格納するクラス
    """
    @overload
    def __init__(self,name:bytes,data:bytes):
        ...
    @overload
    def __init__(self,name:bytes,size:int,fp:RawIOBase):
        ...
    def __init__(self,*args):
        def __init__2(name:bytes,data:bytes):
            assert(len(name)==4)
            super(InfoItemChunk,self).__init__(name,data)
        def __init__3(name:bytes,size:int,fp:RawIOBase):
            super(InfoItemChunk,self).__init__(name,size,fp)
        if len(args)==2:
            __init__2(*args)
        elif len(args)==3:
            __init__3(*args)
    def _summary_dict(self)->dict:
        return dict(super()._summary_dict(),**{"value":self.data})




class InfoListChunk(ChunkHeader):
    @overload
    def __init__(self,size:int,fp:RawIOBase):
        ...
    @overload
    def __init__(self,items:Sequence[InfoItemChunk]):
        """
        Args:
        items
            (タグ名,値)のタプルか、InfoItemChunkオブジェクトの混在シーケンスが指定できます。
            タプルの場合は[0]のフィールドは4バイトである必要があります。
        """
        ...
    def __init__(self,*args):
        self._items:Tuple[InfoItemChunk]
        def __init__2(size:int,fp:RawIOBase):
            super(InfoListChunk,self).__init__(b"LIST",size,b"INFO")
            #Infoパーサ
            read_size=4
            items=[]
            while read_size<self._size:
                name,rsize=struct.unpack_from('<4sL',fp.read(8))
                item=InfoItemChunk(name,rsize,fp)
                read_size+=rsize+rsize%2+8
                items.append(item)
            self._items=items
        def __init__1(items:Sequence[InfoItemChunk]):
            #itemsの整形
            d=[]
            for i in items:
                d.append(i)
            
            s=sum([i.size+i.size%2+8 for i in d])
            self._items=d
            super(InfoListChunk,self).__init__(b"LIST",s,b"INFO")
        if len(args)==1:
            __init__1(*args)
        elif len(args)==2:
            __init__2(*args)
        else:
            ValueError()            
        assert(self._name==b"LIST")
    @property
    def data(self)->bytes:
        payload=b"".join([i.toChunkBytes() for i in self._items])
        return super().data+payload
    @property
    def items(self)->Sequence[InfoItemChunk]:
        return self._items
    def _summary_dict(self)->dict:
        return dict(super()._summary_dict(),**{"info":[i._summary_dict() for i in self.items]})        





class WaveFile(RiffHeader):
    @overload
    def __init__(self,fp:RawIOBase):
        ...
    @overload
    def __init__(self,sample_rate:int,samplewidth:int,nchannel:int,frames:bytes,chunks:Sequence[Chunk]=None):
        """

        
        Args:
            samplewidth : サンプル値のbyte幅。n*8bit幅。
        """
        ...
    def __init__(self,*args):
        self._chunks:Sequence[Chunk]
        def __init__1(fp:RawIOBase):
            super(WaveFile,self).__init__(fp)
            assert(self._form==b"WAVE")
            read_size=4
            chunks=[]
            while read_size<self._size: 
                name,size=struct.unpack_from('<4sL',fp.read(8))
                read_size+=size+(size%2)+8
                # assert(size%2==0)
                if name==b"fmt ":
                    chunks.append(fmtChunk(size,fp))
                elif name==b"data":
                    chunks.append(dataChunk(size,fp))
                elif name==b"LIST":
                    fmt=struct.unpack_from("<4s",fp.read(4))[0]
                    if fmt==b"INFO":
                        chunks.append(InfoListChunk(size,fp))
                    else:
                        chunks.append(RawListChunk(size,fmt,fp))
                else:
                    chunks.append(RawChunk(name,size,fp))
            self._chunks=chunks
        def __init__4_5(samplerate:int,samplewidth:int,nchannel:int,frames:bytes,extchunks:Sequence[Chunk]=None):
            if len(frames)%(samplewidth*nchannel)!=0:
                ValueError("fammes length {0}%(samplewidth {1} * nchannel {2})".format(frames,samplewidth,nchannel))
            fmt_chunk=fmtChunk(samplerate,samplewidth,nchannel)
            data_chunk=dataChunk(frames)
            chunks:List[Chunk]=[fmt_chunk,data_chunk]
            if extchunks is not None:
                chunks.extend(extchunks)
            s=sum([i.size+i.size%2+8 for i in chunks])+4
            super(WaveFile,self).__init__(s,b"WAVE")
            self._chunks=chunks        
            # super().__init__(len(self.data),b"WAVE")

        al=len(args)
        if al==5 or al==4:
            __init__4_5(*args)
        elif al==1:
            __init__1(*args)
        else:
            ValueError()
    @property
    def data(self)->bytes:
        payload=b"".join([i.toChunkBytes() for i in self._chunks])
        return super().data+payload
    def chunk(self,name:bytes)->Chunk:
        """ nameに一致するchunkを返します。
            Return:
                チャンクが見つかればチャンクオブジェクトを返します。なければNoneです。
        """
        for i in self._chunks:
            if i.name==name:
                return i
        return None
    def __str__(self):
        return str([str(i) for i in self._chunks])


if __name__ == '__main__':
    with open("cat1.wav","rb") as f:
        src=f.read()
        r=WaveFile(BytesIO(src))
        print(r)
        dest=r.toChunkBytes()
        print(src==dest)
        for i in range(len(src)):
            if src[i]!=dest[i]:
                print(i)
        with open("ssss.wav","wb") as g:
            g.write(dest)
        n=WaveFile(44100,2,2,r.chunk(b"data").data)
        with open("ssss2.wav","wb") as g:
            g.write(n.toChunkBytes())

        n=WaveFile(44100,2,2,r.chunk(b"data").data,[
            InfoListChunk([
                    InfoItemChunk(b"IARL",b"The location where the subject of the file is archived"),
                    InfoItemChunk(b"IART",b"The artist of the original subject of the file"),
                    InfoItemChunk(b"ICMS",b"The name of the person or organization that commissioned the original subject of the file"),
                    InfoItemChunk(b"ICMT",b"General comments about the file or its subject"),
                    InfoItemChunk(b"ICOP",b"Copyright information about the file (e.g., 'Copyright Some Company 2011')"),
                    InfoItemChunk(b"ICRD",b"The date the subject of the file was created (creation date)"),
                    InfoItemChunk(b"ICRP",b"Whether and how an image was cropped"),
                    InfoItemChunk(b"IDIM",b"The dimensions of the original subject of the file"),
                    InfoItemChunk(b"IDPI",b"Dots per inch settings used to digitize the file"),
                    InfoItemChunk(b"IENG",b"The name of the engineer who worked on the file"),
                    InfoItemChunk(b"IGNR",b"The genre of the subject"),
                    InfoItemChunk(b"IKEY",b"A list of keywords for the file or its subject"),
                    InfoItemChunk(b"ILGT",b"Lightness settings used to digitize the file"),
                    InfoItemChunk(b"IMED",b"Medium for the original subject of the file"),
                    InfoItemChunk(b"INAM",b"Title of the subject of the file (name)"),
                    InfoItemChunk(b"IPLT",b"The number of colors in the color palette used to digitize the file"),
                    InfoItemChunk(b"IPRD",b"Name of the title the subject was originally intended for"),
                    InfoItemChunk(b"ISBJ",b"Description of the contents of the file (subject)"),
                    InfoItemChunk(b"ISFT",b"Name of the software package used to create the file"),
                    InfoItemChunk(b"ISRC",b"The name of the person or organization that supplied the original subject of the file"),
                    InfoItemChunk(b"ISRF",b"The original form of the material that was digitized (source form)"),
                    InfoItemChunk(b"ITCH",b"The name of the technician who digitized the subject file"),]
                    )])
        with open("ssss3.wav","wb") as g:
            g.write(n.toChunkBytes())
        with open("ssss3.wav","rb") as g:
            r=WaveFile(g)
            print(r)

    with open("ssss2.wav","rb") as f:
        src=f.read()
        r=WaveFile(BytesIO(src))
        print(r)
