# tbskmodem

tbskmodemの機能を一通り試用するためのスクリプトです。
PyPIからインストールできます。

```
pip install tbskmodem
```

githubからインストールする場合は、次のようにします。

```
$ git clone https://github.com/nyatla/TBSKmodem.git
$ cd TBSKmodem
$ pip install .
```


ソースコードは、[tbskmodem_apps/_tbskmodem.py](https://github.com/nyatla/TBSKmodem/tbskmodem_apps/_tbskmodem.py)です。


## 機能

以下の機能があります。

1. 文字列、Hex string、ファイルをTBSK変調して、Wavファイルに変換する。
2. WAVファイルを復調して文字列、Hex stringを表示する、保存する。
3. 文字列、Hex string、ファイルをTBSK変調してオーディオデバイスに出力する。
4. オーディオデバイスから音声を取り込んで文字列、Hex string、ファイルを復調する。

### 文字列、Hex string、ファイルをTBSK変調して、Wavファイルに変換する。

Wavファイルへの変換は、modサブコマンドを使います。
```
$ tbskmodem mod delicious.wav --text からあげうまい
Start Modulation.
Modulated.
Output file : delicious.wav  16000Hz,16bits,1ch,2.14sec(silence:0.50sec x 2)
Tone        : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate    : 160.0bps

Finihed.
```

このコマンドは、文字列をutf-8でバイナリ値にエンコードして、変調したWaveファイルを出力します。

コマンドラインオプションの説明は、--helpオプションで表示できます。

```
$ tbskmodem mod --help
usage: tbskmodem mod [-h] [--carrier CARRIER] [--sample_bits {8,16}] [--tone TONE] [--silence SILENCE] [--text [TEXT]]
                     [--hex [HEX]] [--file FILE]
                     out

Moduleate text or hex string or binary to wavefile.

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
このオプションは、ブロックチェーンのトランザクションを変調するときに役立ちます。

```
$ tbskmodem mod delicious.wav --hex 79616b69746f7269756d6169
Start Modulation.
Modulated.
Output file : delicious.wav  16000Hz,16bits,1ch,1.69sec(silence:0.50sec x 2)
Tone        : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate    : 160.0bps

Finihed.
```

--fileを使うと、引数のファイルの内容をバイナリ値として変調します。

```
$ tbskmodem mod licence.wav --file ./LICENSE
Start Modulation.
Modulated.
Output file : licence.wav  16000Hz,16bits,1ch,59.14sec(silence:0.50sec x 2)
Tone        : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate    : 160.0bps

Finihed.
```

--textと--hexで値引数を省略すると、入力を求められます。

その他のパラメータは変調パラメータです。--carrierは搬送波周波数,--toneはシンボルトーンのパラメータです。


### Wavファイルを復調して文字列、Hex stringを表示する、保存する。

Waveファイルからの変換は、demサブコマンドを使います。先ほど作ったdelicious.wavからメッセージを復調します。

このコマンドは、復調したビット値をutf-8でデコードして結果を返します。
```
$ $ tbskmodem dem delicious.wav --text
Input file  : delicious.wav  16000Hz,16bits,1ch,1.69sec
Tone        : 100ticks,6.2msec/symbol
Bit rate    : 160.0bps

Start Demodulation.
Preamble found.
yakitoriumai
Signal lost.
End of stream.
Finihed.
```


--texeの代わりに--hexを使うと、復調したビット値をhexstrで表示します。
このオプションは、ブロックチェーンのトランザクションを復調するときに役立ちます。

```
$ tbskmodem dem delicious.wav --hex
Input file  : delicious.wav  16000Hz,16bits,1ch,1.69sec
Tone        : 100ticks,6.2msec/symbol
Bit rate    : 160.0bps

Start Demodulation.
Preamble found.
79616b69746f7269756d6169
Signal lost.
End of stream.
Finihed.
```

--fileを使うと、値引数で指定したファイルにバイナリ値をそのまま書き込みます。



### 文字列、Hex string、ファイルをTBSK変調してオーディオデバイスに出力する。

txサブコマンドは、変調した信号を直接オーディオデバイスに出力します。

結構な音量なので注意してください。

```
$ tbskmodem tx --text 今川焼？大判焼き？回転焼き？
[WARN] Executed on WSL platform. Audio device may not work properly.
Start Modulation.
Pcm format   : 16000Hz,16bits,1ch,3.19sec(silence:0.50sec x 2)
Tone         : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate     : 160.0bps
playing...
16000
100%|████████████████████████████████████████████████████████████████████████
Finihed.
```
--text,--hex,--file引数はmodサブコマンドと同じです。

オーディオデバイスに接続できない場合は--deviceパラメータでオーディオデバイスのIDを変更してみてください。
番号は気合で探す必要があります。

--volumeオプションで音量を調整することができます。



### オーディオデバイスから音声を取り込んで文字列、Hex string、ファイルを復調する。


rxサブコマンドは、信号をオーディオデバイスから取り込んで内容を表示、保存します。

```
$ tbskmodem rx --text
Audio source     : 16000Hz,16bits,1ch deviceid:None
Tone             : 100ticks,6.2msec/symbol
Bit rate         : 160.0bps

Start detection.
Preamble found.
TBSK modem -- Trait Block Shift Keying modulation/demodulation library.
Signal lost.
```

スクリプトが待機状態になったら、別の端末、もしくは別のターミナルから信号を送信します。
```
$python ./_tbskmodem.py tx --text "TBSK modem -- Trait Block Shift Keying modulation/demodulation library."
```

スクリプトは延々とシグナルの検出を続けます。終了するにはCtrl^Cか、Ctrl^[PAUSE]を入力します。

--norepeatオプションを指定すると、１つだけ信号を検出して終了します。



## パラメータの詳細

### トーン信号の変更 (--tone)

rxとmodサブコマンドでは、--toneオプションで変調に使うトーンを変更できます。

トーン信号にはプリセットの4種類と、ユーザー定義値があります。

#### プリセット値


`--tone sin:points,cycle`

このトーン値は、単純なSin波です。
Sin波一周期をサンプル数pointsで生成し、それをcycle回繰り返します。

`--tone xpsk:points,cycle(,shift)`

このトーン値は、位相シフトスペクトラム拡散Sin波です。
とりあえず、Sin波が広帯域に拡散されます。

Sin波一周期を,2π/shift*PN[n]づつ位相をずらしながら、サンプル数pointsで生成し、それをcycle回繰り返します。
PN[n]は1,-1をとる乱数数列です。

`--tone pn:seed,interval,basetone`

basetoneに指定したトーンを、XorShiftでintervalティックおきに反転します。
出力されるトーン長さは、basetoneと同じです。

`--tone mseq:bits,tap,basetone`

basetoneに指定したトーンをM-Sequenceで変調します。
出力されるトーン長さは、basetone*2^bitsです。

`--tone pcm:filename.wav`

ファイル名で示されるpcmファイルをそのまま1シンボル分のトーン信号にします。
pcmファイルは、1チャンネルモノラルでなければなりません。



トーン信号を指定した信号を復調するには、復調側のtx,demサブコマンドでも--toneを指定しなければなりません。
復調側で指定すべき値は、信号の変調結果にある、Tone: xxxTickの部分です。

```
Output file : aaa.wav  16000Hz,16bits,1ch,3.04sec(silence:0.50sec x 2)
Tone        : 'xpsk:10,10' 100ticks,6.2msec/symbol
Bit rate    : 160.0bps
```

このように指定します。
```
$ tbskmodem rx --tone 100 --text
```

キャリア周波数を変更した場合も同様です。--carrierで変調時と同じ値を与えてください。
