package org.ultimania;

/**
 * TracLightning�̃T���v���N���X�R�[�h
 * @author someone
 */
public class SampleLib {
	public enum LangType {
		RUBY, PYTHON, PERL, UNKNOWN
	};

	/**
	 * ����̎�ނ𔻒�
	 *
	 * @param langType
	 *            ����̎�ނ�����������
	 * @return ����̎��
	 */
	public LangType detectLangType(String langType) {
		if (langType.equals("ruby")) {
			System.out.println("Ruby���I������܂���");
			return LangType.RUBY;
		} else if (langType.equals("pyhon")) {
			System.out.println("Python���I������܂���");
			return LangType.PYTHON;
		} else if (langType.equals("perl")) {
			System.out.println("Perl���I������܂���");
			return LangType.PERL;
		}
		return LangType.UNKNOWN;
	}

}
