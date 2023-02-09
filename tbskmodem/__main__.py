import argparse

from time import sleep
import re
from tqdm import tqdm
import platform
import sys,os

is_local_library=False


try:
     from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,TraitTone,PcmData,SoundDeviceInputIterator,SoundDeviceAudioPlayer,__version__
except ModuleNotFoundError:
     sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
     from tbskmodem import TbskModulator,TbskDemodulator,TbskTone,TraitTone,PcmData,SoundDeviceInputIterator,SoundDeviceAudioPlayer,__version__
     is_local_library=True


lprint=print

TEXT_RESOURCR={
    "Argument_tone_help":'Trait tone format."xpsk:int,int(,int)" | "sin:int,int | "pcm:str"',
}

# parser



def inputstr(message:str)->str:
    print(message)
    return input()
def str2tone(param:str,carrier:int)->TraitTone:
    m=re.match(r'^[a-z0-1]+\:',param) #name:...
    if m is not None:
        s=m.group() #name,param:param,...
        name=m.group()[:-1] #name:
        value=param[len(name)+1:]
        if name=="xpsk":
            v=re.match(r'^[1-9][0-9]*(\,[1-9][0-9]*)(\,[1-9][0-9]*)?$',value)
            if v is not None:
                p=v.group().split(",")
                if len(p)==2:
                    return TbskTone.createXPskSin(int(p[0]),int(p[1]))
                elif len(p)==3:
                    return TbskTone.createXPskSin(int(p[0]),int(p[1]),int(p[2]))
            raise RuntimeError("xpsk must be 'xpsk:point,cycle,(shift)' 'ex xpsk:10:10'")
        elif name=="sin":
            v=re.match(r'^[1-9][0-9]*(\,[1-9][0-9]*)$',value)
            if v is not None:
                p=v.group().split(",")
                return TbskTone.createSin(int(p[0]),int(p[1]))
            raise RuntimeError("sin must be 'sin:point,cycle' ex 'sin:10,10'")
        elif name=="pn":
            v=re.match(r'^[1-9][0-9]*(\,[1-9][0-9]*)\,',value)
            if v is not None:
                p=v.group().split(",")
                subtone=value[v.span()[1]:]
                if "pn" in subtone:
                    raise ValueError("Recursion error")
                return TbskTone.createPn(int(p[0]),int(p[1]),str2tone(subtone,carrier))
            raise RuntimeError("pn must be 'pn:seed,interval,basetone' ex 'pn:299,2,sin:10,10'")
        elif name=="mseq":
            v=re.match(r'^[1-9][0-9]*(\,[1-9][0-9]*)\,',value)
            if v is not None:
                p=v.group().split(",")
                print(value[v.span()[1]:])
                subtone=value[v.span()[1]:]
                if "mseq" in subtone:
                    raise ValueError("Recursion error")
                return TbskTone.createMSeq(int(p[0]),int(p[1]),str2tone(subtone,carrier))
            raise RuntimeError("Parameter must be 'mseq:bit,tap,base_tone' ex'mseq:3,2,sin:10,10'")
        elif name=="pcm":
            with open(value,"rb") as fp:
                pcm=PcmData.load(fp)
                print(pcm.frame_rate,carrier)
                if pcm.frame_rate!=carrier:
                    raise ValueError("Pcm framerate must be same as carrier")
                return TraitTone(pcm.dataAsFloat())

    raise RuntimeError("tone parameter must be 'xpsk|sin|pn|mseq:...")
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
        "Moduleate text or hex string or binary to wavefile.",
        epilog=
        "Example:\n"
        "  $tbskmodem mod susi.wav\n"
        "    Modulate console input text to susi.wav with default parameter.\n"
        "  $tbskmodem mod yakitori.wav --text yakitori\n"
        "    Modulate command line text to tempura.wav\n"
        "  $tbskmodem mod tempura.wav --text tempura --carrier 48000\n"
        "    Modulate command line text to tempura.wav with specified carrier frequency.\n"
        "  $tbskmodem mod beef.wav --hex 00beef\n"
        "    Modulate command line hex string to beef.wav as binary.\n"
        "  $tbskmodem mod sabakan.wav --file sabakan.txt\n"
        "    Modulate file contents to sabakan.wav in binary.\n",
        help='see `$tbskmodem mod -h`')
        parser_add.add_argument('out',type=str,help='Output wave file name.')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--tone',type=str,default="xpsk:10,10",help=TEXT_RESOURCR["Argument_tone_help"])
        parser_add.add_argument('--silence',type=float,default=0.5,help='Silence padding time in sec')
        parser_add.add_argument('--text',type=str,nargs="?" ,default=None,help='Text format input.')
        parser_add.add_argument('--hex',type=str,nargs="?" ,default=None,help='Hex text format input.')
        parser_add.add_argument('--file',type=str,nargs="?" ,default=None,help='File input')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):

        # print(args)
        tone=str2tone(args.tone,args.carrier)    # SSFM DPSK
        mod=TbskModulator(tone)
        #入力値の判定
        numoffmt=3-[args.text,args.hex,args.file].count(None)
        if numoffmt>1:
            raise RuntimeError("Must be set text,hex,file parameter in exclusive.")
        src_pcm=None
        if numoffmt==0 or args.text is not None:
            src=inputstr("input string>") if numoffmt==0 or len(args.text)==0 else args.text
            lprint("Start Modulation.")
            src_pcm=[i for i in mod.modulate(src)]
        elif args.hex is not None:
            src=inputstr("input hex string>") if len(args.hex)==0 else args.hex
            lprint("Start Modulation.")
            src_pcm=[i for i in mod.modulateAsHexStr(src)]
        elif args.file is not None:
            lprint("Start Modulation.")
            with open(args.file,"rb") as fp:
                src_pcm=[i for i in mod.modulate(fp.read())]
        else:
            raise RuntimeError()
        lprint("Modulated.")
        
        #save to wave
        carrier=args.carrier
        sample_bits=args.sample_bits
        out=args.out
        silence=[0]*int(carrier*args.silence)

        pcm=PcmData(silence+src_pcm+silence,sample_bits,carrier)
        lprint("Output file : %s  %dHz,%dbits,%dch,%.2fsec(silence:%.2fsec x 2)"%(out,pcm.frame_rate,pcm.sample_bits,1,pcm.timelen,args.silence))
        lprint("Tone        : '%s' %dticks,%.1fmsec/symbol"%(args.tone,len(tone),len(tone)/carrier*1000))
        lprint("Bit rate    : %.1fbps"%(carrier/len(tone)))
        lprint()
        with open(out,"wb") as fp:
            PcmData.dump(pcm,fp)
        lprint("Finihed.")
        return

