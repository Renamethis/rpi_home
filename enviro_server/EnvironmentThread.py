from threading import Thread
from .EnvironmentData import EnvironmentData, EnvironmentValue
from .LCD import LCD
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas

class EnvironmentThread(Thread):
    
    FACTOR = 2.25
    
    def __init__(self):
        super().__init__()
        self.__bme280 = BME280()
        self.__lcd = LCD()

    def run(self):
        while self.__is_running:
            temperature = self.__get_compensated_temperature() # C
            pressure = self.__bme280.get_pressure() # hPa
            humidity = self.__bme280.get_humidity() # %
            illumination = ltr559.get_lux() # lux
            gas_data = gas.read_all() # Ok
            oxidising = gas_data.oxidising / 1000
            reducing = gas_data.reducing / 1000
            nh3 = gas_data.nh3 / 1000
            self.__data = EnvironmentData(
                EnvironmentValue(temperature, "C", [28, 34]),
                EnvironmentValue(pressure, "hPa", [970, 1030]),
                EnvironmentValue(humidity, "%", [45, 70]),
                EnvironmentValue(illumination, "Lux", [30, 250]),
                EnvironmentValue(oxidising, "Ok", [20, 40]),
                EnvironmentValue(reducing, "Ok", [700, 1000]),
                EnvironmentValue(nh3, "Ok", [80, 120])
            )
            self.__lcd.display(self.__data)

    def get_data(self):
        return self.__data

    def start(self):
        self.__is_running = True
        super().start()

    def stop(self):
        self.__is_running = False

    def __get_compensated_temperature(self):
        cpu_temps = [self.__get_cpu_temperature()] * 5
        cpu_temp = self.__get_cpu_temperature()
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = self.__bme280.get_temperature()
        return raw_temp - ((avg_cpu_temp - raw_temp) / self.FACTOR)
    
    def __get_cpu_temperature(self):
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
            temp = int(temp) / 1000.0
        return temp