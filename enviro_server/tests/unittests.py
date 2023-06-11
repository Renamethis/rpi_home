import unittest
from .EnvironmentData import EnvironmentDataTest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(EnvironmentDataTest('test_serialize'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())