import pathlib
from datetime import datetime
from enviro_server.EnvironmentData import CHANNELS, Units, Limits
from enviro_server.tests.DataTest import DataTest
from enviro_server.tasks import transform_data

class DataTransformTest(DataTest):
        def setUp(self):
            self.resource_path = pathlib.Path(__file__).parent.resolve() / "resources" / "data_transform_resource.json"
            super().setUp()

        def test_transform_data_big_amount(self):
            transformed_data = transform_data(self._data, 50)
            self.assertEqual(len(self._data), len(transformed_data) * CHANNELS)
            self.assertEqual(len(self._raw_data) / CHANNELS, len(transformed_data))
            self.__test_set(transformed_data)

        def test_transform_data_small_amount(self):
            transformed_data = transform_data(self._data, 2)
            self.assertEqual(len(transformed_data), 2)
            self.__test_set(transformed_data)

        def __test_set(self, transformed_data):
            for entry in transformed_data:
                self.assertIsNotNone(entry)
                for field_key in entry.keys():
                    if(field_key != "datetime"):
                        self.assertIn(entry[field_key]["unit"], Units)
                        self.assertIn(entry[field_key]["limits"], Limits.values())
                    else:
                        self.assertTrue(datetime.strptime(entry[field_key], '%Y-%m-%d %H:%M:%S.%f'))