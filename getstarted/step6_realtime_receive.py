""" リアルタイムに文字列を受信するサンプルです。
"""
try:
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator
except ModuleNotFoundError:
    import sys,os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator
    print("Imported local library.")

def main():
    #save to sample
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload="アンタヤルーニャ" # ?byte
    carrier=16000

    #modulation
    mod=TbskModulator(tone)
    wav=PcmData([0]*(carrier//2)+[i for i in mod.modulate(payload)]+[0]*(carrier//2),16,carrier)
    #save to wave
    with open("step6.wav","wb") as fp:
        PcmData.dump(wav,fp)

    print(carrier/len(tone),"bps")
    print("Play step6.wave in your player.")
    print("Start capturing")
    
    demod=TbskDemodulator(tone)
    with SoundDeviceInputIterator(carrier,device_id=0) as stream:
        while True:
            print(">",end="",flush=True)
            s=demod.demodulateAsStr(stream) # 
            for i in s:
                print(i,end="",flush=True)
            print("\nTerminated.")


if __name__ == "__main__":
    main()