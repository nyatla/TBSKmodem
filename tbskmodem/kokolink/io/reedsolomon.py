""" ReedSolomon符号ライブラリへの依存性を切り離すための実装です。

    https://mathlog.info/articles/3167

    GF(2) b111       0x7   7   x2+x1+1 
    GF(3) b1011      0x0b  11  x3+x1+1 
    GF(4) b10011     0x13  19  x4+x1+1 
    GF(5) b100101    0x25  37  x5+x2+1 
    GF(6) b1000011   0x43  67  x6+x1+1
    GF(7) b10000011  0x83  131 x7+x1+1
    GF(8) b100011101 0x11d 285 x^8+x^4+x^2+x^1


"""
from abc import ABC, abstractmethod,abstractproperty
from msilib.schema import Error
from typing import TypeVar,Sequence
from ..interfaces import IConverter

from ..streams import RoStream

from ..filter import BitsWidthFilter





class StopIteration_RS_DecodeError(StopIteration):
    ...
    
import reedsolo as rs
from reedsolo import gf_log, gf_exp, field_charac
import math



class ReedSoloCoder(IConverter[Sequence[int]]):
    @property
    def payload_size(self):
        return self._message_size
    @property
    def packet_size(self)->int:
        return self._packet_size
    @property
    def rate(self)->float:
        """ 実効レート
        """
        return 1-(self._ecc_syms/self._block_syms)
    def _push(self):
        global gf_log, gf_exp, field_charac
        self._global_params=(gf_log, gf_exp, field_charac)
        if self._local_params is not None:
            gf_log, gf_exp, field_charac=self._local_params
    def _pop(self):
        global gf_log, gf_exp, field_charac
        self._local_params=(gf_log, gf_exp, field_charac)
        gf_log, gf_exp, field_charac=self._global_params

    def __init__(self,message_size:int,block_syms:int,ecc_syms:int,prim:int=0x11d,fcr:int=0):
        """ 長さがmessage_sizeのbyte値をmbspos(prim)ビットでシンボル化して、GF(2*mbspos(prim)-1)の短縮RS符号を生成します。
            出力は、短縮RS符号を左詰めして連結したバイト配列です。


            パラメータは以下の条件を満たす必要があります。

            ※ symbits      = mbspos(prim) RSシンボルビット幅
            ※ payload_syms = block_syms-ecc_syms

            短縮RSのブロックサイズ      block_syms<2**symbits
            eccのサイズ                ecc_syms<block_size
            メッセージサイズとECCの関係 ((message_size*8)/(payload_syms*symbits)*(block_syms*symbits))%8=0

            出力のデータ長DESTのバイト長は以下の通りです。
            DEST = [ブロック数] * block_syms * sym_bits / 8
                 = [メッセージシンボル数]/[ペイロードシンボル数] * block_syms * sym_bits / 8
                 = (message_size*8/symbits) / payload_syms * block_syms * sym_bits / 8
                 = (message_size) / (block_syms-ecc_syms) * block_syms
            例
            message=8, blocks_syms=4,ecc_syms=2
                = 8/(4-2)*4  = 16
            message=32, blocks_syms=6,ecc_syms=2
                = 32/(6-2)*6 = 48
        """
        self._local_params=None
        def mbsPos(n:int):
            """ 値nの最上位ビット位置を得ます。
            """
            assert(n>0)
            c=0
            while n!=0:
                c=c+1
                n=n>>1    
            return c
        # symbits換算のメッセージサイズとパケットサイズを計算
        symbits=mbsPos(prim)-1
        #print("symbit",symbits,prim)
        # print(message_size*8,payload_bits)
        # print(message_size*8/((block_syms-ecc_syms)*symbits)) #ペイロードのビット数
        assert(block_syms<2**symbits) #短縮RSの最大値チェック
        # assert(message_size*8%payload_bits==0)#バイト境界かチェック
        self._bits_per_sym=symbits
        self._block_syms=block_syms
        self._ecc_syms=ecc_syms
        self._payload_syms=block_syms-ecc_syms
        self._message_size=message_size
        self._packet_size=int(self._message_size*self._block_syms/(self._block_syms-self._ecc_syms))
        assert(self._message_size*self._block_syms%(self._block_syms-self._ecc_syms)==0)

        self._push()
        rs.init_tables(prim=prim,c_exp=symbits)
        self._gen = rs.rs_generator_poly_all(message_size,fcr=fcr)
        self._pop()
        self._message_bits=message_size*8


