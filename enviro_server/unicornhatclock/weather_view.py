import os
import sys
import time
import datetime
from json import loads
import pytz
from threading import Timer
from enviro_server.unicornhatclock.sprite_cache import cache, import_sprite
from enviro_server.unicornhatclock.led import Led
from enviro_server.unicornhatclock.options import clock_options

def get_time(timezone):
    return datetime.datetime.now(pytz.timezone(timezone))

def mirror(seq):
    output = list(seq[::-1])
    return output

frame_rate = {
    'disconnected': 1,
    'loading': 10,
    'sun': 0.5,
    'sun and cloud': 0.5,
    'sun and haze': 0.5,
    'clouds': 0.25,
    'fog': 2,
    'rain': 5,
    'rain and cloud': 5,
    'storm': 10,
    'snow': 2,
    'snow and cloud': 2,
    'hot': 5,
    'cold': 5,
    'wind': 5,
    'moon': 5,
    'moon and cloud': 0.125,
    'moon and haze': 0.125,
}

TWELVE_HR_FORMAT = clock_options.get('12hrFormat', False)
OMIT_LEADING_ZERO = clock_options.get('omitLeadingZeros', False)
DEMO = clock_options.get('demo', False)
COLOR = clock_options.get('color', [255, 255, 255])

filters = [('multiply', COLOR)]

class WeatherView:
    def __init__(self, unicornhat, width, height, redis_client):
        self.led = Led(unicornhat, width, height)
        digits_path = os.path.join('enviro_server', 'unicornhatclock', 'sprites', 'digits.png')
        import_sprite(digits_path, (3, 5), 1)
        self.__state = False
        self.__clock_state = False

        sprites_path = os.path.join('enviro_server', 'unicornhatclock', 'sprites', 'weather_icons')
        sprites_list = os.listdir(sprites_path)

        for filename in sprites_list:
            sprite_path = os.path.join(sprites_path, filename)
            import_sprite(sprite_path, (9, 9))
        self.redis_client = redis_client
        self.__weather = None
        self.__clock_timer = Timer(5.0, self.clock_callback)

    def setup(self):
        try:
            self.__timer.cancel()
        except:
            pass
        self.led.setup()
        self.__timer = Timer(10.0, self.timer_callback)
        self.__timer.start()

    def timer_callback(self):
        self.__clock_timer.cancel()
        self.__state = not self.__state
        self.__timer = Timer(10.0, self.timer_callback)
        self.__timer.start()
        self.__clock_timer = Timer(5.0, self.clock_callback)
        self.__clock_timer.start()

    def clock_callback(self):
        self.__clock_state = not self.__clock_state
        self.__clock_timer = Timer(5.0, self.clock_callback)
        self.__clock_timer.start()

    def draw_time(self):
        now = get_time(self.timezone)
        hour, minute = now.hour, now.minute
        if TWELVE_HR_FORMAT:
            twelve_hour = hour % 12
            if twelve_hour == 0:
                hour_str = '12'
            else:
                hour_str = str(twelve_hour).zfill(2)
        else:
            hour_str = str(hour).zfill(2)
        minute_str = str(minute).zfill(2)

        # Draw hour digits
        hour_x_offset = 0
        if(not self.__clock_state):
            if not (OMIT_LEADING_ZERO and int(hour_str[0]) == 0):
                self.led.draw_frame(mirror(cache['digits'][int(hour_str[0])]),
                            0 + hour_x_offset, 0, filters)
            self.led.draw_frame(mirror(cache['digits'][int(hour_str[1])]),
                    4 + hour_x_offset, 0, filters)
        else:
            # # # # Draw minute digits
            self.led.draw_frame(mirror(cache['digits'][int(minute_str[0])]), 0, 0, filters)
            self.led.draw_frame(mirror(cache['digits'][int(minute_str[1])]), 4, 0, filters)


    def draw_weather(self):
        weather = self.redis_client.lrange('Weather', -1, -1)
        if(len(weather)):
            self.__weather = loads(weather[0].replace(b'\'', b'\"')) # TODO: Remove?
        if(len(self.__weather)):
            sprite_name = self.__weather["current"]["weather"][0]["icon"]
            weather_sprite = cache.get(sprite_name, None)
            if weather_sprite is None:
                return

            # Get frame
            ticks = int(time.time() * frame_rate.get(sprite_name, 1))
            frame_index = ticks % len(weather_sprite)

            self.led.draw_frame(mirror(weather_sprite[frame_index]), 0, 0)

    def draw(self):
        if(not self.__state):
            self.led.draw_function(self.__weather, self.draw_weather)
        else:
            self.led.draw_function(self.__weather, self.draw_time)

    @property
    def timezone(self):
        return self.__weather["timezone"]
