import time
import _thread as thread
import requests
from requests.exceptions import ConnectionError
from json import loads
from json.decoder import JSONDecodeError
from enviro_server.unicornhatclock.options import weather_options

weather_code = 0
weather_temp = None


def get_code():
    return weather_code

def get_temp():
    return weather_temp
