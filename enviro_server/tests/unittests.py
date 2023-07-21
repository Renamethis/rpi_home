import unittest
from EnvironmentData_test import EnvironmentDataTest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(EnvironmentDataTest('test_serialize'))
    suite.addTest(EnvironmentDataTest('test_deserialize'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())