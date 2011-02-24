= プレビューでWord等のテキスト表示 with xdoc2txt ver 0.1 =

== 1. 概要 ==

[http://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html xdoc2txt] を使って、
Word,Excel.PDF等のテキストをTracのリポジトリブラウザのプレビューに表示するプラグインです。
xdoc2txtを使ってるので、Windows上でTracを動かさないと使えません。

リポジトリブラウザでWord等のファイルを見ると普段はさびしい表示なのですが、
このプラグインを入れるとさびしくなくなります。(*ﾟ▽ﾟ)/ﾟ･: *
また、xdoc2txtは別途入手しておく必要があります。

'''確認済み環境'''

||Windows 2000Pro||
||apache 2.0.54||
||Trac-0.92-ja||
||xdoc2txt 1.17||

'''制限'''

  * TracはWindowsで動作している必要があります。
  * xdoc2txtはPATHのとおったフォルダに置く必要があります。
  * もちろん動作は無保証です。
  * 表示はMS-Word2000,MS-Excel2000,暗号化・パスワードのないPDFでしか試してません。ただ、xdoc2txtでテキスト抽出できればたぶん大丈夫でしょう。

== 3. セットアップ ==

=== 3.1 ダウンロード ===

省略

=== 3.2 インストール ===

XDocViewPluginのインストールを行います。

==== (1) eggの設置 ====

zipを解凍してください。
解凍して出来たフォルダ配下のsrcディレクトリに移動してください。
以下のコマンドを実行して下さい:

{{{
$ python setup.py bdist_egg
}}}

distフォルダが作成されます。
その中にある*.eggファイルを、TracEnvのpluginsディレクトリにコピーしてください。

=== 3.3 xdoc2txtをセットアップする。 ===

http://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html
から「xdoc2txt 1.17 ( d2txt117.lzh /107KB )」,
 「cryptlib.dll Ver1.00 ( crypt100.lzh / 37KB )」(cryptlibは無くても可) を
ダウンロードしてください。
適当なフォルダに解凍し、環境変数PATHにファイルを置いたフォルダを追加してください。

=== 3.4 Apacheを再起動する ===

このプラグインを使う人は、WindowsでApacheを使用していると思いますが、
Apacheはただ再起動しただけでは環境変数PATHを読み込みなおしてくれません。
PCを再起動してください。

== 4. 表示してみる ==

リポジトリにWord,Excel等のファイルを登録してください。
Tracのリポジトリブラウザで、登録したファイルを選択してください。
テキストが表示されればOKです。だめだったら、xdoc2txtがPATHのとおったフォルダにあるか
確認してください。

== 5. 備考 ==

=== 5.1 使用可能なファイルについて ===

以下のMIMEタイプを受け入れるようにしてます。新松/松5/松6についてはMIMEタイプがわからずでした。(!^▽!^；)

{{{
application/msword
application/rtf
application/vnd.ms-excel
application/vnd.ms-powerpoint
application/pdf
application/x-js-taro
application/vnd.fujitsu.oasys
application/vnd.fujitsu.oasys2
application/vnd.fujitsu.oasys3
application/lotus-123
}}}


=== 5.2 ライセンスについて ===

xdoc2txtのライセンスは、http://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html を参照。

----
Kazuya Hirobe <hirobe at weekbuild.sakura.ne.jp>

