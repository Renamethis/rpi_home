from copy import deepcopy
from datetime import datetime, timedelta, timezone
from enviro_server.unicornhatclock.options import led_options

def get_brightness_level(weather):
    now = datetime.now()
    if(weather is not None):
        sunrise = weather["current"]["sunrise"]
        sunset = weather["current"]["sunset"]
    else:
        return 0.5
    if now < datetime.fromtimestamp(sunrise):
        return now.hour / datetime.fromtimestamp(sunrise).hour
    elif now < datetime.fromtimestamp(sunset):
        return 1
    else:
        return 0


class Led:
    def __init__(self, hat, width, height):
        self.hat = hat
        self.width = width
        self.height = height
        self.buffer = []
        self.old_buffer = []

    def map_coords(self, x, y):
        return (self.width - x - 1, y)


    def setup(self):
        self.clear()
        self.old_buffer = deepcopy(self.buffer)


    def draw_frame(self, frame, x, y, filters=[]):
        for y2 in range(len(frame)):
            for x2 in range(len(frame[y2])):

                # Check for out of bounds
                xx2, yy2 = x + x2, y + y2
                if not self.in_bounds(xx2, yy2):
                    continue

                old_px = self.buffer[yy2][xx2]

                in_rgb = self.apply_filters(frame[y2][x2][:3], filters)
                in_alpha = frame[y2][x2][3]

                if in_alpha == 0:
                    continue
                elif in_alpha == 255:
                    add_px = in_rgb
                else:
                    in_alpha = float(in_alpha) / 255
                    add_px = [int(val * in_alpha) for val in in_rgb]

                new_px = [old + new for old, new in zip(old_px, add_px)]
                new_px = [min(max(val, 0), 255) for val in new_px]

                self.buffer[yy2][xx2] = new_px
                # hat.set_pixel(*map_coords(xx2, yy2), *(new_px))


    def apply_filters(self, in_rgb, filters):
        for blend_mode, f_rgb in filters:
            if blend_mode == 'multiply':
                in_rgb = [int(x * (y / 255)) for x, y in zip(in_rgb, f_rgb)]
        return in_rgb


    def set_px(self, x, y, color, filters=[]):
        if self.in_bounds(x, y):
            self.buffer[y][x] = self.apply_filters(color, filters)


    def in_bounds(self, x, y):
        return not (x < 0 or x >= self.width or y < 0 or y >= self.height)


    def clear(self):
        self.buffer = [[[0, 0, 0] for _ in range(self.width)] for y in range(self.height)]
        self.hat.clear()


    def show(self):
        for y in range(self.height):
            for x in range(self.width):
                px = [int(((self.buffer[y][x][i] + self.old_buffer[y][x][i])) / 2)
                    for i in range(3)]
                self.hat.set_pixel(*self.map_coords(x, y), *px)

        self.hat.show()

        self.old_buffer = deepcopy(self.buffer)


    def off(self):
        self.hat.off()

    def set_brightness(self, level):
        min_val, max_val = led_options.get(
            'minBrightness', 0.01), led_options.get('maxBrightness', 1.0)
        brightness = min_val + ((max_val - min_val) * level)
        self.hat.set_brightness(brightness)

    def draw_function(self, weather, draw_func):
        self.clear()
        self.set_brightness(get_brightness_level(weather))
        draw_func()
        self.show()

        # Calculate how long we have left in the loop to sleep
