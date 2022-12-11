from dataclasses import dataclass, asdict

@dataclass
class EnvironmentValue:
    value: float
    unit: str
    limits: list

@dataclass
class EnvironmentData:
        temperature : EnvironmentValue # C
        pressure : EnvironmentValue # hPa
        humidity : EnvironmentValue # %
        illumination : EnvironmentValue # lux
        oxidising : EnvironmentValue # Ok
        reducing : EnvironmentValue # Ok
        nh3 : EnvironmentValue # Ok

        def get_dict(self):
            return {k: str(v) for k, v in asdict(self).items()}