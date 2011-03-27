package org.ultimania;

/**
 * TracLightningのサンプルクラスコード
 * @author someone
 */
public class SampleLib {
	public enum LangType {
		RUBY, PYTHON, PERL, UNKNOWN
	};

	/**
	 * 言語の種類を判定
	 *
	 * @param langType
	 *            言語の種類を示す文字列
	 * @return 言語の種類
	 */
	public LangType detectLangType(String langType) {
		if (langType.equals("ruby")) {
			System.out.println("Rubyが選択されました");
			return LangType.RUBY;
		} else if (langType.equals("pyhon")) {
			System.out.println("Pythonが選択されました");
			return LangType.PYTHON;
		} else if (langType.equals("perl")) {
			System.out.println("Perlが選択されました");
			return LangType.PERL;
		}
		return LangType.UNKNOWN;
	}

}
