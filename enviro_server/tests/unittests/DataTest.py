import unittest
from json import load
from enviro_server.database.models import EnvironmentRecordModel

class DataTest(unittest.TestCase):
        def setUp(self):
            with open(self.resource_path, "r") as resource:
                dict_data = load(resource)
                self._raw_data = dict_data
                self._data = [EnvironmentRecordModel(id=entry["id"], ptime=entry["ptime"],
                                                     value=entry["value"], field_name=entry["field_name"],
                                                     unit=entry["unit"])
                              for entry in dict_data]