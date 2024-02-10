import unittest
from datetime import datetime
from enviro_server.EnvironmentData import EnvironmentData, CHANNELS, \
                                          EnvironmentValue, Units
from dataclasses import asdict

class EnvironmentValueTest(unittest.TestCase):
    def setUp(self):
        self.__val = EnvironmentValue(28, Units.TEMPERATURE, [28, 34])

    def test_serialize(self):
        self.assertEqual(self.__val,
                         EnvironmentValue.from_dict(asdict(self.__val)),
                         "Serialization or deserialization was failed.")

class EnvironmentDataTest(unittest.TestCase):
    def setUp(self):
        self.__data = EnvironmentData(
            datetime.now(),
            EnvironmentValue(28, Units.TEMPERATURE, [28, 34]),
            EnvironmentValue(970, Units.PRESSURE, [970, 1030]),
            EnvironmentValue(45, Units.HUMIDITY, [45, 70]),
            EnvironmentValue(30, Units.ILLUMINATION, [30, 250]),
            EnvironmentValue(20, Units.GAS, [20, 40]),
            EnvironmentValue(700, Units.GAS, [700, 1000]),
            EnvironmentValue(80, Units.GAS, [80, 120]),
            EnvironmentValue(80, Units.DUST, [500, 700])
        )

    def test_serialize(self):
        self.assertEqual(self.__data,
                         EnvironmentData.from_message(self.__data.serialize()),
                         "Serialization or deserialization was failed.")

    def test_get_dict(self):
        data_dict = self.__data.get_dict()
        self.assertIs(type(data_dict), dict)
        self.assertEqual(len(data_dict), CHANNELS + 1)
        for key in data_dict.keys():
            self.assertIsNotNone(data_dict[key], "Dict value is None.")
