= TracAvatarプラグイン = 
2010/08/30 Takashi Okamoto

== 概要 ==
TracAvatarプラグインは、Tracにアバター機能(ユーザのキャラクタ化機能)を追加します。
TracAvatarプラグインを利用することにより、タイムラインの変更者やチケットの担当者、
報告者、コメント者などユーザ名が表示される部分にキャラクタも一緒に表示されるよう
になります。


== 事前準備 ==
(※TracLightningをご利用の方は事前準備は不要です)
TracAvatarプラグインは、TracUserManagerプラグインの拡張として実装しています。動作には、
予めTracUserManagerプラグインをインストールしておく必要があります。TracUserManager
プラグインの動作には、TracAccountManagerプラグインが必要です。

$ easy_install 

TracUserManagerプラグインと
TracAccountManagerの導入方法については、下記のURLをご覧ください。

 * TracAccountManagerPlugin
     http://trac-hacks.org/wiki/AccountManagerPlugin
 * TracUserManagerPlugin
     http://code.optaros.com/trac/oforge

== インストール方法 ==
=== Tracにパッチを当てる ===
まずは、trac本体に次のパッチを当て、Tracをインストールします。
{{{
$ cd trac (Tracのソースディレクトリへ移動)
$ patch -p1 < tractavatar_support_for_trac0.11.7.patch
$ python setup.py install
}}}

=== TracAvatarプラグインのインストール ===
下記の手順でTracAvatarプラグインをインストールします。
{{{
$ svn co https://svn.sourceforge.jp/svnroot/shibuya-trac/plugins/tracavatarplugin/branches/0.11 tracavatarplugin
$ cd tracavatarplugin
$ python setup.py install
}}}
=== trac.iniの設定 ===
trac.iniファイルに下記の設定を追加し、TracAvatarプラグインを有効にします。

[components]
tracavatar.web_ui.* = enabled

== 使い方 ==
タイムラインやチケットのユーザ名が表示される個所にアバターが表示されるようになります。
メニューの上の「ユーザ設定」のリンクから「My Profile」タブを開いて、Picture:で選択した画像がアバターになります。




