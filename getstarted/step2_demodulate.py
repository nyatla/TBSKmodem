""" wavに保存した振幅信号からビットを復元します。
"""
import sys,os
try:
    from tbskmodem import TbskDemodulator,TbskTone,PcmData
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskDemodulator,TbskTone,PcmData
    print("[WARN] Imported local library.")

def main():
    wav=None
    with open("step1.wav","rb") as fp:
        wav=PcmData.load(fp)

    # tone=SinTone(20,8)
    tone=TbskTone.createXPskSin(10,10)
    demod=TbskDemodulator(tone)

    ret=demod.demodulateAsBit(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)

if __name__ == "__main__":
    main()
