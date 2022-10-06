import argparse
from cmath import atan
from email.policy import default
from secrets import choice
from time import sleep
from typing import Callable, Tuple
import re
from tqdm import tqdm


try:
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator,SoundDeviceAudioPlayer,SinTone, TraitTone,__version__
except ModuleNotFoundError:
    import sys,os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tbskmodem import TbskModulator,TbskDemodulator,XPskSinTone,PcmData,SoundDeviceInputIterator,SoundDeviceAudioPlayer,SinTone, TraitTone,__version__
    print("Imported local library.")




# parser

def hexstr2int(src:str)->Tuple[int]:
    return bytes.fromhex(src)
def inputstr(message:str)->str:
    print(message)
    return input()
def str2tone(param:str)->TraitTone:
    m=re.match(r'^[a-z]+\:[1-9][0-9]*(\,[1-9][0-9]*)+$',param)
    if m is not None:
        s=m.group().split(":") #name,param,param,...
        if s[0]=="xpsk":
            p=s[1].split(",")
            if len(p)==2:
                return XPskSinTone(int(p[0]),int(p[1]))
            elif len(p)==3:
                return XPskSinTone(int(p[0]),int(p[1]),int(p[2]))
            raise RuntimeError("tone parameter must be 'xpsk:points,cycle(,shift)'")
        elif s[0]=="sin":
            p=s[1].split(",")
            if len(p)==2:
                return SinTone(int(p[0]),int(p[1]))
            raise RuntimeError("tone parameter must be 'sin:points,cycle'")
    raise RuntimeError("tone parameter must be 'xpsk:P,C(,S)' or 'sin:P,C'")
def str2tone2(param:str)->TraitTone:
    m=re.match(r'^[1-9][0-9]+$',param)
    if m is not None:
        return TraitTone([0]*int(m[0]))
    else:
        return str2tone(param)

class BaseCommand:
    def __init__(self,parser:argparse.ArgumentParser):
        self._parser=parser
    @property
    def help(self):
        return self._parser.format_help()
    @property
    def usage(self):
        return self._parser.format_usage()

class Modulate(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('mod',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Moduleate text or binary to wavefile.",
        epilog=
        "Example:\n"
        "  $tbskmodem mod susi.wav\n"
        "    Modulate console input text to susi.wav with default parameter.\n"
        "  $tbskmodem mod yakitori.wav --text yakitori\n"
        "    Modulate command line text to tempura.wav\n"
        "  $tbskmodem mod tempura.wav --text tempura --carrier 48000\n"
        "    Modulate command line text to tempura.wav with specified carrier frequency.\n"
        "  $tbskmodem mod beef.wav --bin 00beef\n"
        "    Modulate command line hextext to tempura.wav\n"
        "  $tbskmodem mod sabakan.wav --file sabakan.txt\n"
        "    Modulate file contents to tempura.wav in binary.\n",
        help='see `$tbskmodem mod -h`')
        parser_add.add_argument('out',type=str,help='Output wave file name.')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--tone',type=str,default="xpsk:10,10",help='Trait tone format."xpsk:int,int(,int)" | "sin:int:int"')
        parser_add.add_argument('--silence',type=float,default=0.5,help='Silence padding time in sec')
        parser_add.add_argument('--text',type=str,nargs="?" ,default=None,const="",help='Text format input.')
        parser_add.add_argument('--bin',type=str,nargs="?" ,default=None,const="",help='Hex text format input.')
        parser_add.add_argument('--file',type=str,default=None,help='File input')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):

        # print(args)
        tone=str2tone(args.tone)    # SSFM DPSK
        mod=TbskModulator(tone)
        #入力値の判定
        numoffmt=3-[args.text,args.bin,args.file].count(None)
        if numoffmt>1:
            raise RuntimeError("Must be set text,bin,file parameter in exclusive.")
        src_pcm=None
        if numoffmt==0 or args.text is not None:
            src=inputstr("input string>") if numoffmt==0 or len(args.text)==0 else args.text
            src_pcm=[i for i in mod.modulate(src)]
        elif args.bin is not None:
            src=inputstr("input hex string>") if len(args.bin)==0 else args.bin
            src_pcm=[i for i in mod.modulate(hexstr2int(src))]
        elif args.file is not None:
            with open(args.file,"rb") as fp:
                src_pcm=[i for i in mod.modulate(fp.read())]
        else:
            raise RuntimeError()
        
        #save to wave
        carrier=args.carrier
        sample_bits=args.sample_bits
        out=args.out
        silence=[0]*int(carrier*args.silence)

        # print(len(src_pcm))
        pcm=PcmData(silence+src_pcm+silence,sample_bits,carrier)
        with open(out,"wb") as fp:
            PcmData.dump(pcm,fp)
        print("Output file       : %s  %dHz,%dbits,%dch,%.2fsec(silence:%.2fsec x 2)"%(out,pcm.frame_rate,pcm.sample_bits,1,pcm.timelen,args.silence))
        print("Tone              : '%s' %dticks,%.1fmsec/symbol"%(args.tone,len(tone),len(tone)/carrier*1000))
        print("Bit rate          : %.1fbps"%(carrier/len(tone)))
        return

