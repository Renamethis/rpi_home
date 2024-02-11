import pathlib
from datetime import datetime
from enviro_server.EnvironmentData import CHANNELS, Units, Limits
from enviro_server.tests.DataTest import DataTest
from enviro_server.tasks import transform_data, calculate_slices

class DataTransformTest(DataTest):
        def setUp(self):
            self.resource_path = pathlib.Path(__file__).parent.resolve() / "resources" / "data_transform_resource.json"
            super().setUp()

        def test_calculate_slices_big(self):
            startSlice, endSlice, amount = calculate_slices((5, 40), len(self._data))
            self.assertEqual(startSlice, 0)
            self.assertEqual(endSlice, len(self._data))
            self.assertEqual(amount, len(self._data) / CHANNELS)

        def test_calculate_slices_small(self):
            startSlice, endSlice, amount = calculate_slices((2, 10), len(self._data))
            self.assertEqual(startSlice, 2 * CHANNELS)
            self.assertEqual(endSlice, 10 * CHANNELS)
            self.assertEqual(amount, 10)

        def test_transform_data_big(self):
            transformed_data = transform_data(self._data, 50)
            self.assertEqual(len(self._data), len(transformed_data) * CHANNELS)
            self.assertEqual(len(self._raw_data) / CHANNELS, len(transformed_data))
            self.__test_set(transformed_data)

        def test_transform_data_small(self):
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