# RawString Format Specification

RawStringはTBSKモデムのL2フォーマットであり、文字列転送用に設計されています。このフォーマットは、データの終端を終端文字\0によって確定します。また、エラー検出やエラー訂正機能は持ちません。

## EBNF Specification
```
raw_string = *(utf8_character / null_character);
utf8_character = utf8_octet / utf8_continuation_octet;
utf8_octet = %x00-7F / %xC2-DF utf8_continuation_octet / %xE0-EF 2utf8_continuation_octet / %xF0-F4 3utf8_continuation_octet;
utf8_continuation_octet = %x80-BF;
null_character = %x00;
raw_string: RawStringの主要な定義であり、UTF-8文字またはnull文字のシーケンスを含みます。
utf8_character: UTF-8文字の定義であり、単一のUTF-8文字を表します。
utf8_octet: UTF-8文字のバイト表現を定義します。1〜4バイトのUTF-8シーケンスを扱います。
utf8_continuation_octet: UTF-8多バイト文字の連続バイトを定義します。
null_character: 終端文字\0を表します。
```
## エンコード
データはUTF-8エンコードされ、終端文字\0によってデータの終端が確定されます。

## デコード
データは先頭からUTF-8文字にデコードされます。無効な文字コードが検出された場合、1バイトの非表示文字として扱われます。また、終端のnull文字が1つ以上出現した場合でも、1つのnull文字として扱われます。バイト列の先頭が0である場合、他のフォーマットにフォールバックします。フォールバック先がない場合は、エラーとして処理されます。
