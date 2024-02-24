#!/usr/bin/env python3
import time
import sys
import pathlib

from threading import Thread
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini
from .EnvironmentThread import spi_lock, critical_section
from gpiozero import Button


class MatrixThread(Thread):
    def __init__(self, bothSides):
        super().__init__()
        self.rotation = 0
        self.__bothSides = bothSides
        critical_section(spi_lock, self.__init_unicornhat)
        self.font = ImageFont.truetype(str(pathlib.Path().resolve() / "resources/5x7.ttf"), 8)
        self.__time_offset = 0
        self.__animation_fps = 30
        self.__init_buttons()

    def run(self):
        while True:
            self.time_animation()
            critical_section(spi_lock, self.unicornhatmini.show)
            time.sleep(1/self.__animation_fps)

    def time_animation(self):
        current_time = time.strftime("%H:%M", time.gmtime())
        image = self.__draw_text(current_time)
        for y in range(self.display_height):
            for x in range(self.display_width):
                hue = (time.time() / 10.0) + (x / float(self.display_width * 2))
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                if image.getpixel((x + self.__time_offset, y)) == 255:
                    critical_section(spi_lock, self.unicornhatmini.set_pixel, (x, y, r, g, b))
                else:
                    critical_section(spi_lock, self.unicornhatmini.set_pixel, (x, y, 0, 0, 0))

        self.__time_offset += 1
        if self.__time_offset + self.display_width > image.size[0]:
            self.__time_offset = 0

    def __init_buttons(self):
        button_a = Button(5)
        button_b = Button(6)
        # button_x = Button(16)
        button_y = Button(24)
        try:
            button_a.when_pressed = self.__button_callback
            button_b.when_pressed = self.__button_callback
            # button_x.when_pressed = self.__button_callback
            button_y.when_pressed = self.__button_callback
        except KeyboardInterrupt:
            button_a.close()
            button_b.close()
            button_x.close()
            button_y.close()

    def __button_callback(self, button):
        pin = button.pin.number

    def __init_unicornhat(self):
        self.unicornhatmini = UnicornHATMini(bothSectors=self.__bothSides, spi_max_speed_hz=6000)
        self.unicornhatmini.clear()
        self.unicornhatmini.set_rotation(self.rotation)
        self.unicornhatmini.set_brightness(0.1)
        self.display_width, self.display_height = self.unicornhatmini.get_shape()

    def __draw_text(self, text):
        text_width, text_height = self.font.getsize(text)
        image = Image.new('P', (text_width + self.display_width + self.display_width, self.display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((self.display_width, -1), text, font=self.font, fill=255)
        return image