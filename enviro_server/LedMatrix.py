#!/usr/bin/env python3
import time
import sys
import pathlib

from threading import Thread
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini
from .EnvironmentThread import spi_lock, critical_section


class MatrixThread(Thread):
    def __init__(self):
        super().__init__()
        self.rotation = 0
        critical_section(spi_lock, self.__init_unicornhat)
        self.font = ImageFont.truetype(str(pathlib.Path().resolve() / "resources/5x7.ttf"), 8)

    def __init_unicornhat(self):
        self.unicornhatmini = UnicornHATMini(spi_max_speed_hz=6000)
        self.unicornhatmini.set_rotation(self.rotation)
        self.unicornhatmini.set_brightness(0.1)
        self.display_width, self.display_height = self.unicornhatmini.get_shape()

    def run(self):
        offset_x = 0
        while True:
            current_time = time.strftime("%H:%M", time.gmtime())
            image = self.__draw_text(current_time)
            for y in range(self.display_height):
                for x in range(self.display_width):
                    hue = (time.time() / 10.0) + (x / float(self.display_width * 2))
                    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                    if image.getpixel((x + offset_x, y)) == 255:
                        critical_section(spi_lock, self.unicornhatmini.set_pixel, (x, y, r, g, b))
                    else:
                        critical_section(spi_lock, self.unicornhatmini.set_pixel, (x, y, 0, 0, 0))

            offset_x += 1
            if offset_x + self.display_width > image.size[0]:
                offset_x = 0
            critical_section(spi_lock, self.unicornhatmini.show)
            time.sleep(0.1)

    def __draw_text(self, text):
        text_width, text_height = self.font.getsize(text)
        image = Image.new('P', (text_width + self.display_width + self.display_width, self.display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((self.display_width, -1), text, font=self.font, fill=255)
        return image