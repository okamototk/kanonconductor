package org.ultimania;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.ultimania.SampleLib.LangType;

import static org.junit.Assert.*;

/**
 * SampleLib�̃e�X�g�N���X
 */
public class SampleLibTest {

	/**
	 * ���̃N���X�̑S�Ẵe�X�g�����s����O�̏���
	 */
	@BeforeClass
	public static void doBeforeTests() {
		// �S�Ẵe�X�g�����s����O�Ɉ�x�������s���鏈�����L�q
		// DB�̏�������e�X�g�ɂ���ē��e���ς��\��������t�@�C����
		// �����������Ȃǂ��L�q
	}

	/**
	 * �R���X�g���N�^�B�e�e�X�g�O�̏������L�q�B
	 */
	public SampleLibTest() {
		// �e�e�X�g���ɃC���X�^���X�����������B
		// �e�e�X�g���̏������L�q
	}

	/**
	 * �e�e�X�g��̏���
	 */
	@After
	public void postProcess() {
		// �e�e�X�g��̏������L�q����B
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
	 * ���̃N���X�̑S�Ẵe�X�g�����s������̏���
	 */
	@AfterClass
	public static void doAfterTests() {
		// ���̃N���X�̑S�Ẵe�X�g�̎��s���I��������Ƃɂ��鏈�����L�q�B
		// �ύX����DB�̍폜��S�~�t�@�C���̍폜�Ȃǂ��L�q����
	}

}
