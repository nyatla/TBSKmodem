""" リアルタイムに文字列を受信するサンプルです。
"""
import threading
import sys,os
try:
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator
    print("[WARN] Imported local library.")

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
    with SoundDeviceInputIterator(carrier,device_id=None) as stream:
        def checkInput():
            print("Press [ENTER] to stop.")
            try:
                input()
            except EOFError:
                pass
            finally:
                stream.close()
        th=threading.Thread(target=checkInput)
        th.start() 
        try:
            while True:
                print(">",end="",flush=True)
                s=demod.demodulateAsStr(stream)
                if s is None:
                    break
                for i in s:
                    print(i,end="",flush=True)
                print("\nEnd of signal.")
        except KeyboardInterrupt:
            print("\nInterrupted.")
        finally:
            th.join()


if __name__ == "__main__":
    main()
