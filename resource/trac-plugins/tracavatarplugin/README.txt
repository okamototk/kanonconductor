= TracAvatar�v���O�C�� = 
2010/08/30 Takashi Okamoto

== �T�v ==
TracAvatar�v���O�C���́ATrac�ɃA�o�^�[�@�\(���[�U�̃L�����N�^���@�\)��ǉ����܂��B
TracAvatar�v���O�C���𗘗p���邱�Ƃɂ��A�^�C�����C���̕ύX�҂�`�P�b�g�̒S���ҁA
�񍐎ҁA�R�����g�҂Ȃǃ��[�U�����\������镔���ɃL�����N�^���ꏏ�ɕ\�������悤
�ɂȂ�܂��B


== ���O���� ==
(��TracLightning�������p�̕��͎��O�����͕s�v�ł�)
TracAvatar�v���O�C���́ATracUserManager�v���O�C���̊g���Ƃ��Ď������Ă��܂��B����ɂ́A
�\��TracUserManager�v���O�C�����C���X�g�[�����Ă����K�v������܂��BTracUserManager
�v���O�C���̓���ɂ́ATracAccountManager�v���O�C�����K�v�ł��B

$ easy_install 

TracUserManager�v���O�C����
TracAccountManager�̓������@�ɂ��ẮA���L��URL���������������B

 * TracAccountManagerPlugin
     http://trac-hacks.org/wiki/AccountManagerPlugin
 * TracUserManagerPlugin
     http://code.optaros.com/trac/oforge

== �C���X�g�[�����@ ==
=== Trac�Ƀp�b�`�𓖂Ă� ===
�܂��́Atrac�{�̂Ɏ��̃p�b�`�𓖂āATrac���C���X�g�[�����܂��B
{{{
$ cd trac (Trac�̃\�[�X�f�B���N�g���ֈړ�)
$ patch -p1 < tractavatar_support_for_trac0.11.7.patch
$ python setup.py install
}}}

=== TracAvatar�v���O�C���̃C���X�g�[�� ===
���L�̎菇��TracAvatar�v���O�C�����C���X�g�[�����܂��B
{{{
$ svn co https://svn.sourceforge.jp/svnroot/shibuya-trac/plugins/tracavatarplugin/branches/0.11 tracavatarplugin
$ cd tracavatarplugin
$ python setup.py install
}}}
=== trac.ini�̐ݒ� ===
trac.ini�t�@�C���ɉ��L�̐ݒ��ǉ����ATracAvatar�v���O�C����L���ɂ��܂��B

[components]
tracavatar.web_ui.* = enabled

== �g���� ==
�^�C�����C����`�P�b�g�̃��[�U�����\���������ɃA�o�^�[���\�������悤�ɂȂ�܂��B
���j���[�̏�́u���[�U�ݒ�v�̃����N����uMy Profile�v�^�u���J���āAPicture:�őI�������摜���A�o�^�[�ɂȂ�܂��B




