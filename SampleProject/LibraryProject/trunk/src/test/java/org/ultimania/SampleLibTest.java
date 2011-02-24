package org.ultimania;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

/**
 * Unit test for simple SampleLibTest.
 */
public class SampleLibTest extends TestCase {
	/**
	 * Create the test case
	 * 
	 * @param testName
	 *            name of the test case
	 */
	public SampleLibTest(String testName) {
		super(testName);
	}

	/**
	 * @return the suite of tests being tested
	 */
	public static Test suite() {
		return new TestSuite(SampleLibTest.class);
	}

	/**
	 * Rigourous Test :-)
	 */
	public void testDetectLangType() {
		System.out.println(
				"==========\n"
				+ java.util.ResourceBundle.getBundle("msg").getString("message")
				+"\n==========\n");
		SampleLib lib = new SampleLib();
		assertEquals(lib.detectLangType("ruby"), SampleLib.RUBY);
		assertEquals(lib.detectLangType("pyton"), SampleLib.PYTHON);
		assertEquals(lib.detectLangType("perl"), SampleLib.PERL);
	}
}
