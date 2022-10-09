# TBSK modem

TBSK (Trait Block Shift Keying) modemは、FFT/IFTTを使わない、低速、短距離の音響通信の実装です。

バイト/ビットストリームの振幅信号への変調、振幅信号からバイト/ビットストリームへの復調ができます。

開発用のライブラリと、コンソールアプリ[tbskmodem](tbskmodem.md)があります。

## 性能

静かな室内での音響通信性能は、ビットレートが5bps～1kbps、通信距離は1mくらいです。
パソコンに備わるマイクとスピーカーで通信ができます。

その他の媒体でも、それなりに波形を伝送できれば通信できると思います。


## 仕様

| パラメータ | 値 |
| --- | --- |
| 変調方式 | 特徴ブロック差動変調 |
| ビットレート | 5～1kbps |
| 搬送波周波数 | 任意 |
| 帯域幅 | 5Hz～全帯域 |
| エラー訂正/検出 | なし |

### 特徴ブロック差動変調

TBSKの特徴ブロック差動変調は、波形シンボルの代わりに任意形状のトーン信号とその反転値を、2値の伝送シンボルとして使います。
トーン信号はスペクトラム拡散したSin波を使いますが、他にも任意形状の波形を使うことができます。
復調は、隣接するシンボルの相関値を遅延検波します。相関値は1,-1を取るので、これをビットに復調します。

この伝送方式のパラメータは、トーン信号長(Tick数×搬送波周波数)のみです。トーン信号長だけ適合していれば、同一な復調器で信号の形式によらず復調することができます。

### 信号同期

信号の検出は、相関値を一定時間観測して判定します。信号の先端には通常のシンボルよりも長い同期パターンを配置します。
同期は初期の同期シンボル検知のほか、シンボル反転時の相関ピークを検出します。
搬送波の安定しないシステムでシンボルが長時間反転しない信号を送ると、同期が取れずにストリームが中断します。
数秒に一度はデータが反転するように送信するデータを加工してください。

### トーン信号

標準のトーン信号は、Sin波をPN符号で位相シフトしたスペクトラム拡散波形です。
トーン信号は復調側でS/N比が高くなる形状であれば何でも構いません。トーン信号にサイン波を使用すると、DPSK変調と同じ動作をします。

### 外乱耐性

トーン信号が長いほど外乱耐性は強くなりますが、トーン信号が長くなるほどビットレートは低下します。
搬送波周波数に対する最大通信レートの理論値は1bit/Hzです。実際には0.01bit/Hzが目安となります。

トーン信号は、線路媒体の特性に合わせて、時間方向、周波数方向に拡散（帯域の無駄遣い）ができます。


### パケット仕様
現状のプロトコルは、開始点検出とそれに続くペイロード読出しのみを実装しています。パケットサイズや終端識別子、エラー訂正、検出についてはアプリケーションで実装してください。

## ライセンス

本ソフトウェアは、MITライセンスで提供します。ホビー・研究用途では、MITライセンスに従って適切に運用してください。
産業用途では、特許の取り扱いに注意してください。

このライブラリはMITライセンスのオープンソースソフトウェアですが、特許フリーではありません。

特許権については、YAMAHA CORPORATION様の特許のうち、請求項4,請求項7,請求項8,請求項11,請求項12が該当すると考えられます。

