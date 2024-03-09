import unittest
from json import load
from enviro_server.tests.utils.load_environment_resources import load_environment_data
from enviro_server.database.models import EnvironmentRecordModel

class DataTest(unittest.TestCase):
        def setUp(self):
            self._raw_data, self._data = load_environment_data(self.resource_path)