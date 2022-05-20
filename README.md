# Exif情報の読み取り

## 目次
- [はじめに](#はじめに)
- [Exifの全体構造](#Exifの全体構造)
- [IFDの概略](#IFDの概略)
- [フィールドの構成](#フィールドの構成)
- [参考](#参考)

## はじめに
exiftoolを入れるのが面倒なのでExifを読み取るコードを書いてみた。ここにExifのデータ構造を備忘録として書いておく。なお、互換性IFD(interoperability IFD)については十分に情報が得られなかったため、Makernoteについては機種により仕様が異なるため([こちら](https://exiftool.org/makernote_types.html)を参照)、それぞれ対応していない。悪しからず。

## Exifの全体構造
<div align="center"><img src="https://github.com/mathphilia/Exif/blob/main/images/Figure1.png?raw=true"></div>  
上記がJPEG圧縮データの構造である。ExifはAPP1に入っている。Exif IFDのみがExifの情報ではなく、APP1全体がExif情報を構成する。  
ヘッダにはAPP1セグメントに関する情報が書かれている。具体的には大きく4つに分かれており、最初の2bytesがAPP1マーカ(APP1であることを示す目印。値は常に`b'\xff\xe1'`)、続く2bytesがAPP1全体からAPP1マーカを除いた部分の長さ(big endian)、続く6bytesがExif識別子(Exifであることを示す目印。値は常に`b'Exif\x00\x00'`)、続く8bytesはTIFFヘッダである。TIFFヘッダはさらに3つの部分に分かれる。最初の2bytesがバイトオーダー識別子(APP1内の数値の表現方法を示す。big endianなら`b'MM'`, little endianなら`b'II'`)、続く2bytesがTIFFバージョン(調べた限りでは常に42)、最後の4bytesは0th IFDのオフセット(TIFFヘッダの0byte目が0)である。なお、TIFFヘッダ内の数値も最初の2bytesで示されるバイトオーダーに従う。例として、APP1の長さ(APP1マーカ除く)が1234bytesで、バイトオーダーがlittle endianであり、0th IFDがTIFFヘッダの直後から始まる場合、APP1ヘッダは`b'\xff\xe1\x04\xd2\x45\x78\x69\x66\x00\x00\x49\x49\x2a\x00\x08\x00\x00\x00'`となる。  
<div align="center"><img src="https://github.com/mathphilia/Exif/blob/main/images/Figure2.png?raw=true"></div>

## IFDの概略
IFD(Image File Directory)はAPP1セグメントにおいて情報を格納するデータ構造である。IFDの先頭にはそのIFDが格納するフィールドの個数が記されている。その後には、次節で説明する各フィールドの内容が記述される。続いて後続IFDへのオフセットが記述されるが、この部分には通常「後続IFDがない」ことを示す0が入っている。その次にフィールドの値が入っている。これに関しても次節で説明する。1st IFDのみは、最後にサムネイル(主画像の縮小版, JPEG形式)が書かれている。  
標準IFDとしては0th IFD, 1st IFD, Exif IFD, GPS IFD, 互換性IFDの5種類がある。以下、各IFDの概略を説明する。0th IFDはExifに必ず存在するIFDである(中身が空っぽであることはあるが)。画像の幅や高さ、ファイルの変更日時やソフトウェアなど、主画像に関する情報が入っている。1st IFDにはサムネイルに関する情報が0th IFDと同様に入っている。Exif IFDにはExifバージョンや時差データ、温度・湿度・加速度など、Exif固有の付属情報が入っている。GPS IFDには緯度・経度・高度やGPSの測位方法など、GPSに関する情報が入っている。互換性IFDは互換性を保証するための情報が入っているらしいが、情報が少なくよくわからなかった。また、非標準IFDとしてMakernote IFDがあるとか。これに関しては機種によってあまりに多様であるためなかなか難しい。

## フィールドの構成
各フィールドはすべて12bytesで構成されており、具体的にはタグ番号、タイプ、カウント、値(のオフセット)の4つの部分からなる。冒頭2bytesのタグ番号はそのフィールドが保持する情報の種類を表す。例えばタグ番号が259(0x0103)ならそのフィールドには画像の圧縮方法が格納されていることになる。タグ番号とデータ種別の対応表はPIL.ExifTags.pyのTAGSやGPSTAGSを見ると分かる。また、[参考](#参考)に貼った仕様書も参照されたい。続く2bytesのタイプは、格納された情報のデータ形式を示す。タイプの値とデータ形式の対応はTIFF Rivision6.0に従い、以下のように定められている。  
<div align="center"><img src="https://github.com/mathphilia/Exif/blob/main/images/Figure3.png?raw=true"></div>  
なお、灰色で書かれているものはExifでは使われない。(123, 456, 789)のように、1つのフィールドに複数の値が格納されることもある(複数のデータタイプが混ざることはない)。また、ASCIIおよびUNDEFINEDは、文字列/バイト列の集まりとしてではなく、文字/バイトの集まりとして、すなわち('e', 'x', 'i', 'f', '\x00')や(b'\x03', b'\x01', b'\x04')のように格納される。このようなタプル(?)の長さが、タイプに続く4bytesに書かれるカウントである。つまり、タイプがASCIIでカウントが5ならデータサイズは1×5=5bytes、タイプがRATIONALでカウントが3(例: (22/7, 355/113, 103993/33102))ならデータサイズは8×3=24になる。カウントに続く4bytesに書かれる「値のオフセット」は、そのフィールドの保持する実データがどこにあるかを示す。各フィールドは12bytes固定なので、一定以上データサイズが大きいとフィールドに格納できないため、後続IFDのオフセットの後にまとめて保管する。オフセットの起点は、APP1ヘッダの末尾にある0th IFDのオフセットの起点と同じく、TIFFヘッダの0byte目である。ただし、実データ全体の長さ(タイプがRATIONALでカウントが3なら24bytes)が4bytes以下なら、「値のオフセット」の部分にオフセットでなく実データそのものが左詰めで書かれる。1st IFDの場合はこの後にサムネイルの画像データが続く。なお、このサムネイルデータのオフセットは1st IFD内のJPEGInterchangeFormatタグ(PIL.ExifTags.pyのTAGSでは'JpegIFOffset'に当たる)に書かれている。フィールドのバイト列の例を2つ挙げる。まず、バイトオーダーがlittle endianのExifで、タグ番号が256(0x0100, ImageWidth)、タイプがSHORT、カウントが1、実データが4800(0x12c0)のとき、このフィールドのバイト列は`b'\x00\x01\x03\x00\x01\x00\x00\x00\xc0\x12\x00\x00'`となる。また、バイトオーダーがbig endianのExifで、タグ番号が306(0x0132, DateTime)、タイプがASCII、カウントが20、実データが'2112:09:03 12:34:56\x00'のとき、実データが4bytesを越えるため後続IFDのオフセットの後に保管される。実データがTIFFヘッダの0byte目の1000bytes後から始まる場合、このフィールドのバイト列は`b'\x01\x32\x00\x02\x00\x00\x00\x14\x00\x00\x03\xe8'`となる。  
<div align="center"><img src="https://github.com/mathphilia/Exif/blob/main/images/Figure4.png?raw=true"></div>

## 参考
コードや解説を書くにあたって参考にしたページを記載する。多分私の拙い文章よりこれらのページの説明の方が分かりやすい。
- [Exif データにアクセスするコードを自作してみる : DSAS開発者の部屋](http://dsas.blog.klab.org/archives/52123322.html)
- [EXIFファイル入門](http://www.nextftp.com/swlabo/m0_pctech/pc_exif/exf_00.htm)
- [Exifについて](https://hp.vector.co.jp/authors/VA032610/JPEGFormat/AboutExif.htm)
- [Exif Version 2.32の仕様書(日本語版)](https://www.cipa.jp/std/documents/j/DC-X008-2019-J.pdf)
- [Exif Version 2.32の仕様書(英語版)](https://www.cipa.jp/std/documents/e/DC-X008-Translation-2019-E.pdf)
- [CGファイル概説 TIFFファイル](http://www.snap-tck.com/room03/c02/cg/cg05_01.html)
- [Makernote Types](https://exiftool.org/makernote_types.html)
