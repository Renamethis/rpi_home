from dataclasses import dataclass, asdict, fields
from enum import Enum
from json import dumps, loads
from datetime import datetime

class Units(str, Enum):
    TEMPERATURE = "C"
    PRESSURE = "hPa"
    HUMIDITY = "%"
    ILLUMINATION = "lux"
    OXIDISING = "Ok"
    REDUCING = "Ok"
    NH3 = "Ok"

@dataclass
class EnvironmentValue:
    value: float
    unit: Units
    limits: list

@dataclass
class EnvironmentData:
        datetime: datetime
        temperature : EnvironmentValue # C
        pressure : EnvironmentValue # hPa
        humidity : EnvironmentValue # %
        illumination : EnvironmentValue # lux
        oxidising : EnvironmentValue # Ok
        reducing : EnvironmentValue # Ok
        nh3 : EnvironmentValue # Ok

        @staticmethod
        def __from_dict(dict, type=None):
            if(type is None):
                type = EnvironmentData
            try:
                fieldtypes = {f.name:f.type for f in fields(EnvironmentData)}
                return type(**{f:type.__from_dict(dict[f], fieldtypes[f]) for f in dict})
            except Exception:
                return dict

        @staticmethod
        def from_message(message):
            return EnvironmentData.__from_dict(loads(message))

        def get_dict(self):
            return {k: str(v) for k, v in asdict(self).items()}

        def serialize(self):
            return dumps(self.get_dict())