class ReedSoloEncoder(ReedSoloCoder):
    def __init__(self,*args,**kwds):
        super().__init__(*args,**kwds)
    def convert(self, src: Sequence[int]) -> Sequence[int]:
        assert(len(src)==self._message_size)
        symsize=self._bits_per_sym
        payload_bits=(self._payload_syms*self._bits_per_sym)
        payload_syms=self._block_syms-self._ecc_syms
        n_blocks=int(self._message_size*8/payload_bits)
        # print(self._message_size,payload_bits,self._payload_syms,self._bits_per_sym)
        r=[]
        self._push()
        try:
            #シンボル単位に分割
            bwf1=BitsWidthFilter(8,symsize)
            bwf1.setInput(RoStream[int](src))

            # print(n_blocks,self._message_bits,payload_syms_per_block,self._bits_per_sym)
            # assert(self._message_bits%(payload_syms_per_block)==0)
            block_ecc=self._ecc_syms
            # print(n_blocks,symsize,payload_syms)
            r=[]
            try:
                # print("en>",n_blocks,self._block_syms,symsize)
                for _ in range(n_blocks):
                    d=bwf1.gets(payload_syms,fillup=True)
                    # print(">",payload_syms_per_block,block_ecc,symsize,d)
                    r.extend(rs.rs_encode_msg(d, block_ecc,gen=self._gen[block_ecc]))
                    # print(r)
                bwf2=BitsWidthFilter(symsize,8)
                return [i for i in bwf2.setInput(RoStream[int](r))]
            except StopIteration:
                raise Exception() #何かがおかしい。
        finally:
            self._pop()

class ReedSoloDecoder(ReedSoloCoder):
    def __init__(self,*args,**kwds):
        super().__init__(*args,**kwds)
        self._is_raise_on_error=True
    def convert(self, src: Sequence[int]) -> Sequence[int]:
        # assert(len(src)==self._packet_bits//8)
        symsize=self._bits_per_sym
        block_ecc=self._ecc_syms
        payload_bits=(self._payload_syms*self._bits_per_sym)
        n_blocks=int(self._message_size*8/payload_bits)

        self._push()
        try:
            bwf1=BitsWidthFilter(8,symsize)
            bwf1.setInput(RoStream[int](src))
            r=[]
            try:
                # print(n_blocks,self._block_syms,symsize)

                for _ in range(n_blocks):
                    d=bwf1.gets(self._block_syms,fillup=True)
                    # print("<",d,symsize)
                    try:
                        rmes, recc, errata_pos = rs.rs_correct_msg(d,block_ecc)
                        #print(errata_pos)
                        r.extend(rmes)
                    except rs.ReedSolomonError:
                        if self._is_raise_on_error:
                            raise
                        else:
                            # print("THROW")
                            r.extend(d[:self._block_syms-self._ecc_syms])
                bwf2=BitsWidthFilter(symsize,8)
                return [i for i in bwf2.setInput(RoStream[int](r))]
            except StopIteration:
                raise Exception() #何かがおかしい。
            except rs.ReedSolomonError as e:
                print(e)
                raise StopIteration_RS_DecodeError()
        finally:
            self._pop()












class ReedSolomonCoderBuilder():
    DEFAULT_prim=0x011d
    DEFAULT_fcr=0
    @staticmethod
    def createEncoder(message_size:int,block_syms:int,ecc_syms:int,prim:int=DEFAULT_prim,fcr:int=DEFAULT_fcr)->ReedSoloEncoder:
        """ messsage_sizeのsequence[int]をGF(2^N),N=mbspos(prim)で符号化するコンバータを返します。

            Nが8以外の場合でシンボル長が8に満たない場合、左詰めでbyte単位に成型したint配列を返します。
            
            メッセージの長さは、len(msg)%8==0 && len(msg)%N==0である必要があります。
        """        
        return ReedSoloEncoder(message_size,block_syms,ecc_syms,prim,fcr)
    @staticmethod
    def createDecoder(message_size:int,block_syms:int,ecc_syms:int,prim:int=DEFAULT_prim,fcr:int=DEFAULT_fcr)->ReedSoloDecoder:
        """ messsage_sizeのsequence[int]をGF(2^N),N=mbspos(prim)で復号化するコンバータを返します。
            (message_size*8/N)%8==0でなければなりません。
            Nが8以外の場合でシンボル長が8に満たない場合、左詰めでbyte単位に成型したint配列を返します。
            メッセージの長さは、len(msg)%8==0 && len(msg)%N==0である必要があります。
        """
        return ReedSoloDecoder(message_size,block_syms,ecc_syms,prim,fcr)
