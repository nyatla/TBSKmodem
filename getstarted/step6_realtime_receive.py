""" リアルタイムに文字列を受信するサンプルです。
"""
import threading
import sys,os
try:
    from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,PcmData,SoundDeviceInputIterator
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,PcmData,SoundDeviceInputIterator
    print("[WARN] Imported local library.")

def main():
    #save to sample
    tone=TbskTone.createXPskSin(10,10).mul(0.5)    # SSFM DPSK
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
    terminated=False
    with SoundDeviceInputIterator(carrier,device_id=None) as stream:
        def sub():
            demod=TbskDemodulator(tone)
            try:
                while not terminated:
                    print(">",end="",flush=True)
                    s=demod.demodulateAsStr(stream)
                    if s is None:
                        break
                    for i in s:
                        print(i,end="",flush=True)
                    print("\nEnd of signal.")
            except KeyboardInterrupt:
                print("\nInterrupted.")
        try:
            th=threading.Thread(target=sub)
            th.start()
            print("Press [ENTER] to stop.")
            input()
        except EOFError:
            pass
        finally:
            terminated=True
            stream.close()#ストリームを止めてTBSKのブロッキングを解除
            print("join")
            th.join()
            print("closed")







if __name__ == "__main__":
    main()
