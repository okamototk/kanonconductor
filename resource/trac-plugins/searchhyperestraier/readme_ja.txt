
= リポジトリの全文検索 with !HyperEstraier プラグイン Ver 0.1 =

== 1. 概要 ==

リポジトリ検索プラグインのHyperEstraier版を作りました。[[BR]]CGI版でもmod_python版でも動きます。

仕組み：バッチでリポジトリをエクスポートし、HyperEstraierのインデックスを生成します。Trac内でコマンド版cmdestを実行し、その結果を表示します。

cmdestの出力をXMLにしたせいでかえって文字コードがややこしかった。動作確認はWindowsのみで行ってます。[[BR]]HyperEstraierのpythonバインディングは使いませんでした。Windowsでのビルドに挫折。


'''確認済み環境'''

Trac0.9, Trac.011

'''制限'''

  * リポジトリ内の最新のファイルしか検索できません。
  * Windowsでしか動作確認してません。でもUnix系でも動くかも。
  * apacheからcmdest.exeを起動できるように権限設定が必要かもしれません。
  * もちろん動作は無保証です。コメントに何か書いてくれれば反応はするかもしれません。

== 3. セットアップ ==

=== 3.1 ダウンロード ===

Subversion を使用して、CodeReposからHTTP経由でチェックアウトしてください。コマンドラインクライアントでは、以下のようにします。

{{{
svn checkout http://svn.coderepos.org/share/browser/platform/trac/plugins/searchhyperestraier
}}}
[[BR]]

=== 3.2 インストール ===

プラグインのインストールを行います。[[FootNote(Tracのプラグインに共通する説明は、[wiki:TracPlugins TracPlugins]を参照してください。)]][[BR]]

==== (1) eggの設置 ====

zipを解凍してください。[[BR]]解凍して出来たフォルダ配下のtrunkディレクトリ(trac0.9用は/branches/0.9)に移動してください。[[BR]]以下のコマンドを実行して下さい:

{{{
$ python setup.py bdist_egg
}}}

distフォルダが作成されます。[[BR]]その中にある*.eggファイルを、TracEnvのplugins ディレクトリにコピーしてください。[[BR]]

=== 3.3 HyperEstraierをセットアップする ===

HyperEstraierをインストールして動くようにしてください。以下の手順で私はできました。できないひとは自分で調べてね。

==== (1) HyperEstraierをインストール ====

http://hyperestraier.sourceforge.net/ よりダウンロード(Windowsなら「 Windows版のバイナリパッケージ 」)。[[BR]]Unix系ならビルドするのかな。Windowsでは適当なフォルダ(C:\hyperestraier等)に解凍。

==== (2) 環境変数PATHの設定 ====

環境変数PATHに、(1)で置いたフォルダを追加。[[BR]]

=== 3.4.インデックスの設定をする ===

{{{
}}}

リポジトリのエクスポートとインデックス生成を行うバッチを作成します。 makeindex.batを適切に書き換えてください。冒頭部の環境変数を書き換えてください。このバッチでやっているのは、(1)リポジトリのエクス ポート(2)インデックス生成です。Unix系の人は自分でがんばって。[[BR]]なお、リポジトリのエクスポートの認証は考慮してません。認証が必要であればsvn exportに適切な引数を設定してください。

{{{
}}}

||EXPORT_FOLDER||リポジトリのエクスポート先となるフォルダ。空のフォルダを指定。||
||REPOS_URI||エクスポート元となるリポジトリのURI||
||INDEX_FOLDER||インデックスの生成先フォルダ。空のフォルダを指定。||

{{{
}}}

makeindex.batを実行した後で、以下のコマンドを実行して、正しく検索されることを確認してください。

{{{
}}}

{{{
 estcmd search -vx -sf -ic Shift_JIS [index_path] [query] >hoge.xml
}}}

{{{
}}}

[query]には適当に結果が出るキーワード(注：半角アルファベットで)、[index_path]にはmakeindex.batで指定した INDEX_FOLDERを指定してください。 結果はhoge.xmlファイルに出力されます。テキストエディタで開いて文字コードがUTF-8で出力されていることを確認してください。

{{{
}}}

{{{
}}}

動作確認ができたらmakeindex.batが１日１回実行できるようにWindowsのタスクを設定してください。

{{{
}}}
[[BR]]

=== 3.5 trac.iniを設定する ===

{{{
}}}

テキストファイルでtrac.ini(リポジトリのフォルダのconf配下)を開いて searchhyperestraierというブロックを追加してください。

{{{
}}}

||index_path||インデックス生成パス(makeindex.batのINDEX_FOLDER)||
||replace_left||検索結果のパスの頭で削るべき文字列。||
||browse_trac||Tracのブラウザへのリンクを作るか否か。enabled=Tracのブラウザへのリンクを作る。デフォルトは'enabled'。||
||url_left||URLを生成する際に頭につける文字列。browse_trac=enabledの場合は/がリポジトリのルートになるようにすること。||
||estcmd_path||環境変数PATHが設定済みなら設定不要。estcmd.exeの絶対パス。デフォルトは'estcmd'||
||estcmd_arg||Windowsでは設定不要。estcmd.exeの引数。デフォルトは'search -vx -sf -ic Shift_JIS'||
||estcmd_encode||Windowsでは設定不要。コマンド実行時のエンコード(Pythonでの形式)。デフォルトは'mbcs'||

例：

{{{
}}}

{{{
[searchhyperestraier]
index_path = E:\RepositorySearch\casket
replace_left = E:\RepositorySearch\rep
url_left = /trunk/test3
}}}

{{{
}}}

browser_tracがenabledになる場合は、登録されるURLはTracのリポジトリブラウザでRoot直下が/となるように replace_left,url_leftを調整する必要があります。[[BR]]たとえば、リポジトリブラウザでRoot/trunk/test3/検索のテスト.docと表示されるファイルは、/trunk/test3/検索のテスト.docとなるように調整してください。[[BR]]難しければ、何も設定せずに、検索結果として表示されたURLを見ながら調整してください。

{{{
}}}

=== 3.6 Apacheを再起動する ===

なお、WindowsでApacheを使用している場合、Apacheの再起動をしてもPATHを読み直してはくれません。PC自体を再起動してください。[[BR]][[BR]]

== 4. 検索してみる。 ==

{{{
}}}

検索タブをクリックして、「リポジトリ」チェックボックスが表示されることを確認してください。[[BR]]適当なキーワードで検索して、結果(source:××)が表示されることを確認してください。[[BR]]リンクをクリックして、画面がリポジトリブラウザに切り替わり、正しくそのファイルを表示していることを確認してください。

{{{
}}}

== 5. ご意見・ご要望 ==

ご意見・ご要望は[http://weekbuild.sakura.ne.jp/trac/newticket?component=SearchHyperEstraierPlugin こちら] から登録してください。[[BR]]これまでに登録されたものは[http://weekbuild.sakura.ne.jp/trac/query:?component=SearchHyperEstraierPlugin こちら] を参照してください。[[BR]][[BR]][[BR]][[FootNote]][[BR]][[BR]]