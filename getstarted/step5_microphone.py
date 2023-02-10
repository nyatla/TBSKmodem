""" マイクのテストスクリプトです。
    ターミナルにマイクの音量を表示します。
"""
import threading
import time
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
    terminated=False
    with SoundDeviceInputIterator(carrier,device_id=None) as stream:
        def sub():
            try:
                print("Volume meter")
                print("",end="",flush=True)
                while not terminated:
                    v=int(max(0, (0 if stream.rms==0 else (math.log(stream.rms)+5)) * 5))
                    print("\r" + '#'*v + ' '*(50 - v),end="",flush=True)
                    time.sleep(0.03)
            except StopIteration:
                pass
            except KeyboardInterrupt:
                print("\nInterrupted.")
            print("thread closed.")
        try:
            th=threading.Thread(target=sub)
            th.start()
            print("Press [ENTER] to stop.")
            input()
        except EOFError:
            pass
        finally:
            terminated=True
            th.join()
            print("closed")

        

if __name__ == "__main__":
    main()