class Demodulate(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('dem',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Demoduleate wavefile to text or hex string or file.",
        epilog=
        "Example:\n"
        "  $tbskmodem dem susi.wav\n"
        "    Demodulate susi.wav with default parameter and print as text format.\n"        
        "  $tbskmodem dem tempura.wav --hex\n"
        "    Demodulate tempura.wav with default parameter and show as hex string format.\n"
        "  $tbskmodem dem tonkatu.wav --text --tone 100\n"
        "    Demodulate tonkatu.wav with specified tone ticks and print as string format.\n"
        "  $tbskmodem dem yakitori.wav --file umai.txt\n"
        "    Demodulate yakitori.wav and save to umai.txt.\n",
        help='see `$tbskmodem dem -h`')
        parser_add.add_argument('src',type=str,help='Input wave file name.')
        parser_add.add_argument('--text',default=None,action='store_const',const=True,help='Show in text.')
        parser_add.add_argument('--hex',default=None,action='store_const',const=True,help='Show in hex string.')
        parser_add.add_argument('--file',default=None,nargs="?",help='Save to file as is.')
        parser_add.add_argument('--tone',default=None,help='Tone format or ticks.')
        parser_add.add_argument('--noinfo',action='store_true',help='Hide details other than results.')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):
        # print(args)

        pcm:PcmData
        with open(args.src,"rb") as fp:
            pcm=PcmData.load(fp)
        tone=str2tone2("100" if args.tone is None else args.tone)    # SSFM DPSK

        lprint("Input file  : %s  %dHz,%dbits,%dch,%.2fsec"%(args.src,pcm.frame_rate,pcm.sample_bits,1,pcm.timelen))
        lprint("Tone        : %dticks,%.1fmsec/symbol"%(len(tone),len(tone)/pcm.frame_rate*1000))
        lprint("Bit rate    : %.1fbps"%(pcm.frame_rate/len(tone)))
        lprint()
        demod=TbskDemodulator(tone)
        src=iter(pcm.dataAsFloat())


        numoffmt=3-[args.text,args.hex,args.file].count(None)
        if numoffmt>1:
            raise RuntimeError("Must be set text,hex,file parameter in exclusive.")
        lprint("Start Demodulation.")
        if numoffmt==0 or args.text==True:
            while True:
                c=0
                n=demod.demodulateAsStr(src)
                if n is None:
                    break
                lprint("Preamble found.")
                # print("RX>",end="",flush=True)
                for i in n:
                    c=c+1
                    print(i,end="",flush=True)
                print()
                lprint("Signal lost.")
            lprint("End of stream.")
        elif args.hex==True:
            while True:
                c=0
                n=demod.demodulateAsHexStr(src)
                if n is None:
                    break
                lprint("Preamble found.")
                # print("RX>",end="",flush=True)
                for i in n:
                    c=c+1
                    print(i,end="",flush=True)
                print()
                lprint("Signal lost.")
            lprint("End of stream.")
        elif args.file!=False:
            d=b""
            while True:
                c=0
                n=demod.demodulateAsBytes(src)
                if n is None:
                    break
                lprint("Preamble found.")
                for i in n:
                    c=c+1
                    d=d+i
                    print(".",end="",flush=True)
                print()
                lprint("Signal lost.")
            lprint("End of stream.")
            if len(d)>0:
                with open(args.file,"wb") as fp:
                    fp.write(d)
                lprint("File saved:%s"%(args.file))
        else:
            raise RuntimeError()
        lprint("Finihed.")
        return

