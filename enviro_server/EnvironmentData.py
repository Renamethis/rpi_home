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
        oxidising : EnvironmentValue # Ok
        reducing : EnvironmentValue # Ok
        nh3 : EnvironmentValue # Ok

        @staticmethod
        def __from_dict(dict, itype=None):
            if(itype is None):
                itype = EnvironmentData
            try:
                fieldtypes = {f.name:f.type for f in fields(EnvironmentData)}
                return itype(**{f:itype.__from_dict(dict[f], fieldtypes[f]) \
                    for f in dict})
            except AttributeError as e:
                try:
                    return datetime.strptime(dict, '%Y-%m-%d %H:%M:%S.%f')
                except TypeError:
                    return EnvironmentValue.from_dict(dict)

        @staticmethod
        def from_message(message):
            return EnvironmentData.__from_dict(loads(message))

        def get_dict(self):
            return {k: (str(v) if isinstance(v, datetime) else v) \
                for k, v in asdict(self).items()}

        def serialize(self):
            return dumps(self.get_dict())
