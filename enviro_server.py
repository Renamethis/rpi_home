#!/usr/bin/env python3

import time
import colorsys
import os
import sys
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
from dataclasses import dataclass, fields
import logging

@dataclass
class EnvironmentValue:
    value: float
    unit: str

@dataclass
class EnvironmentData:
        temperature : EnvironmentValue # C
        pressure : EnvironmentValue # hPa
        humidity : EnvironmentValue # %
        illumination : EnvironmentValue # lux
        oxidising : EnvironmentValue # Ok
        reducing : EnvironmentValue # Ok
        nh3 : EnvironmentValue # Ok

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""all-in-one.py - Displays readings from all of Enviro plus' sensors
Press Ctrl+C to exit!
""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
path = os.path.dirname(os.path.realpath(__file__))
font_size = 11
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25


# Displays data and text on the 0.96" LCD
def display(data):
    y = 0
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for field in fields(data):
        name = field.name
        print(getattr(data, field.name))
        message = field.name + " = %.1f" %  getattr(data, field.name).value + " %s" % getattr(data, field.name).unit
        draw.text((0, y), message, font=font, fill=(0, 0, 0))
        y+=11
    st7735.display(img)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

delay = 0.5  # Debounce the proximity tap
mode = 0  # The starting mode
last_page = 0
light = 1

def get_compensated_temperature():
    cpu_temps = [get_cpu_temperature()] * 5
    cpu_temp = get_cpu_temperature()
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    return raw_temp - ((avg_cpu_temp - raw_temp) / factor)

# The main loop
try:
    while True:
        temperature = get_compensated_temperature() # C
        pressure = bme280.get_pressure() # hPa
        humidity = bme280.get_humidity() # %
        illumination = ltr559.get_lux() # lux
        gas_data = gas.read_all() # Ok
        oxidising = gas_data.oxidising / 1000
        reducing = gas_data.reducing / 1000
        nh3 = gas_data.nh3 / 1000
        display(EnvironmentData(
            EnvironmentValue(temperature, "C"), 
            EnvironmentValue(pressure, "hPa"), 
            EnvironmentValue(humidity, "%"), 
            EnvironmentValue(illumination, "Lux"), 
            EnvironmentValue(oxidising, "Ol"), 
            EnvironmentValue(reducing, "Ok"), 
            EnvironmentValue(nh3, "Ok")))


# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
