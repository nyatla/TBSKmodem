# TBSK modem

English document ð[Readme.en.md](Readme.en.md)

TBSK (Trait Block Shift Keying) modemã¯ãFFT/IFTTãä½¿ããªããä½éãç­è·é¢ã®é³é¿éä¿¡ã®å®è£ã§ãã
ãã¤ã/ãããã¹ããªã¼ã ã®æ¯å¹ä¿¡å·ã¸ã®å¤èª¿ãæ¯å¹ä¿¡å·ãããã¤ã/ãããã¹ããªã¼ã ã¸ã®å¾©èª¿ãã§ãã¾ãã

éçºç¨ã®ã©ã¤ãã©ãªã¨ãã³ã³ã½ã¼ã«ã¢ããª[tbskmodem](tbskmodem.md)ãããã¾ãã

![preview_tbsk](https://user-images.githubusercontent.com/2483108/194768184-cecddff0-1fa4-4df8-af3f-f16ed4ef1718.gif)

[Youtube](https://www.youtube.com/watch?v=4cB3hWATDUQ)ã§ã¿ãï¼ä¿¡å·é³ä»ãã§ããï¼


## æ§è½

éããªå®¤åã§ã®é³é¿éä¿¡æ§è½ã¯ããããã¬ã¼ãã5bpsï½1kbpsãéä¿¡è·é¢ã¯1mãããã§ãã
ãã½ã³ã³ã«åãããã¤ã¯ã¨ã¹ãã¼ã«ã¼ã§éä¿¡ãã§ãã¾ãã

ãã®ä»ã®åªä½ã§ãããããªãã«æ³¢å½¢ãä¼éã§ããã°éä¿¡ã§ããã¨æãã¾ãã


## ä»æ§

| ãã©ã¡ã¼ã¿ | å¤ |
| --- | --- |
| å¤èª¿æ¹å¼ | ç¹å¾´ãã­ãã¯å·®åå¤èª¿ |
| ãããã¬ã¼ã | 5ï½1kbps |
| æ¬éæ³¢å¨æ³¢æ° | ä»»æ |
| å¸¯åå¹ | 5Hzï½å¨å¸¯å |
| ã¨ã©ã¼è¨æ­£/æ¤åº | ãªã |

### ç¹å¾´ãã­ãã¯å·®åå¤èª¿

TBSKã®ç¹å¾´ãã­ãã¯å·®åå¤èª¿ã¯ãæ³¢å½¢ã·ã³ãã«ã®ä»£ããã«ä»»æå½¢ç¶ã®ãã¼ã³ä¿¡å·ã¨ãã®åè»¢å¤ãã2å¤ã®ä¼éã·ã³ãã«ã¨ãã¦ä½¿ãã¾ãã
ãã¼ã³ä¿¡å·ã¯ã¹ãã¯ãã©ã æ¡æ£ããSinæ³¢ãä½¿ãã¾ãããä»ã«ãä»»æå½¢ç¶ã®æ³¢å½¢ãä½¿ããã¨ãã§ãã¾ãã
å¾©èª¿ã¯ãé£æ¥ããã·ã³ãã«ã®ç¸é¢å¤ãéå»¶æ¤æ³¢ãã¾ããç¸é¢å¤ã¯1,-1ãåãã®ã§ãããããããã«å¾©èª¿ãã¾ãã

ãã®ä¼éæ¹å¼ã®ãã©ã¡ã¼ã¿ã¯ããã¼ã³ä¿¡å·é·(Tickæ°Ãæ¬éæ³¢å¨æ³¢æ°)ã®ã¿ã§ãããã¼ã³ä¿¡å·é·ã ãé©åãã¦ããã°ãåä¸ãªå¾©èª¿å¨ã§ä¿¡å·ã®å½¢å¼ã«ãããå¾©èª¿ãããã¨ãã§ãã¾ãã

### ä¿¡å·åæ

ä¿¡å·ã®æ¤åºã¯ç¸é¢å¤ãä¸å®æéè¦³æ¸¬ãã¦å¤å®ãã¾ããä¿¡å·ã®åç«¯ã«ã¯éå¸¸ã®ã·ã³ãã«ãããé·ãåæãã¿ã¼ã³ãéç½®ãã¾ãã
åæã®åæã·ã³ãã«æ¤ç¥ã®ã»ããåæãããè£æ­£ããããã«ã·ã³ãã«åè»¢æã®ç¸é¢ãã¼ã¯ãæ¤åºãã¾ãã
æ¬éæ³¢ã®å®å®ããªãã·ã¹ãã ã§ã·ã³ãã«1ã®ä¿¡å·ãé·æéãéãã¨ãåæãåããã«ã¹ããªã¼ã ãä¸­æ­ãã¾ãã
é·æéã®éä¿¡ã§ã¯ãæ°åç§ã«ä¸åº¦ã¯0ã®ã·ã³ãã«ãé£ç¶ãã¦éä¿¡ãããããã«ãã¼ã¿ãå å·¥ãã¦ãã ããã

### ãã¼ã³ä¿¡å·

æ¨æºã®ãã¼ã³ä¿¡å·ã¯ãSinæ³¢ãPNç¬¦å·ã§ä½ç¸ã·ããããã¹ãã¯ãã©ã æ¡æ£æ³¢å½¢ã§ãã
ãã¼ã³ä¿¡å·ã¯å¾©èª¿å´ã§S/Næ¯ãé«ããªãå½¢ç¶ã§ããã°ä½ã§ãæ§ãã¾ããããã¼ã³ä¿¡å·ã«ãµã¤ã³æ³¢ãä½¿ç¨ããã¨ãDPSKå¤èª¿ã¨åãåä½ããã¾ãã

### å¤ä¹±èæ§

ãã¼ã³ä¿¡å·ãé·ãã»ã©å¤ä¹±èæ§ã¯å¼·ããªãã¾ããããã¼ã³ä¿¡å·ãé·ããªãã»ã©ãããã¬ã¼ãã¯ä½ä¸ãã¾ãã
æ¬éæ³¢å¨æ³¢æ°ã«å¯¾ããæå¤§éä¿¡ã¬ã¼ãã®çè«å¤ã¯1bit/Hzã§ããå®éã«ã¯0.01bit/Hzãç®å®ã¨ãªãã¾ãã

ãã¼ã³ä¿¡å·ã¯ãç·è·¯åªä½ã®ç¹æ§ã«åããã¦ãæéæ¹åãå¨æ³¢æ°æ¹åã«æ¡æ£ï¼å¸¯åã®ç¡é§é£ãï¼ãã§ãã¾ãã


### ãã±ããä»æ§
ç¾ç¶ã®ãã­ãã³ã«ã¯ãéå§ç¹æ¤åºã¨ããã«ç¶ããã¤ã­ã¼ãèª­åºãã®ã¿ãå®è£ãã¦ãã¾ãããã±ãããµã¤ãºãçµç«¯è­å¥å­ãã¨ã©ã¼è¨æ­£ãæ¤åºã«ã¤ãã¦ã¯ã¢ããªã±ã¼ã·ã§ã³ã§å®è£ãã¦ãã ããã

## ã©ã¤ã»ã³ã¹

æ¬ã½ããã¦ã§ã¢ã¯ãMITã©ã¤ã»ã³ã¹ã§æä¾ãã¾ããããã¼ã»ç ç©¶ç¨éã§ã¯ãMITã©ã¤ã»ã³ã¹ã«å¾ã£ã¦é©åã«éç¨ãã¦ãã ããã
ç£æ¥­ç¨éã§ã¯ãç¹è¨±ã®åãæ±ãã«æ³¨æãã¦ãã ããã

ãã®ã©ã¤ãã©ãªã¯MITã©ã¤ã»ã³ã¹ã®ãªã¼ãã³ã½ã¼ã¹ã½ããã¦ã§ã¢ã§ãããç¹è¨±ããªã¼ã§ã¯ããã¾ããã

ç¹è¨±æ¨©ã«ã¤ãã¦ã¯ãYAMAHA CORPORATIONæ§ã®ææããä»¥ä¸ã®ç¹è¨±ãåã³æ´¾çåç¹è¨±å¨è¾ºã«é¡ä¼¼ããç®æãããæ§ã«æããã¾ãã
å°éå®¶ã®ç£ä¿®ã¯åãã¦ããã¾ããã®ã§ãè©³ç´°ã¯ãèªèº«ã§ãèª¿ã¹ãã ããã

[ç¹è¨±æå ±ãã©ãããã©ã¼ã ](https://www.j-platpat.inpit.go.jp/)

[å¤èª¿è£ç½®åã³å¾©èª¿è£ç½® WO-A-2010/016589](https://www.j-platpat.inpit.go.jp/c1800/PU/WO-A-2010-016589/7847773A7250230D1C8D66BBF506D4E794BEF7F38B5DF2B8C11BE9225DF7BB10/50/ja)


## GetStarted

Anacondaã®å©ç¨ãåæã¨ãã¦èª¬æãã¾ããPythonã®ãã¼ã¸ã§ã³ã¯ãPython 3.10.xãæ¨å¥¨ãã¾ãã

ã»ããã¢ãããæåããã¨ãã³ãã³ãã©ã¤ã³ãã¼ã«ã®[tbskmodem](./tbskmodem.md)ãåæã«ã¤ã³ã¹ãã¼ã«ããã¾ãã


#### Anacondaã§ã®ã»ããã¢ãã
ã½ã¼ã¹ã³ã¼ããgithubããcloneãã¾ãã

```
>git clone https://github.com/nyatla/TBSKmodem.git
```

step4ã¾ã§ã¯å¤é¨ã¢ã¸ã¥ã¼ã«ã¯ä¸è¦ã§ãã

step4ããåã«é²ããªãã°ãnumpy,sounddeviceãã¤ã³ã¹ãã¼ã«ãã¦ãã ããã
ãµã¦ã³ãã®åçãã­ã£ããã£ã«å¿è¦ã§ãã
```
>conda install -c anaconda numpy
>conda install -c conda-forge python-sounddevice
```

#### pipããã®ã»ããã¢ãã

Linuxç°å¢ã®pipã§ã»ããã¢ããããå ´åã¯portaudioãå¿è¦ã«ãªãã¾ãã

```
$sudo apt-get install portaudio19-dev
$pip install tbskmodem
```
portaudioãã»ããã¢ããã§ããã°Windowsä¸ã§ãå©ç¨ã§ããã¯ãã§ãã




### ãµã³ãã«ãã­ã°ã©ã ã®å ´æ

ãµã³ãã«ãã­ã°ã©ã ã¯TBSKmodem/getstartedãã£ã¬ã¯ããªã«ããã¾ãã
```
> cd getstarted
```

#### step1. ãã¼ã¿ãwaveãã¡ã¤ã«ã«å¤æ
step1.modulate.pyã¯ããããå¤ãå¤èª¿ãããã¨ãã§ãã¾ãã

```
> python step1_modulate.py
Imported local library.
[WARN] Imported local library.
>
```
ãã®ã¹ã¯ãªããã¯å¤èª¿ããæ¯å¹ä¿¡å·ãwavãã¡ã¤ã«ã«ä¿å­ãã¾ãã
åºåãã¡ã¤ã«åã¯ãstep1.wavã§ãã

`[WARN] Imported local library.`ã¨è¡¨ç¤ºããã¾ãããï¼å¿éã¯ä¸è¦ã§ãã
ãã®è¡¨ç¤ºã¯ãã©ã¤ãã©ãªã§ã¯ãªããã­ã¼ã«ã«ãã£ã¬ã¯ããªã«ããtbskmodemããã±ã¼ã¸ããªã³ã¯ããæã«è¡¨ç¤ºãããã¡ãã»ã¼ã¸ã§ãã

ã¡ã¤ã³é¢æ°ãè¦ã¦ã¿ã¾ãããã
```
def main():
    # tone=SinTone(10,10).mul(0.5)      # DPSK
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload=[0,1,0,1,0,1,0,1]*16 # 16byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    src_pcm=[i for i in mod.modulateAsBit(payload)]

    #save to wave
    with open("step1.wav","wb") as fp:
        PcmData.dump(PcmData(src_pcm,16,carrier),fp)
```

ãã®ã¹ã¯ãªããã¯ãã¾ãä¼éã·ã³ãã«ã«ç¸å½ããXPskSinToneãªãã¸ã§ã¯ããçæãã¾ãã
æ¬¡ã«ãå¤èª¿å¨ã®TbskModulatorãªãã¸ã§ã¯ããçæãã¦ãmodulateAsBité¢æ°ã§å¤èª¿ãã¾ãã
å¤èª¿ããã®ã¯ãããå¤(1 or 0)ã®éåã§ãåè¨8*16=128ãããã§ãã

modulateAsBité¢æ°ã®æ»ãå¤ã¯ãå¤èª¿ããæ¯å¹å¤(float)ãè¿ãã¤ãã¬ã¼ã¿ã§ããããããªã¹ãã«ãã¦ãæå¾ã«Waveãã¡ã¤ã«ã«ãã¦ä¿å­ãã¾ãã

#### step2. wavãã¡ã¤ã«ããå¾©èª¿

step2.modulate.pyã¯ãä½æããwavãã¡ã¤ã«ãåã®ãããåã«æ»ãã¾ãã
```
> python step2_demodulate.py
[WARN] Imported local library.
[0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
>
```
å½ç¶ã®ããã«ãåã®ãããåã«æ»ãã¯ãã§ãã

ã¡ã¤ã³é¢æ°ãè¦ã¦ã¿ã¾ãããã
```
def main():
    wav=None
    with open("step1.wav","rb") as fp:
        wav=PcmData.load(fp)

    # tone=SinTone(20,8)
    tone=XPskSinTone(10,10)
    demod=TbskDemodulator(tone)

    ret=demod.demodulateAsBit(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)
```
ä¿¡å·ãæ ¼ç´ããWaveãã¡ã¤ã«ã¯step1ã§ä½æããstep1.wavã§ãããããèª­ã¿åºãã¾ãã
æ¬¡ã«ãã¼ã³ä¿¡å·ãä½ããããããå¾©èª¿å¨ã®TbskDemodulatorãä½ããdemodulateAsBité¢æ°ã§å¾©èª¿ãã¾ãã

demodulateAsBité¢æ°ã¯ãããåãintã§è¿ãã¤ãã¬ã¼ã¿ã§ããããããªã¹ãã«ãã¦è¡¨ç¤ºãã¾ãã


ã¤ãã¬ã¼ã¿ã¯ä¿¡å·ãæç«ããªããªãã¾ã§å¤ããããå¤ãè¿ãç¶ãã¾ãã(ä¿¡å·çµç«¯ã«ã¤ãã¦ã®çåã¯ããã§ã¯ä¸æ¦å¿ãã¾ãã)


#### step3. ãã¤ããã¼ã¿ã®å¤èª¿ã¨å¾©èª¿

ãã¤ãå¤ãéåä¿¡ããé¢æ°ãå½ç¶å®è£æ¸ã¿ã§ãã
step3_bytedata.pyã¯ãbyteså¤ã®å¤èª¿ã¨å¾©èª¿ãå®è¡ãã¾ãã

```
> python .\step3_bytedata.py
[WARN] Imported local library.
[b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']
> 
```

ã¡ã¤ã³é¢æ°ãè¦ã¦ã¿ã¾ãããã

```
def main():
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload=b"0123456789" # 10byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    src_pcm=[i for i in mod.modulate(payload)]

    #save to wave
    wav=PcmData(src_pcm,16,carrier)
    with open("step3.wav","wb") as fp:
        PcmData.dump(wav,fp)

    #demodulate to bytes
    demod=TbskDemodulator(tone)
    ret=demod.demodulateAsBytes(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)
```

step1ã¨step2ãåä½ãããããªæ§é ã§ãã
mod.modulateé¢æ°ã«æ³¨ç®ãã¦ãã ãããããã§ãpayloadã«bytesããã®ã¾ã¾æ¸¡ãã¦ãã¾ãã
ããã¦ãdemod.demodulateAsBytesã«ãæ³¨ç®ãã¦ãã ããããã¼ã¿ãæ¸¡ãã¨ãBytesã«ãã¦è¿ãã¦ãããããªé¢æ°ã§ãã

å¥åã¯é£ç¶ããbyteså¤ãªã®ã«æ»ãå¤ã1byteåä½ã®bytesåãªã®ã¯ä¸èªç¶ãªæ°ããã¾ããããããããã®ã§ãã

#### step4. æå­åã®å¤èª¿ã¨å¾©èª¿

step4_text.pyã¯ãæå­åã®å¤èª¿ã¨å¾©èª¿ãå®è¡ãã¾ãã

```
> python .\step4_text.py    
[WARN] Imported local library.
['ã¢', 'ã³', 'ã¿', 'ã¤', 'ã«', 'ã¼', 'ã', 'ã£']
>
```
ã¡ã¤ã³é¢æ°ãè¦ã¦ã¿ã¾ããããstep3ã¨ã»ã¨ãã©å¤ããã¾ããã

```
def main():
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload="ã¢ã³ã¿ã¤ã«ã¼ãã£" # 8byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    wav=PcmData([i for i in mod.modulate(payload)],16,carrier)
    #save to wave
    with open("step4.wav","wb") as fp:
        PcmData.dump(wav,fp)

    #demodulate to bytes
    demod=TbskDemodulator(tone)
    ret=demod.demodulateAsStr(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)
```
å¤èª¿é¨åã¯mod.modulateãã®ã¾ã¾ã§ãã
é¢æ°å¼ã³åºãã®å¤æ´ç¹ã¯ãå¾©èª¿é¨åã§demodulateAsStré¢æ°ãä½¿ããã¦ããã¨ããã§ãã

å¤èª¿å¨ã¨å¾©èª¿å¨ã¯ããããããbitéå,æå­å,Hex string,bytes,uint8éåãå¼æ°ã«åãé¢æ°ãããã¾ãã
åã®è¯ãèª­èã®æ¹ã¯æ°ãä»ããããããã¾ããããHex stringã¯ãã­ãã¯ãã§ã¼ã³ãããã¯ã¼ã¯ã®ãã©ã³ã¶ã¯ã·ã§ã³ãéä¿¡ããããã®æ©è½ã§ããð§±â


#### step5. ãã¤ã¯å¥åã®ãã¹ã

step5_microphone.pyã§ããµã¦ã³ãããã¤ã¹ãpythonããã¢ã¯ã»ã¹ã§ããããã¹ããã¾ãããã

æ³¨æ:WSLãVirtualBoxãªã©ã®ä»®æ³ã·ã¹ãã ã§ã¯ããµã¦ã³ãããã¤ã¹ã«ãã¤ãºãæ··ãããããéä¿¡ãæç«ããªããã¨ãããã¾ãã

```
> python .\step5_microphone.py
[WARN] Imported local library.
Press [ENTER] to stop.
Volume meter
###
```

ãã¤ã¯ã«åãã£ã¦ä¸æ²æ«é²ãã¦ãã ãããé¸æ²ã¯ãä»»ããã¾ãã
"#"ã§ç¤ºããããã¼ã°ã©ããåãã¦ããã°ãpythonã¯æ­£å¸¸ã«ãã¤ã¯ãèªè­ãã¦ãã¾ãã

ãã¾ãèªè­ã§ããªãå ´åã¯æ¬¡ã®äºãè©¦ãã¦ãã ããã

1. ãã¤ã¯ãPCã«æ¥ç¶ããã¦ãããç¢ºèªããã
2. ã¹ã¯ãªããã®device_idãã©ã¡ã¼ã¿ãå¤æ´ãã(1,2,3...)
3. ä»ã®ãã­ã°ã©ã ã§ãã¤ã¯ãèªè­ãã¦ãããç¢ºèªããã
4. ãã£ã¨å¤§ããªå£°ã§æ­ãã

æ­ãçµãã£ãããENTERã§ãã­ã°ã©ã ãåæ­¢ãã¾ãã


#### step6. ãªã¢ã«ã¿ã¤ã éåä¿¡

ä»ä¸ãã«ãstep6_realtime_receive.pyã§ãªã¢ã«ã¿ã¤ã ã«ä¿¡å·ãå¾©èª¿ãã¾ãã
ãã¤ã¯ã®æºåã¯å®ããã§ããï¼

æ³¨æ:WSLãVirtualBoxãªã©ã®ä»®æ³ã·ã¹ãã ã§ã¯ããµã¦ã³ãããã¤ã¹ã«ãã¤ãºãæ··ãããããéä¿¡ãæç«ããªããã¨ãããã¾ãã

```
> python .\step6_realtime_receive.py
[WARN] Imported local library.
160.0 bps
Play step6.wave in your player.
Start capturing
>ã¢ã³ã¿ã¤ã«ã¼ãã£
End of signal.
>
```

å®è¡ãããã£ã¬ã¯ããªã«ãstep6.wavãçæããã¦ãã¾ãã
ãã®Waveãã¡ã¤ã«ãpythonã«èããã¦ãã ããã
å¾©èª¿ããæå­åãè¡¨ç¤ºããã¾ãã

ã¨ããã§ãåä¿¡ããä¿¡å·ã®çµç«¯ã¯ã©ããªã®ãï¼ã¨ããçåãæ®ãããã¾ã¾ã§ãã
TBSKã§ã¯ãä¿¡å·ãæ¤ç¥ããå¾ãä¿¡å·å¼·åº¦ãé¾å¤ãè¶ãã¦ããã°ããããä½ã§ãã£ã¦ãå»¶ãã¨å¤ãå¾©èª¿ãç¶ãã¾ãã
ä¸ä½ã®éä¿¡ä»æ§ã§ãã±ããé·ãåºå®ããããé·ããã©ã¡ã¼ã¿ãåãã«éä¿¡ãããªã©ãã¦å¯¾å¦ãã¦ãã ããã


ãã¥ã¼ããªã¢ã«ã¯ããã¾ã§ã§ãã[ã¢ã³ã¿ã¤ã«ã¼ãã£](http://wiki.ffo.jp/html/2682.html)






## ðTo Be Continued â²â¼â²

ãã¦ãæ¥é±(æ¥å¹´)ã®ç®æ¨ã¯ã

1. Unityã§åããã¦ã¿ããã
2. ãã©ã¦ã¶ã§ãåããã¦ã¿ããã
3. ãã¤ã­ã¼ãã®ç§å¿åã¨ã¨ã©ã¼è¨æ­£

ã®ï¼æ¬ã§ãã

