from time import sleep
from .EnvironmentData import EnvironmentData, EnvironmentValue, Units, Limits
from .LCD import LCD
from threading import Thread, Lock
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from pms5003 import PMS5003
from bme280 import BME280
from enviroplus import gas
from datetime import datetime

spi_lock = Lock()

def critical_section(lock, routine, args=None):
    while(not lock.acquire(blocking=True)):
        pass
    if(args is not None):
        result = routine(*args)
    else:
        result = routine()
    lock.release()
    return result

class EnvironmentThread(Thread):

    FACTOR = 2.25
    __data = None

    def __init__(self, redis_client, with_display=True):
        super().__init__()
        self.__lcd = LCD(1 if with_display else 0)
        if(not with_display):
            self.__lcd.backlight = 0
        else:
            self.__lcd.backlight = 1
        self.__bme280 = BME280()
        self.__pms5003 = PMS5003()
        self.__client = redis_client

    def run(self):
        while(self.__is_running):
            critical_section(spi_lock, self.__build_environment_data)
            self.__client.rpush('Data', self.__data.serialize())
            sleep(1)

    def get_data(self):
        return self.__data

    def start(self):
        self.__is_running = True
        super().start()

    def stop(self):
        self.__is_running = False

    def __build_environment_data(self):
        (temperature, pressure, humidity, illumination, dust, gas_data) =  self.__read_data_from_sensors()
        oxidizing = gas_data.oxidising / 1000
        reducing = gas_data.reducing / 1000
        nh3 = gas_data.nh3 / 1000
        data = EnvironmentData(
            datetime.now(),
            EnvironmentValue(temperature, Units.TEMPERATURE, Limits["temperature"]),
            EnvironmentValue(pressure, Units.PRESSURE, Limits["pressure"]),
            EnvironmentValue(humidity, Units.HUMIDITY, Limits["humidity"]),
            EnvironmentValue(illumination, Units.ILLUMINATION, Limits["illumination"]),
            EnvironmentValue(dust, Units.DUST, Limits["dust"]),
            EnvironmentValue(oxidizing, Units.GAS, Limits["oxidizing"]),
            EnvironmentValue(reducing, Units.GAS, Limits["reducing"]),
            EnvironmentValue(nh3, Units.GAS, Limits["nh3"])
        )
        self.__data = data
        self.__lcd.display(data)

    def __read_data_from_sensors(self):
        return (self.__get_compensated_temperature(), # C
            self.__bme280.get_pressure(), # hPa
            self.__bme280.get_humidity(), # %
            ltr559.get_lux(), # lux
            float(self.__pms5003.read().pm_ug_per_m3(2.5)), # ug/m3
            gas.read_all()) # Ok

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