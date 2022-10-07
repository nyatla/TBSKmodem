# tbskmodem

tbskmodemの機能を一通り試用するためのスクリプトです。
PyPIからインストールできます。

```
pip install tbskmodem
```

ソースコードは、[tbskmodem_apps/_tbskmodem.py](https://github.com/nyatla/TBSKmodem/tbskmodem_apps/_tbskmodem.py)です。


### 機能

以下の機能があります。

1. 文字列、Hex string、ファイルをTBSK変調して、Wavファイルに変換する。
2. WAVファイルを復調して文字列、Hex stringを表示する、保存する。
3. 文字列、Hex string、ファイルをTBSK変調してオーディオデバイスに出力する。
4. オーディオデバイスから音声を取り込んで文字列、Hex string、ファイルを復調する。

### 文字列、Hex string、ファイルをTBSK変調して、Wavファイルに変換する。

Wavファイルへの変換は、modサブコマンドを使います。
```
$ tbskmodem mod delicious.wav --text からあげうまい
Output file       : delicious.wav  16000Hz,16bits,1ch,2.14sec(silence:0.50sec x 2)
Tone              : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate          : 160.0bps
```

このコマンドは、文字列をutf-8でバイナリ値にエンコードして、変調したWaveファイルを出力します。

コマンドラインオプションの説明は、--helpオプションで表示できます。

```
$ tbskmodem mod --help
usage: tbskmodem mod [-h] [--carrier CARRIER] [--sample_bits {8,16}] [--tone TONE] [--silence SILENCE] [--text [TEXT]]
                     [--hex [HEX]] [--file FILE]
                     out

Moduleate text or hextext or binary to wavefile.

positional arguments:
  out                   Output wave file name.

optional arguments:
  -h, --help            show this help message and exit
  --carrier CARRIER     Carrier frequency.
  --sample_bits {8,16}  Sampling bit width.
  --tone TONE           Trait tone format."xpsk:int,int(,int)" | "sin:int,int"
  --silence SILENCE     Silence padding time in sec
  --text [TEXT]         Text format input.
  --hex [HEX]           Hex text format input.
  --file FILE           File input

Example:
  $tbskmodem mod susi.wav
    Modulate console input text to susi.wav with default parameter.
  $tbskmodem mod yakitori.wav --text yakitori
    Modulate command line text to tempura.wav
  $tbskmodem mod tempura.wav --text tempura --carrier 48000
    Modulate command line text to tempura.wav with specified carrier frequency.
  $tbskmodem mod beef.wav --hex 00beef
    Modulate command line hex string to beef.wav as binary.
  $tbskmodem mod sabakan.wav --file sabakan.txt
    Modulate file contents to sabakan.wav in binary.
```

--textの代わりに--hexを使うと、文字列をhex stringとして解釈します。

```
$ tbskmodem mod delicious.wav --hex 79616b69746f7269756d6169
Output file       : delicious.wav  16000Hz,16bits,1ch,1.69sec(silence:0.50sec x 2)
Tone              : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate          : 160.0bps
```

--fileを使うと、引数のファイルの内容をバイナリ値として変調します。

```
$ tbskmodem mod licence.wav --file ./LICENSE
Output file       : licence.wav  16000Hz,16bits,1ch,59.14sec(silence:0.50sec x 2)
Tone              : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate          : 160.0bps
```

--textと--hexで値引数を省略すると、入力を求められます。

その他のパラメータは変調パラメータです。--carrierは搬送波周波数,--toneはシンボルトーンのパラメータです。


### Wavファイルを復調して文字列、Hex stringを表示する、保存する。

Waveファイルからの変換は、demサブコマンドを使います。先ほど作ったdelicious.wavからメッセージを復調します。

このコマンドは、復調したビット値をutf-8でデコードして結果を返します。
```
$ tbskmodem dem delicious.wav --text
[WARN] Executed on WSL platform. Audio device may not work properly.
Input file       : delicious.wav  16000Hz,16bits,1ch,2.14sec
Tone             : 100ticks,6.2msec/symbol
Bit rate         : 160.0bps

Start detection.
Preamble found.
からあげうまい
End of signal.
```


--texeの代わりに--hexを使うと、復調したビット値をhexstrで表示します。

```
$ tbskmodem dem delicious.wav --hex
Input file       : delicious.wav  16000Hz,16bits,1ch,2.14sec
Tone             : 100ticks,6.2msec/symbol
Bit rate         : 160.0bps

Start detection.
Preamble found.
e3818be38289e38182e38192e38186e381bee38184
End of signal.
End of stream.
```

--fileを使うと、値引数で指定したファイルにバイナリ値をそのまま書き込みます。



### 文字列、Hex string、ファイルをTBSK変調してオーディオデバイスに出力する。

txサブコマンドは、変調した信号を直接オーディオデバイスに出力します。

結構な音量なので注意してください。

```
$ tbskmodem tx --text 今川焼？大判焼き？回転焼き？
Pcm format       : 16000Hz,16bits,1ch,3.19sec(silence:0.50sec x 2)
Tone             : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate         : 160.0bps
playing...
16000
100%|█████████████████████████████████████████████████████████████████
```
--text,--hex,--file引数はmodサブコマンドと同じです。

オーディオデバイスに接続できない場合は--deviceパラメータでオーディオデバイスのIDを変更してみてください。
番号は気合で探します。

### オーディオデバイスから音声を取り込んで文字列、Hex string、ファイルを復調する。


rxサブコマンドは、信号をオーディオデバイスから取り込んで内容を表示、保存します。

