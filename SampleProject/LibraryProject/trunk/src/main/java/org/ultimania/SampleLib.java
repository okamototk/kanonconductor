package org.ultimania;

/**
 * アプリケーションのサンプル
 * @author Takashi Okamoto
 */
public class SampleLib
{
    public static final int RUBY = 1;
    public static final int PYTHON = 2;
    public static final int PERL = 3;
    public static final int UNKNOWN = 4;
    /**
      * 言語の種類を判定
      * @param langType 言語の種類を示す文字列
      * @return 言語の種類
      */
    public int detectLangType(String langType) {
      if(langType.equals("ruby")){
        System.out.println("Ruby言語が設定されました。");
        return RUBY;
      } else if(langType.equals("python")){
        System.out.println("Python言語が設定されました。");
        return PYTHON;
      } else if(langType.equals("perl")){
        System.out.println("Perl言語が設定されました。");
        return PERL;
      }
      return UNKNOWN;
    }
}