class Tx(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('tx',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Transmit text or hex string or file to audio device as TBSK modulation.",
        epilog=
        "Example:\n"
        "  $tbskmodem tx\n"
        "    Send console input text to susi.wav with default parameter.\n"
        "  $tbskmodem tx --text yakitori\n"
        "    Send command line text\n"
        "  $tbskmodem tx --text tempura --carrier 48000\n"
        "    Send command line text with specified carrier frequency.\n"
        "  $tbskmodem tx --hex 00beef\n"
        "    Send command line hex string\n"
        "  $tbskmodem tx --file sabakan.txt\n"
        "    Send file contents in binary.\n",
        help='see `$tbskmodem mod -h`')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--device',type=int,default=None,help='Audio device id')
        parser_add.add_argument('--tone',type=str,default="xpsk:10,10",help=TEXT_RESOURCR["Argument_tone_help"])
        parser_add.add_argument('--silence',type=float,default=0.5,help='Silence padding time in sec')
        parser_add.add_argument('--volume',type=float,default="1.0",help='Volume multiplyer 0 to 1.0')
        parser_add.add_argument('--text',type=str,nargs="?" ,default=None,const="",help='Text format input.')
        parser_add.add_argument('--hex',type=str,nargs="?" ,default=None,const="",help='Hex string format input.')
        parser_add.add_argument('--file',type=str,nargs="?",default=None,help='File input')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):

        # print(args)
        tone=str2tone(args.tone,args.carrier).mul(max(0,min(1,args.volume)))    # SSFM DPSK
        mod=TbskModulator(tone)
        #入力値の判定
        numoffmt=3-[args.text,args.hex,args.file].count(None)
        if numoffmt>1:
            raise RuntimeError("Must be set text,hex,file parameter in exclusive.")
        src_pcm=None
        if numoffmt==0 or args.text is not None:
            src=inputstr("input string>") if numoffmt==0 or len(args.text)==0 else args.text
            lprint("Start Modulation.")
            src_pcm=[i for i in mod.modulate(src)]
        elif args.hex is not None:
            src=inputstr("input hex string>") if len(args.hex)==0 else args.hex
            lprint("Start Modulation.")
            src_pcm=[i for i in mod.modulateAsHexStr(src)]
        elif args.file is not None:
            lprint("Start Modulation.")
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
        lprint("Pcm format   : %dHz,%dbits,%dch,%.2fsec(silence:%.2fsec x 2)"%(pcm.frame_rate,pcm.sample_bits,1,pcm.timelen,args.silence))
        lprint("Tone         : '%s' %dticks,%.1fmsec/symbol"%(args.tone,len(tone),len(tone)/carrier*1000))
        lprint("Bit rate     : %.1fbps"%(carrier/len(tone)))
        lprint()
        lprint("Playing...")
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
        lprint("Finihed.")
        return


