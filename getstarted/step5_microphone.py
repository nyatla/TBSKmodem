""" マイクのテストスクリプトです。
    ターミナルにマイクの音量を表示します。
"""
import threading
import sys,os

try:
    from tbskmodem import SoundDeviceInputIterator
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import SoundDeviceInputIterator
    print("[WARN] Imported local library.")

import math
def main():
    #save to sample
    carrier=8000
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
            scale=carrier//10
            print("Volume meter")
            print("",end="",flush=True)
            while True:
                v=sum([abs(next(stream)) for i in range(scale)])/scale
                v=int(min(max(math.log10(v)+2.2,0),2)*25)
                s="#"*v+" "*(50-v)
                print("\r"+s,end="",flush=True)
        except StopIteration:
            pass
        except KeyboardInterrupt:
            print("\nInterrupted.")
        finally:
            th.join()
        

if __name__ == "__main__":
    main()
