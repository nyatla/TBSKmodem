""" tbsk変調したWAVファイルを作ります。
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tbskmodem import TbskModulator,XPskSinTone,PcmData


def main():
    # tone=SinTone(10,10).mul(0.5)      # DPSK
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload=[0,1,0,1,0,1,0,1]*16 # 16byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    src_pcm=[i for i in mod.modulateAsBit(payload)]

    #save to wave
    with open("step1.wav","wb") as fp:
        PcmData.dump(PcmData(src_pcm,16,carrier),fp)


if __name__ == "__main__":
    main()

