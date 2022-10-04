""" wavに保存した振幅信号からビットを復元します。
"""
try:
    from tbskmodem import TbskDemodulator,XPskSinTone,PcmData
except ModuleNotFoundError:
    import sys,os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskDemodulator,XPskSinTone,PcmData
    print("Imported local library.")



def main():

    wav=None
    with open("step1.wav","rb") as fp:
        wav=PcmData.load(fp)

    # tone=SinTone(20,8)
    tone=XPskSinTone(10,10)
    demod=TbskDemodulator(tone)

    ret=demod.demodulateAsBit(iter(wav.dataAsFloat()))
    print([i for i in ret])

if __name__ == "__main__":
    main()
