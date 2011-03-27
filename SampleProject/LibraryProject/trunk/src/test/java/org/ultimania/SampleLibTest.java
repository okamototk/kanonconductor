package org.ultimania;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.ultimania.SampleLib.LangType;

import static org.junit.Assert.*;

/**
 * SampleLibのテストクラス
 */
public class SampleLibTest {

	/**
	 * このクラスの全てのテストを実行する前の処理
	 */
	@BeforeClass
	public static void doBeforeTests() {
		// 全てのテストを実行する前に一度だけ実行する処理を記述
		// DBの初期化やテストによって内容が変わる可能性があるファイルの
		// 初期化処理などを記述
	}

	/**
	 * コンストラクタ。各テスト前の処理を記述。
	 */
	public SampleLibTest() {
		// 各テスト毎にインスタンスが生成される。
		// 各テスト毎の処理を記述
	}

	/**
	 * 各テスト後の処理
	 */
	@After
	public void postProcess() {
		// 各テスト後の処理を記述する。
	}

	@Test
	public void pythonTest() {
		SampleLib lib = new SampleLib();
		assertEquals(LangType.PYTHON, lib.detectLangType("python"));
	}

	@Test
	public void rubyTest() {
		SampleLib lib = new SampleLib();
		assertEquals(LangType.RUBY, lib.detectLangType("ruby"));
	}

	@Test
	public void perlTest() {
		SampleLib lib = new SampleLib();
		assertEquals(LangType.PERL, lib.detectLangType("perl"));
	}

	@Test
	public void otherTest() {
		SampleLib lib = new SampleLib();
		assertEquals(LangType.UNKNOWN, lib.detectLangType("scala"));
	}

	/**
	 * このクラスの全てのテストを実行した後の処理
	 */
	@AfterClass
	public static void doAfterTests() {
		// このクラスの全てのテストの実行が終わったあとにする処理を記述。
		// 変更したDBの削除やゴミファイルの削除などを記述する
	}

}
