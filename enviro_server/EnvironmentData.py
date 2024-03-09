from dataclasses import dataclass, asdict, fields
from enum import Enum
from json import dumps, loads
from datetime import datetime

CHANNELS = 8

class Units(str, Enum):
    TEMPERATURE = "C"
    PRESSURE = "hPa"
    HUMIDITY = "%"
    ILLUMINATION = "lux"
    DUST = "ug/m3"
    GAS = "Ok"

Limits = {
    "temperature" : (28, 34),
    "pressure" : (970, 1030),
    "humidity" : (45, 70),
    "illumination" : (30, 250),
    "dust" : (30, 100),
    "oxidizing" : (40, 60),
    "reducing" : (700, 1000),
    "nh3" : (120, 200),
}

@dataclass
class EnvironmentValue:
    value: float
    unit: Units
    limits: tuple

    @staticmethod
    def from_dict(dictionary):
        return EnvironmentValue(
            value = dictionary['value'],
            unit = Units(dictionary['unit']),
            limits = dictionary['limits']
        )

@dataclass
class EnvironmentData:
        datetime: datetime
        temperature : EnvironmentValue # C
        pressure : EnvironmentValue # hPa
        humidity : EnvironmentValue # %
        illumination : EnvironmentValue # lux
        dust : EnvironmentValue # ug/m3
        oxidizing : EnvironmentValue # Ok
        reducing : EnvironmentValue # Ok
        nh3 : EnvironmentValue # Ok

        @staticmethod
        def from_dict(dict, itype=None):
            if(itype is None):
                itype = EnvironmentData
            try:
                fieldtypes = {f.name:f.type for f in fields(EnvironmentData)}
                return itype(**{f:itype.from_dict(dict[f], fieldtypes[f]) \
                    for f in dict})
            except (AttributeError, KeyError) as e:
                try:
                    return datetime.strptime(dict, '%Y-%m-%d %H:%M:%S.%f')
                except TypeError:
                    return EnvironmentValue.from_dict(dict)

        @staticmethod
        def from_message(message):
            return EnvironmentData.from_dict(loads(message))

        @property
        def dict(self):
            return {k: (str(v) if isinstance(v, datetime) else v) \
                for k, v in asdict(self).items()}

        def serialize(self):
            return dumps(self.dict)
