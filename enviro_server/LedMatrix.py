#!/usr/bin/env python3
import time
import sys
import pathlib
import math
from threading import Thread
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont, ImageOps
from unicornhatmini_fork import UnicornHATMini, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y
from gpiozero import Button
from enviro_server.unicornhatclock.weather_view import WeatherView
from enviro_server.unicornhatclock.options import led_options

MODE_COUNT = 2

TIME_MODE = 0
WEATHER_MODE = 1
UNICORN_MODE = 2

class MatrixThread(Thread):
    def __init__(self, bothSides, redis_client):
        super().__init__()
        self.rotation = 0
        self.__bothSides = bothSides
        self.redis_client = redis_client
        self.__init_unicornhat()
        self.font = ImageFont.truetype(str(pathlib.Path().resolve() / "resources/5x7.ttf"), 8)
        self.__time_offset = 0
        self.__animation_fps = 30
        self.__init_buttons()
        self.__weather_view.setup()
        self.__mode = 0

    def run(self):
        time_behind = 0
        time_behind_max = 0.5
        secs_per_frame = 1 / led_options.get('fps', 10)
        while True:
            loop_start_time = time.time()
            if(self.__mode == TIME_MODE):
                self.time_animation()
                self.unicornhatmini.show()
            elif(self.__mode == WEATHER_MODE):
                self.weather_animation()
            elif(self.__mode == UNICORN_MODE):
                self.unicorn_animation()

            time.sleep(1/self.__unicorn_fps if self.__mode == UNICORN_MODE else 0.1)

    def weather_animation(self):
        self.__weather_view.draw()

    def unicorn_animation(self):
        self.__unicorn_step += 1
        for x in range(0, self.display_width):
            for y in range(0, self.display_height):
                dx = (math.sin(self.__unicorn_step / self.display_width + 20) * self.display_height) + self.display_height
                dy = (math.cos(self.__unicorn_step / self.display_height) * self.display_height) + self.display_height
                sc = (math.cos(self.__unicorn_step / self.display_height) * self.display_height) + self.display_width

                hue = math.sqrt(math.pow(x - dx, 2) + math.pow(y - dy, 2)) / sc
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1, 1)]

                self.unicornhatmini.set_pixel(x, y, r, g, b)
        self.unicornhatmini.show()

    def time_animation(self):
        current_time = time.strftime("%H:%M", time.gmtime())
        image = self.__draw_text(current_time)
        for y in range(self.display_height):
            for x in range(self.display_width):
                hue = (time.time() / 10.0) + (x / float(self.display_width * 2))
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                if image.getpixel((x - self.__time_offset, y)) == 255:
                    self.unicornhatmini.set_pixel(x, y, r, g, b)
                else:
                    self.unicornhatmini.set_pixel(x, y, 0, 0, 0)

        self.__time_offset += 1
        if self.__time_offset + self.display_width > image.size[0]:
            self.__time_offset = 0

    def __init_buttons(self):
        button_a = Button(BUTTON_A)
        button_b = Button(BUTTON_B)
        # button_x = Button(BUTTON_X)
        button_y = Button(BUTTON_Y)
        try:
            button_a.when_pressed = self.__button_callback
            button_b.when_pressed = self.__button_callback
            # button_x.when_pressed = self.__button_callback
            button_y.when_pressed = self.__button_callback
        except KeyboardInterrupt:
            button_a.close()
            button_b.close()
            # button_x.close()
            button_y.close()

    def __button_callback(self, button):
        pin = button.pin.number
        if(pin == 5):
            self.__mode = 0 if self.__mode + 1 == MODE_COUNT else self.__mode + 1
            if(self.__mode == WEATHER_MODE):
                self.__weather_view.setup()
        time.sleep(0.1)

    def __init_unicornhat(self):
        self.unicornhatmini = UnicornHATMini(bothSectors=self.__bothSides, spi_max_speed_hz=6000)
        self.unicornhatmini.clear()
        self.unicornhatmini.set_rotation(self.rotation)
        self.unicornhatmini.set_brightness(0.1)
        self.display_width, self.display_height = self.unicornhatmini.get_shape()
        self.__weather_view = WeatherView(self.unicornhatmini, self.display_width, self.display_height, self.redis_client)

    def __draw_text(self, text):
        text_width, text_height = self.font.getsize(text)
        image = Image.new('P', (text_width + self.display_width + self.display_width, self.display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((self.display_width, -1), text, font=self.font, fill=255)
        image = ImageOps.flip(image)
        image = ImageOps.mirror(image)
        return image