[特許情報プラットフォーム](https://www.j-platpat.inpit.go.jp/)

[変調装置及び復調装置 WO-A-2010/016589](https://www.j-platpat.inpit.go.jp/c1800/PU/WO-A-2010-016589/7847773A7250230D1C8D66BBF506D4E794BEF7F38B5DF2B8C11BE9225DF7BB10/50/ja)

専門家の監修は受けておりませんので、詳細はご自身でお調べください。



## GetStarted

Anacondaの利用を前提として説明します。Pythonのバージョンは、Python 3.10.xを推奨します。

### セットアップ
ソースコードをgithubからcloneします。

```
>git clone https://github.com/nyatla/TBSKmodem.git
```

step4までは外部モジュールは不要です。
step4より先に進むならば、numpy,sounddeviceをインストールしてください。
サウンドの再生やキャプチャに必要です。

```
>conda install -c anaconda numpy
>conda install -c conda-forge python-sounddevice
```



### サンプルプログラムの場所

サンプルプログラムはTBSKmodem/getstartedディレクトリにあります。
```
> cd getstarted
```

#### step1. データをwaveファイルに変換する。
step1.modulate.pyは、ビット値を変調することができます。

```
> python step1_modulate.py
Imported local library.
[WARN] Imported local library.
>
```
このスクリプトは変調した振幅信号をwavファイルに保存します。
出力ファイル名は、step1.wavです。

`[WARN] Imported local library.`と表示されましたか？心配は不要です。
この表示は、ライブラリではなく、ローカルディレクトリにあるtbskmodemパッケージをリンクした時に表示されるメッセージです。

メイン関数を見てみましょう。
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

このスクリプトは、まず伝送シンボルに相当するXPskSinToneオブジェクトを生成します。
次に、変調器のTbskModulatorオブジェクトを生成して、modulateAsBit関数で変調します。
変調するのはビット値(1 or 0)の配列で、合計8*16=128ビットです。

modulateAsBit関数の戻り値は、変調した振幅値(float)を返すイテレータです。これをリストにして、最後にWaveファイルにして保存します。

#### step2. wavファイルの復調

step2.modulate.pyは、作成したwavファイルを元のビット列に戻します。
```
> python step2_demodulate.py
[WARN] Imported local library.
[0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
>
```
当然のように、元のビット列に戻るはずです。

メイン関数を見てみましょう。
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
信号を格納したWaveファイルはstep1で作成したstep1.wavです。これを読み出します。
次にトーン信号を作り、そこから復調器のTbskDemodulatorを作り、demodulateAsBit関数で復調します。

demodulateAsBit関数はビット列をintで返すイテレータです。これをリストにして表示します。


イテレータは信号が成立しなくなるまで値をビット値を返し続けます。(信号終端についての疑問はここでは一旦忘れます。)


#### step3. バイトデータの変調と復調

バイト値を送受信する関数も当然実装済みです。
step3_bytedata.pyは、bytes値の変調と復調を実行します。

```
> python .\step3_bytedata.py
[WARN] Imported local library.
[b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']
> 
```

メイン関数を見てみましょう。

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

step1とstep2を合体したような構造です。
mod.modulate関数に注目してください。ここで、payloadにbytesをそのまま渡しています。
そして、demod.demodulateAsBytesにも注目してください。データを渡すと、Bytesにして返してくれそうな関数です。

入力は連続するbytes値なのに戻り値が1byte単位のbytes型なのは不自然な気もしますが、そういうものです。

#### step4. 文字列の変調と復調

step4_text.pyは、文字列の変調と復調を実行します。

```
> python .\step4_text.py    
[WARN] Imported local library.
['ア', 'ン', 'タ', 'ヤ', 'ル', 'ー', 'ニ', 'ャ']
>
```
メイン関数を見てみましょう。step3とほとんど変わりません。

```
def main():
    tone=XPskSinTone(10,10).mul(0.5)    # SSFM DPSK
    payload="アンタヤルーニャ" # 8byte
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
変調部分はmod.modulateそのままです。
関数呼び出しの変更点は、復調部分でdemodulateAsStr関数が使われているところです。

変調器と復調器は、それぞれ、bit配列,文字列,Hex string,bytes,uint8配列を引数に取る関数があります。
勘の良い読者の方は気が付いたかもしれませんが、Hex stringはブロックチェーンネットワークのトランザクションを送信するための機能です。

イーサリウムネットワークにトランザクションをブリッジするためのサンプルはこちらです。
@todo

#### step5. マイク入力のテスト

step5_microphone.pyで、サウンドデバイスがpythonからアクセスできるかテストしましょう。

注意:WSL、VirtualBoxなどの仮想システムでは、サウンドデバイスにノイズが混じるため、通信が成立しないことがあります。

```
> python .\step5_microphone.py
[WARN] Imported local library.
Press [ENTER] to stop.
Volume meter
###
```

マイクに向かって一曲披露してください。選曲はお任せします。
"#"で示されるバーグラフが動いていれば、pythonは正常にマイクを認識しています。

うまく認識できない場合は次の事を試してください。

1. マイクがPCに接続されているか確認する。
2. スクリプトのdevice_idパラメータを変更する(1,2,3...)
3. 他のプログラムでマイクを認識しているか確認する。
4. もっと大きな声で歌う。

歌い終わったら、ENTERでプログラムを停止します。


#### step6. リアルタイム送受信

仕上げに、step6_realtime_receive.pyでリアルタイムに信号を復調します。
マイクの準備は宜しいですか？

注意:WSL、VirtualBoxなどの仮想システムでは、サウンドデバイスにノイズが混じるため、通信が成立しないことがあります。

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

実行したディレクトリに、step6.wavが生成されています。
このWaveファイルをpythonに聞かせてください。
復調した文字列が表示されます。

ところで、受信した信号の終端はどこなのか？という疑問が残されたままです。
TBSKでは、信号を検知した後、信号強度が閾値を超えていれば、それが何であっても延々と値を復調し続けます。
上位の通信仕様でパケット長を固定したり、長さパラメータを初めに送信するなどして対処してください。


チュートリアルはここまでです。[アンタヤルーニャ](http://wiki.ffo.jp/html/2682.html)






## 👈To Be Continued ▲▼▲

さて、来週(来年)の目標は、

1. Unityで動かしてみよう。
2. ブラウザでも動かしてみよう。
3. ペイロードの秘匿化とエラー訂正

の３本です。

