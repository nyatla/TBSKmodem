""" wavに保存した振幅信号からbytesを復元します。
"""
import sys,os
try:
    from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,PcmData
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,PcmData
    print("[WARN] Imported local library.")

def main():
    tone=TbskTone.createXPskSin(10,10).mul(0.5)    # SSFM DPSK
    payload=b"0123456789" # 10byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    src_pcm=[i for i in mod.modulate(payload)]

    #save to wave
    wav=PcmData(src_pcm,16,carrier)
    with open("step3.wav","wb") as fp:
        PcmData.dump(wav,fp)

    #demodulate to bytes
    demod=TbskDemodulator(tone)
    ret=demod.demodulateAsBytes(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)

if __name__ == "__main__":
    main()