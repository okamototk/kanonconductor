import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(util_test.suite())
    return suite
 
if __name__ == '__main__':
    unittest.main(defaultTest="suite")