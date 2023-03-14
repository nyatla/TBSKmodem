# TBSK modem

Japanese document 👉[Readme.md](Readme.md)

TBSK (Trait Block Shift Keying) modem is a low-speed, short-range audio communication implementation without FFT/IFTT.

It can modulate a byte/bitstream to PCM  and demodulate PCM to a byte/bitstream.

There is a library for development and a console script [tbskmodem](tbskmodem.md).

![preview_tbsk](https://user-images.githubusercontent.com/2483108/194768184-cecddff0-1fa4-4df8-af3f-f16ed4ef1718.gif)

See [Youtube](https://www.youtube.com/watch?v=4cB3hWATDUQ) with modulated sound.🎵

## For other platforms.
- TBSKmodem for Python
- [TBSKmodem for C#](https://github.com/nyatla/TBSKmodemCS)
- [TBSKmodem for C++](https://github.com/nyatla/TBSKmodemCpp)
- [TBSKmodem for JavaScript](https://github.com/nyatla/TBSKmodemJS)
- [TBSKmodem for Java](https://github.com/nyatla/TBSKmodemJava)
- [TBSKmodem for Processing](https://github.com/nyatla/TBSKmodem-for-Processing)
- [TBSKmodem for MicroChip](https://github.com/nyatla/TBSKmodemMicro)



## Performance

Throughput in a quiet room is 5 bps to 1 kbps and transmit distance is about 1 meter.
It is possible with the microphone and speakers provided in a personal computer.


## Specification

| Parameters |  |
| --- | --- |
| Modulation method | Trait block differential modulation |
| Bit rate | 5 - 1kbps |
| Carrier frequency | Any |
| Bandwidths | 5Hz -  |
| Error correction/detection | No |

### Trait block differential modulation

Trait block differential modulation uses an any shaped tone signal and its inverted value as a binary transmission symbol instead of a waveform symbol.
The tone signal is a spread-spectrum Sin wave, but other shaped waveforms can be used.
Demodulation is performed by delay detection of the correlation rate of adjacent symbols. The correlation rate indicates  1,-1, which is demodulated into bits.

This modulatlation method has the only one parameter that is tone signal length (number of ticks x carrier frequency). The demodulator can demodulate any type of signal as long as the tone signal length is compatible.

### Signal Synchronization

First signal detection is determined by observing the correlation value for a certain period of time. A first synchronization pattern longer than a normal symbol, it is placed at the head of the signal.
And to maintain the state of synchronization, demodulator  uses the edge of the symbol in the signal  to detect the peak of the correlation.

If a signal is sent with symbols not inverted for a long time in an unstable carrier wave system, the transaction will be interrupted by lack of synchronization.
Should be good to process the data to be transmitted so that the data is inverted once every few seconds.

### Tone Signal

Default tone signal is a spread spectrum waveform with a sine wave phase-shifted by a PN code.
The tone signal can be any shape that is a high signal-to-noise ratio on the demodulation side. If the tone signal is sine, it behaves the same as DPSK modulation.

### Disturbance Tolerance

Disturbance tolerance becomes stronger the longer the tone signal, but lower the bit rate if longer the tone signal, 
The communication rate relative to the carrier frequency is 0.01 bit/Hz is the realstic.


### Packet format
The current protocol only implements signal detection and followed payload reading. Applications should implement packet size, termination identifier, error correction, and detection.

## License

This software is provided under the MIT license. For hobby and research purposes, use it according to the MIT license.

For industrial applications, be careful with patents.

This library is MIT licensed open source software, but not patent free.

Regarding patent rights, it seems that some of the rights owned by YAMAHA CORPORATION.
It is not supervised by experts, so check the details yourself.

[j-platpat](https://www.j-platpat.inpit.go.jp/)

[MODULATION DEVICE AND DEMODULATION DEVICE WO-A-2010/016589](https://www.j-platpat.inpit.go.jp/c1800/PU/WO-A-2010-016589/7847773A7250230D1C8D66BBF506D4E794BEF7F38B5DF2B8C11BE9225DF7BB10/50/ja)



## GetStarted

The explanation assumes the Anaconda environment.
Python 3.10.x is recommended.

The command line tool [tbskmodem](./tbskmodem.md) will be installed at the same time.

#### Setup for Anaconda
Clone the sorce code from github.

```
>git clone https://github.com/nyatla/TBSKmodem.git
```

Until step4, no external module is required .
If you go beyond step4, install numpy and sounddevice.
It is required for sound playback and capture.

```
>conda install -c anaconda numpy
>conda install -c conda-forge python-sounddevice
```
#### Setup by pip

```
$pip install tbskmodem
$sudo apt-get install portaudio19-dev
```

TBSKmodem requires portaudio library.

### Location of sample scripts

Sample programs are in the TBSKmodem/getstarted directory.
```
> cd getstarted
```

#### step1. Modulate to wave file.
step1.modulate.py moduletes bits to wave file.

```
> python step1_modulate.py
Imported local library.
[WARN] Imported local library.
>
```
This script modulates bits and save result to step1.wav.

`[WARN] Imported local library.` is displayed? Do not warry, This means library is linked from local diractory, not python package.


See main function.
```
def main():
    tone=TbskTone.createXPskSin(10,10).mul(0.5)    # SSFM DPSK
    payload=[0,1,0,1,0,1,0,1]*16 # 16byte
    carrier=8000

    #modulation
    mod=TbskModulator(tone)
    src_pcm=[i for i in mod.modulateAsBit(payload)]

    #save to wave
    with open("step1.wav","wb") as fp:
        PcmData.dump(PcmData(src_pcm,16,carrier),fp)
```

First, this script creates TraitTone objects that use to transmission symbols.
Next, create a modulator TbskModulator object and modulate it with the modulateAsBit function.
Modulating source is an array of bit values (1 or 0), totaling 8*16=128 bits.

The return value of the modulateAsBit function is an iterator that return the modulated amplitude values (float). Make list from it  and save it as a Wave file at the end.

#### step2. Demodulate from wav file.

step2.modulate.py demodulates wav file to bits.

```
> python step2_demodulate.py
[WARN] Imported local library.
[0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
>
```
It is decodes to the original bits.

See main function.
```
def main():
    wav=None
    with open("step1.wav","rb") as fp:
        wav=PcmData.load(fp)

    tone=TbskTone.createXPskSin(10,10)
    demod=TbskDemodulator(tone)

    ret=demod.demodulateAsBit(wav.dataAsFloat())
    print([i for i in ret] if ret is not None else None)
```

First, open and read  step1.wav.
Next, create a tone signal, create a TbskDemodulator demodulator  with it, demodulate it with the demodulateAsBit function.

The demodulateAsBit function returns an iterator that returns bit strings as ints.
Final, display this as a list.

The iterator continues returning bit values until the signal is no longer true. 
(Forget the question about signal termination for now.)

#### step3. Modulate and demodulate byte data.

Of course Functions for sending and receiving byte values are already exist.
step3_bytedata.py performs modulation and demodulation of bytes values.


```
> python .\step3_bytedata.py
[WARN] Imported local library.
[b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']
> 
```

See main function.
```
def main():
    tone=TbskTone.createXPskSin(10,10).mul(0.5)    # SSFM DPSK
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

The structure seems to combines step1 and step2.
Notice the mod.modulate function. This, it sets bytes to payload as is.
Also notice demod.demodulateAsBytes. It is a function that seems to return it as Bytes.


#### step4. Modulate and demodulate text.

step4_text.py modulates and demodulate text as UTF-8.

```
> python .\step4_text.py    
[WARN] Imported local library.
['ア', 'ン', 'タ', 'ヤ', 'ル', 'ー', 'ニ', 'ャ']
>
```

See main function.
```
def main():
    tone=TbskTone.createXPskSin(10,10).mul(0.5)    # SSFM DPSK
    payload="アンタヤルーニャ"
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

Modulation part is mod.modulate as it is.
The changes is the demodulateAsStr function call in the demodulation part.

The modulator and demodulator each have override functions that take bit arrays, strings, hex strings, bytes, and uint8 arrays arguments.

As an astute you may have noticed, hex strings are a function for sending transactions on blockchain networks.🧱⛓



#### step5. Testing microphone

For receiving signal needs microphone device.
Check the sound device is accessible from python with step5_microphone.py.

Note: In virtual systems such as WSL, VirtualBox, etc., audio communication may not be established due to noise in the sound device.

```
> python .\step5_microphone.py
[WARN] Imported local library.
Press [ENTER] to stop.
Volume meter
###
```

Please sing a your best song selection into the microphone.

If the bar graph indicated by "#" is moving, python recognizes the microphone normally.

Do not working? This is troubleshoot.

1. Check connection of microphone to your computer.
2. Change device_id parametor to any value(1,2,3...)
3. Check other programs can connect microphone on same PC.
4. Sing louder 

When finished singing, press ENTER to stop the program.


#### step6. Realtime demodulation.

This is the final step. Demodulate the signal in real time with step6_realtime_receive.py.
Are you ready for the microphone?


Note: In virtual systems such as WSL, VirtualBox, etc., audio communication may not be established due to noise in the sound device.

```
> python .\step6_realtime_receive.py
[WARN] Imported local library.
160.0 bps
Play step6.wave in your player.
Start capturing
>アンタヤルーニャ
End of signal.
>
```

step6.wav is generated in the executed directory.
Let make listen to this wave file to python.
A demodulated string is displayed.

By the way, The question remains. Where is the termination of the received signal? 

In TBSK, after detecting a signal, it endlessly demodulates whatever the signal strength is above the threshold.
Fix the packet length in the upper communication specification or send the length parameter first.


Congratulations! You are now a TBSK Master! [アンタヤルーニャ](http://wiki.ffo.jp/html/2682.html)