class Demodulate(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('dem',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Demoduleate wavefile to text or binary.",
        epilog=
        "Example:\n"
        "  $tbskmodem dem susi.wav\n"
        "    Demodulate susi.wav with default parameter and print as text format.\n"        
        "  $tbskmodem dem tempura.wav --bin\n"
        "    Demodulate tempura.wav with default parameter and show as hex text format.\n"
        "  $tbskmodem dem tonkatu.wav --text --tone 100\n"
        "    Demodulate tonkatu.wav with specified tone ticks and print as text format.\n"
        "  $tbskmodem dem yakitori.wav --file umai.txt\n"
        "    Demodulate yakitori.wav and save to file.\n",
        help='see `$tbskmodem dem -h`')
        parser_add.add_argument('src',type=str,help='Input wave file name.')
        parser_add.add_argument('--text',action='store_true',help='Show in text.')
        parser_add.add_argument('--bin',action='store_true',help='Show in hex text.')
        parser_add.add_argument('--file',default=False,help='Save to file as is.')
        parser_add.add_argument('--tone',default=None,help='Tone format or ticks.')
        parser_add.add_argument('--noinfo',action='store_true',help='Hide details other than results.')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):
        # print(args)
        lprint=(lambda *a,**k:()) if args.noinfo else print

        pcm:PcmData
        with open(args.src,"rb") as fp:
            pcm=PcmData.load(fp)
        tone=str2tone2("100" if args.tone is None else args.tone)    # SSFM DPSK

        lprint("Input file       : %s  %dHz,%dbits,%dch,%.2fsec"%(args.src,pcm.frame_rate,pcm.sample_bits,1,pcm.timelen))
        lprint("Tone             : %dticks,%.1fmsec/symbol"%(len(tone),len(tone)/pcm.frame_rate*1000))
        lprint("Bit rate         : %.1fbps"%(pcm.frame_rate/len(tone)))
        lprint()
        demod=TbskDemodulator(tone)
        src=pcm.dataAsFloat()
        isrc=iter(src)

        lprint("Start detection.")

        numoffmt=3-[args.text,args.bin,args.file].count(False)
        if numoffmt>1:
            raise RuntimeError("Must be set text,bin,file parameter in exclusive.")
        if numoffmt==0 or args.text==True:
            c=0
            while True:
                try:
                    n=demod.demodulateAsStr(isrc)
                    lprint("Preamble found.")
                except StopIteration:
                    break
                # print("RX>",end="",flush=True)
                for i in n:
                    c=c+1
                    print(i,end="",flush=True)
                print()
                lprint("No data" if c==0 else "End of signal.")
        elif args.bin==True:
            c=0
            while True:
                try:
                    n=demod.demodulateAsBytes(isrc)
                    lprint("Preamble found.")
                except StopIteration:
                    lprint("End of stream.")
                    break
                # print("RX>",end="",flush=True)
                for i in n:
                    c=c+1
                    print(bytes.hex(i),end="",flush=True)
                print()
                lprint("No data" if c==0 else "End of signal.")
        elif args.file!=False:
            d=b""
            while True:
                try:
                    n=demod.demodulateAsBytes(isrc)
                    lprint("Preamble found.")
                    c=c+1
                except StopIteration:
                    lprint("End of stream.")
                    break
                for i in n:
                    d=d+i
                    print(".",end="",flush=True)
                print()
                lprint("No data" if c==0 else "End of signal.")
            if len(d)>0:
                with open(args.file,"wb") as fp:
                    fp.write(d)
                lprint("File saved:%s"%(args.file))
        else:
            raise RuntimeError()
        return

