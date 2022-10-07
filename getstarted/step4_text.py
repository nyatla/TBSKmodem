""" wavに保存した振幅信号から文字列を復元します。
"""
import sys,os
try:
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData
    print("[WARN] Imported local library.")

def main():
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload="アンタヤルーニャ" # 8byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    wav=PcmData([i for i in mod.modulate(payload)],16,carrier)
    #save to wave
    with open("step4.wav","wb") as fp:
        PcmData.dump(wav,fp)

    #demodulate to bytes
    demod=TbskDemodulator(tone)
    ret=demod.demodulateAsStr(wav.dataAsFloat())
    print([i for i in ret])

if __name__ == "__main__":
    main()