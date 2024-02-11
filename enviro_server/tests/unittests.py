import unittest
from enviro_server.tests.EnvironmentData_test import EnvironmentDataTest, EnvironmentValueTest
from enviro_server.tests.DataTransform_test import DataTransformTest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(EnvironmentValueTest('test_serialize'))
    suite.addTest(EnvironmentDataTest('test_deserialize'))
    suite.addTest(EnvironmentDataTest('get_dict'))
    suite.addTest(DataTransformTest("test_transform_data_big_amount"))
    suite.addTest(DataTransformTest("test_transform_data_small_amount"))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())