class Tx(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('tx',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Transmit text or binary by audio device as TBSK modulation.",
        epilog=
        "Example:\n"
        "  $tbskmodem tx\n"
        "    Send console input text to susi.wav with default parameter.\n"
        "  $tbskmodem tx --text yakitori\n"
        "    Send command line text\n"
        "  $tbskmodem tx --text tempura --carrier 48000\n"
        "    Send command line text with specified carrier frequency.\n"
        "  $tbskmodem tx --bin 00beef\n"
        "    Send command line hex text\n"
        "  $tbskmodem tx --file sabakan.txt\n"
        "    Send file contents in binary.\n",
        help='see `$tbskmodem mod -h`')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--device',type=int,default=None,help='Audio device id')
        parser_add.add_argument('--tone',type=str,default="xpsk:10,10",help='Trait tone format."xpsk:int,int(,int)" | "sin:int:int"')
        parser_add.add_argument('--silence',type=float,default=0.5,help='Silence padding time in sec')
        parser_add.add_argument('--volume',type=float,default="1.0",help='Volume multiplyer 0 to 1.0')
        parser_add.add_argument('--text',type=str,nargs="?" ,default=None,const="",help='Text format input.')
        parser_add.add_argument('--bin',type=str,nargs="?" ,default=None,const="",help='Hex text format input.')
        parser_add.add_argument('--file',type=str,default=None,help='File input')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):

        # print(args)
        tone=str2tone(args.tone).mul(max(0,min(1,args.volume)))    # SSFM DPSK
        mod=TbskModulator(tone)
        #入力値の判定
        numoffmt=3-[args.text,args.bin,args.file].count(None)
        if numoffmt>1:
            raise RuntimeError("Must be set text,bin,file parameter in exclusive.")
        src_pcm=None
        if numoffmt==0 or args.text is not None:
            src=inputstr("input string>") if numoffmt==0 or len(args.text)==0 else args.text
            src_pcm=[i for i in mod.modulate(src)]
        elif args.bin is not None:
            src=inputstr("input hex string>") if len(args.bin)==0 else args.bin
            src_pcm=[i for i in mod.modulate(hexstr2int(src))]
        elif args.file is not None:
            with open(args.file,"rb") as fp:
                src_pcm=[i for i in mod.modulate(fp.read())]
        else:
            raise RuntimeError()
        
        #save to wave
        carrier=args.carrier
        sample_bits=args.sample_bits
        silence=[0]*int(carrier*args.silence)

        # print(len(src_pcm))
        pcm=PcmData(silence+src_pcm+silence,sample_bits,carrier)
        print("Pcm format       : %dHz,%dbits,%dch,%.2fsec(silence:%.2fsec x 2)"%(pcm.frame_rate,pcm.sample_bits,1,pcm.timelen,args.silence))
        print("Tone             : '%s' %dticks,%.1fmsec/symbol"%(args.tone,len(tone),len(tone)/carrier*1000))
        print("Bit rate         : %.1fbps"%(carrier/len(tone)))
        print("playing...")
        with SoundDeviceAudioPlayer(pcm,device_id=args.device) as sdp:
            sdp.play()
            last=0
            with tqdm(total = pcm.timelen,bar_format="{l_bar}{bar}") as bar:
                while sdp.pos<1:
                    p=max(0,sdp.pos*pcm.timelen)
                    bar.update(p-last) #再生位置/sec *
                    last=p
                    sleep(0.1)
                bar.update(pcm.timelen-last)
            sdp.wait()
        return


