package org.ultimania;

/**
 * �A�v���P�[�V�����̃T���v��
 * @author Takashi Okamoto
 */
public class SampleLib
{
    public static final int RUBY = 1;
    public static final int PYTHON = 2;
    public static final int PERL = 3;
    public static final int UNKNOWN = 4;
    /**
      * ����̎�ނ𔻒�
      * @param langType ����̎�ނ�����������
      * @return ����̎��
      */
    public int detectLangType(String langType) {
      if(langType.equals("ruby")){
        System.out.println("Ruby���ꂪ�ݒ肳��܂����B");
        return RUBY;
      } else if(langType.equals("python")){
        System.out.println("Python���ꂪ�ݒ肳��܂����B");
        return PYTHON;
      } else if(langType.equals("perl")){
        System.out.println("Perl���ꂪ�ݒ肳��܂����B");
        return PERL;
      }
      return UNKNOWN;
    }
}
