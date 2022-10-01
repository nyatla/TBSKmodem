""" マイクのテストスクリプトです。
    ターミナルにマイクの音量を表示します。
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tbskmodem import SoundDeviceInputIterator


import math
def main():
    #save to sample
    carrier=8000
    with SoundDeviceInputIterator(carrier,device_id=0) as stream:
        scale=carrier//10
        print("Volume meter")
        print("",end="",flush=True)
        while True:
            v=sum([abs(next(stream)) for i in range(scale)])/scale
            v=int(min(max(math.log10(v)+2.2,0),2)*25)
            s="#"*v+" "*(50-v)
            print("\r"+s,end="",flush=True)
        

if __name__ == "__main__":
    main()