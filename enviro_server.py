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
from dataclasses import dataclass, fields, asdict
import numpy as np
import logging

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
            
def read_bitmap(filename):
    png_source = Image.open(filename)
    png_np = np.array(png_source)
    _, png_grayscale = np.split(png_np,2,axis=2)
    png_grayscale = png_grayscale.reshape(-1)
    bitmap = np.array(png_grayscale).reshape([png_np.shape[0], png_np.shape[1]])
    bitmap = np.dot((bitmap > 128).astype(float),255)
    return Image.fromarray(bitmap.astype(np.uint8))
    
def load_resources(directory):
    bitmaps = {}
    for filename in os.listdir(directory):
        if(len(filename.split('-')) > 1):
            pattern = filename.split('-')[0]
            matched_list = []
            for f in os.listdir(directory):
                if(pattern in f):
                    matched_list.append(f)
            matched_list = sorted(matched_list)
            bitmap_list = [read_bitmap(os.path.join(directory, file)) for file in matched_list]    
            bitmaps[filename.split('-')[0]] = bitmap_list
            continue
        bitmaps[filename.split('.')[0]] = read_bitmap('resources/%s' % filename)
    return bitmaps
            

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
icons = load_resources('resources')
draw = ImageDraw.Draw(img)
path = os.path.dirname(os.path.realpath(__file__))
font_size = 9
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25

values = {}
for v in fields(EnvironmentData):
    values[v.name] = [1] * WIDTH

colors = ((20, 255, 20), (200, 200, 0), (255, 0, 0))
# Displays data and text on the 0.96" LCD
def display(data):
    x = 0
    y = 2
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    # Scale the values for the variable between 0 and 1
    j = 0
    for field in fields(data):
        values[field.name] = values[field.name][1:] + [getattr(data, field.name).value]
        vmin = min(values[field.name])
        vmax = max(values[field.name])
        colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[field.name]]
        name = field.name
        message = "%.1f" %  getattr(data, field.name).value + " %s" % getattr(data, field.name).unit
        draw.text((x, y + 27), message, font=font, fill=(125, 125, 0))
        for i in range(len(colours)):
            line_y = HEIGHT - (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
            #draw.rectangle((i, line_y, i + 1, line_y + 1), colors[j])
        i = 0
        for limit in getattr(data, field.name).limits:
            if(getattr(data, field.name).value < limit):
                break
            i += 1
        color = colors[i]
        if(type(icons[field.name]) is list):
            if(i >= len(icons[field.name])):
                i = len(icons[field.name]) - 1
            draw.bitmap((x,y), icons[field.name][i], fill = color)
        else:
            draw.bitmap((x,y), icons[field.name], fill=color)
        if(j % 2 == 0):
            y = 40
        else:
            y = 2
        j += 1
        x += 21
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
            EnvironmentValue(temperature, "C", [27, 34]),
            EnvironmentValue(pressure, "hPa", [970, 1030]),
            EnvironmentValue(humidity, "%", [50, 70]),
            EnvironmentValue(illumination, "Lux", [100, 500]),
            EnvironmentValue(oxidising, "Ok", [20, 40]),
            EnvironmentValue(reducing, "Ok", [700, 1000]),
            EnvironmentValue(nh3, "Ok", [80, 120])))


# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
