= �v���r���[��Word���̃e�L�X�g�\�� with xdoc2txt ver 0.1 =

== 1. �T�v ==

[http://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html xdoc2txt] ���g���āA
Word,Excel.PDF���̃e�L�X�g��Trac�̃��|�W�g���u���E�U�̃v���r���[�ɕ\������v���O�C���ł��B
xdoc2txt���g���Ă�̂ŁAWindows���Trac�𓮂����Ȃ��Ǝg���܂���B

���|�W�g���u���E�U��Word���̃t�@�C��������ƕ��i�͂��т����\���Ȃ̂ł����A
���̃v���O�C��������Ƃ��т����Ȃ��Ȃ�܂��B(*߁��)/ߥ: *
�܂��Axdoc2txt�͕ʓr���肵�Ă����K�v������܂��B

'''�m�F�ς݊�'''

||Windows 2000Pro||
||apache 2.0.54||
||Trac-0.92-ja||
||xdoc2txt 1.17||

'''����'''

  * Trac��Windows�œ��삵�Ă���K�v������܂��B
  * xdoc2txt��PATH�̂Ƃ������t�H���_�ɒu���K�v������܂��B
  * ������񓮍�͖��ۏ؂ł��B
  * �\����MS-Word2000,MS-Excel2000,�Í����E�p�X���[�h�̂Ȃ�PDF�ł��������Ă܂���B�����Axdoc2txt�Ńe�L�X�g���o�ł���΂��Ԃ���v�ł��傤�B

== 3. �Z�b�g�A�b�v ==

=== 3.1 �_�E�����[�h ===

�ȗ�

=== 3.2 �C���X�g�[�� ===

XDocViewPlugin�̃C���X�g�[�����s���܂��B

==== (1) egg�̐ݒu ====

zip���𓀂��Ă��������B
�𓀂��ďo�����t�H���_�z����src�f�B���N�g���Ɉړ����Ă��������B
�ȉ��̃R�}���h�����s���ĉ�����:

{{{
$ python setup.py bdist_egg
}}}

dist�t�H���_���쐬����܂��B
���̒��ɂ���*.egg�t�@�C�����ATracEnv��plugins�f�B���N�g���ɃR�s�[���Ă��������B

=== 3.3 xdoc2txt���Z�b�g�A�b�v����B ===

http://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html
����uxdoc2txt 1.17 ( d2txt117.lzh /107KB )�v,
 �ucryptlib.dll Ver1.00 ( crypt100.lzh / 37KB )�v(cryptlib�͖����Ă���) ��
�_�E�����[�h���Ă��������B
�K���ȃt�H���_�ɉ𓀂��A���ϐ�PATH�Ƀt�@�C����u�����t�H���_��ǉ����Ă��������B

=== 3.4 Apache���ċN������ ===

���̃v���O�C�����g���l�́AWindows��Apache���g�p���Ă���Ǝv���܂����A
Apache�͂����ċN�����������ł͊��ϐ�PATH��ǂݍ��݂Ȃ����Ă���܂���B
PC���ċN�����Ă��������B

== 4. �\�����Ă݂� ==

���|�W�g����Word,Excel���̃t�@�C����o�^���Ă��������B
Trac�̃��|�W�g���u���E�U�ŁA�o�^�����t�@�C����I�����Ă��������B
�e�L�X�g���\��������OK�ł��B���߂�������Axdoc2txt��PATH�̂Ƃ������t�H���_�ɂ��邩
�m�F���Ă��������B

== 5. ���l ==

=== 5.1 �g�p�\�ȃt�@�C���ɂ��� ===

�ȉ���MIME�^�C�v���󂯓����悤�ɂ��Ă܂��B�V��/��5/��6�ɂ��Ă�MIME�^�C�v���킩�炸�ł����B(!^��!^�G)

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


=== 5.2 ���C�Z���X�ɂ��� ===

xdoc2txt�̃��C�Z���X�́Ahttp://www31.ocn.ne.jp/~h_ishida/xdoc2txt.html ���Q�ƁB

----
Kazuya Hirobe <hirobe at weekbuild.sakura.ne.jp>