class Rx(BaseCommand):
    def __init__(self,subparsers:argparse.ArgumentParser):
        parser_add = subparsers.add_parser('rx',formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Receive TBSK siglan from audio device.",
        epilog=
        "Example:\n"
        "  $tbskmodem dem susi.wav\n"
        "    Receive TBSK signal with default parameter and print as text format.\n"        
        "  $tbskmodem dem tempura.wav --hex\n"
        "    Receive TBSK signal with default parameter and show as hex string format.\n"
        "  $tbskmodem dem tonkatu.wav --text --tone 100\n"
        "    Receive TBSK siginal with specified tone ticks and print as text format.\n"
        "  $tbskmodem dem yakitori.wav --file umai.txt\n"
        "    Receive TBSK siginal and save to file.\n",
        help='see `$tbskmodem dem -h`')
        parser_add.add_argument('--carrier',type=int,default=16000,help='Carrier frequency.')
        parser_add.add_argument('--sample_bits',type=int,choices=[8,16],default=16,help='Sampling bit width.')
        parser_add.add_argument('--device',type=int,default=None,help='Audio device id')
        parser_add.add_argument('--text',default=None,action='store_const',const=True,help='Show in text.')
        parser_add.add_argument('--hex',default=None,action='store_const',const=True,help='Show in hex string.')
        parser_add.add_argument('--file',default=None,nargs=1,help='Save to file as is.')
        parser_add.add_argument('--rpc',default=None,nargs=2,help='Connect to specified type rpc client by url. get|post url')
        parser_add.add_argument('--tone',default=None,help='Tone format or ticks.')
        parser_add.add_argument('--noinfo',action='store_true',help='Hide details other than results.')
        parser_add.add_argument('--norepeat',action='store_true',help='Do not repeat signal detection.')
        parser_add.set_defaults(handler=self)
        super().__init__(parser_add)

    def execute(self,args):
        # print(args)




        tone=str2tone2("100" if args.tone is None else args.tone)    # SSFM DPSK

        lprint("Audio source     : %dHz,%dbits,%dch deviceid:%s"%(args.carrier,args.sample_bits,1,str(args.device)))
        lprint("Tone             : %dticks,%.1fmsec/symbol"%(len(tone),len(tone)/args.carrier*1000))
        lprint("Bit rate         : %.1fbps"%(args.carrier/len(tone)))
        lprint()
        demod=TbskDemodulator(tone)
        lprint()
        lprint("Listening...")

        with SoundDeviceInputIterator(args.carrier,bits_par_sample=args.sample_bits,device_id=args.device) as isrc:

            flags=[args.text,args.hex,args.file,args.rpc]
            numoffmt=len(flags)-flags.count(None)
            if numoffmt>1:
                raise RuntimeError("Must be set text,hex,file parameter in exclusive.")
            if numoffmt==0 or args.text==True:
                while True:
                    c=0
                    n=demod.demodulateAsStr(isrc)
                    if n is None:
                        break
                    lprint("Preamble found.")
                    # print("RX>",end="",flush=True)
                    for i in n:
                        c=c+1
                        print(i,end="",flush=True)
                    print()
                    lprint("Signal lost.")
                    if args.norepeat:
                        break
                lprint("End of stream.")
            elif args.hex==True:
                while True:
                    c=0
                    n=demod.demodulateAsHexStr(isrc)
                    if n is None:
                        break
                    lprint("Preamble found.")
                    # print("RX>",end="",flush=True)
                    for i in n:
                        c=c+1
                        print(i,end="",flush=True)
                    print()
                    lprint("Signal lost.")
                    if args.norepeat:
                        break
                lprint("End of stream.")
            elif args.file is not None:
                d=b""
                try:
                    while True:
                        c=0                
                        n=demod.demodulateAsBytes(isrc)
                        if n is None:
                            break
                        lprint("Preamble found.")
                        for i in n:
                            c=c+1
                            d=d+i
                            print(".",end="",flush=True)
                        print()
                        lprint("Signal lost.")
                        if args.norepeat:
                            break
                        d=d+"\n"
                    lprint("End of stream.")
                finally:
                    if len(d)>0:
                        with open(args.file[0],"wb") as fp:
                            fp.write(d)
                        lprint("File saved:%s"%(args.file[0]))
            elif args.rpc!=False:
                lprint("Not Implements.")
                # #https://developer.bitcoin.org/reference/rpc/sendrawtransaction.html
                
                # class RpcClient():
                #     def sendRawTransaction(data:bytes):
                # # https://ethereum.org/ja/developers/docs/apis/json-rpc/

                # # btc:sendRawTransaction:
                # # eth:///
                # ...
            else:
                raise RuntimeError()
            return

def main():
    global is_local_library
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,prog="tbskmodem")
        sp=parser.add_subparsers()
        parser.add_argument('--version',"-V",action="store_true",help='print version')
        Modulate(sp)
        Demodulate(sp)
        Tx(sp)
        Rx(sp)
        args:argparse.Namespace = parser.parse_args()
        if args.version:
            print(("tbskmodem/"+__version__+";"+sys.version+";"+platform.platform()).replace("\n",""))
            print("""
TBSK modem -- Trait Block Shift Keying modulation/demodulation library.

Copyright (C) 2022, Ryo Iizuka, nyatla.jp.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.            
            """)
        elif hasattr(args, 'handler'):
            global lprint
            if "noinfo" in args and args.noinfo:
                lprint=(lambda *a,**k:())
            if is_local_library:
                lprint("[WARN] Imported local library.")
            if re.match(".*WSL.*",platform.release()) is not None:            
                lprint("[WARN] Executed on WSL platform. Audio device may not work properly.")
            if re.match(".*conda.*",sys.version) is not None:            
                lprint("[WARN] Executed by conda build. Ctrl^C may not work. Use Ctrl^D or Break(Ctrl^[PAUSE]) instead")


            args.handler.execute(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("KeyboardInterrupt.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        exit(-1)

if __name__ == "__main__":
    main()