class Rx(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('rx',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Receive TBSK siglanfrom audio device.",
        epilog=
        "Example:\n"
        "  $tbskmodem dem susi.wav\n"
        "    Receive TBSK signal with default parameter and print as text format.\n"        
        "  $tbskmodem dem tempura.wav --bin\n"
        "    Receive TBSK signal with default parameter and show as hex text format.\n"
        "  $tbskmodem dem tonkatu.wav --text --tone 100\n"
        "    Receive TBSK siginal with specified tone ticks and print as text format.\n"
        "  $tbskmodem dem yakitori.wav --file umai.txt\n"
        "    Receive TBSK siginal and save to file.\n",
        help='see `$tbskmodem dem -h`')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--device',type=int,default=None,help='Audio device id')
        parser_add.add_argument('--text',action='store_true',help='Show in text.')
        parser_add.add_argument('--bin',action='store_true',help='Show in hex text.')
        parser_add.add_argument('--file',default=False,help='Save to file as is.')
        parser_add.add_argument('--tone',default=None,help='Tone format or ticks.')
        parser_add.add_argument('--noinfo',action='store_true',help='Hide details other than results.')
        parser_add.add_argument('--repeat',action='store_true',help='Repeat signal detection until interrupted.')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):
        # print(args)
        lprint=(lambda *a,**k:()) if args.noinfo else print




        tone=str2tone2("100" if args.tone is None else args.tone)    # SSFM DPSK

        lprint("Audio source     : %dHz,%dbits,%dch deviceid:%s"%(args.carrier,args.sample_bits,1,str(args.device)))
        lprint("Tone             : %dticks,%.1fmsec/symbol"%(len(tone),len(tone)/args.carrier*1000))
        lprint("Bit rate         : %.1fbps"%(args.carrier/len(tone)))
        lprint()
        demod=TbskDemodulator(tone)
        with SoundDeviceInputIterator(args.carrier,device_id=args.device,bits_par_sample=args.sample_bits) as isrc:

        # src=pcm.dataAsFloat()
        # isrc=iter(src)

            lprint("Start detection.")

            numoffmt=3-[args.text,args.bin,args.file].count(False)
            if numoffmt>1:
                raise RuntimeError("Must be set text,bin,file parameter in exclusive.")
            if numoffmt==0 or args.text==True:
                c=0
                while True:
                    try:
                        n=demod.demodulateAsStr(isrc)
                        lprint("Preamble found.")
                    except StopIteration:
                        lprint("End of stream.")
                        break
                    # print("RX>",end="",flush=True)
                    for i in n:
                        c=c+1
                        print(i,end="",flush=True)
                    print("")
                    lprint("No data" if c==0 else "End of signal.")
            elif args.bin==True:
                c=0
                while True:
                    try:
                        n=demod.demodulateAsBytes(isrc)
                        lprint("Preamble found.")
                    except StopIteration:
                        lprint("End of stream.")
                        break
                    # print("RX>",end="",flush=True)
                    for i in n:
                        c=c+1
                        print(bytes.hex(i),end="",flush=True)
                    print("")
                    lprint("No data" if c==0 else "End of signal.")
            elif args.file!=False:
                d=b""
                while True:
                    try:
                        n=demod.demodulateAsBytes(isrc)
                        lprint("Preamble found.")
                        c=c+1
                    except StopIteration:
                        lprint("End of stream.")
                        break
                    for i in n:
                        d=d+i
                        print(".",end="",flush=True)
                    print()
                    lprint("No data" if c==0 else "End of signal.")
                if len(d)>0:
                    with open(args.file,"wb") as fp:
                        fp.write(d)
                    lprint("File saved:%s"%(args.file))
            else:
                raise RuntimeError()
            return

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,prog="tbskmodem")
    sp=parser.add_subparsers()
    parser.add_argument('--version',"-V",action="store_true",help='print version')
    Modulate(sp)
    Demodulate(sp)
    Tx(sp)
    Rx(sp)
    args = parser.parse_args()
    if args.version:
        print("tbskmodem/"+__version__)
    elif hasattr(args, 'handler'):
        print(args.handler.execute(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
        exit(0)
    except Exception as e:
        import traceback
        traceback.print_exception(e)
        exit(-1)