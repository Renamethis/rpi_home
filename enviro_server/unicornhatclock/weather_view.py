import os
import sys
import time
import datetime
from json import loads
from enviro_server.unicornhatclock.sprite_cache import cache, import_sprite
from enviro_server.unicornhatclock.led import Led
from enviro_server.unicornhatclock.weather import get_code
from enviro_server.unicornhatclock.options import clock_options

def get_time():
    return datetime.datetime.now()

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

        sprites_path = os.path.join('enviro_server', 'unicornhatclock', 'sprites', 'weather_icons')
        sprites_list = os.listdir(sprites_path)

        for filename in sprites_list:
            sprite_path = os.path.join(sprites_path, filename)
            import_sprite(sprite_path, (9, 9))
        self.redis_client = redis_client
        self.__weather = None

    def setup(self):
        self.led.setup()

    def draw_time(self):

        now = get_time()
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
        if not (OMIT_LEADING_ZERO and int(hour_str[0]) == 0):
            self.led.draw_frame(mirror(cache['digits'][int(hour_str[0])]),
                        0 + hour_x_offset, 0, filters)
        self.led.draw_frame(mirror(cache['digits'][int(hour_str[1])]),
                2 + hour_x_offset, 0, filters)

        # # # Draw minute digits
        self.led.draw_frame(mirror(cache['digits'][int(minute_str[0])]), 4, 0, filters)
        self.led.draw_frame(mirror(cache['digits'][int(minute_str[1])]), 6, 0, filters)


    def draw_weather(self):
        # Get sprite
        # if (DEMO):
        #     sprite_index = int((time.time() / 5) % len(cache.keys()))
        #     sprite_name = list(cache.keys())[sprite_index]
        # else:
        weather = self.redis_client.lrange('Weather', -1, -1)
        if(len(weather)):
            self.__weather = loads(weather[0].replace(b'\'', b'\"'))
        if(len(self.__weather)):
            sprite_name = self.__weather["current"]["weather"][0]["icon"]
            weather_sprite = cache.get(sprite_name, None)
            if weather_sprite is None:
                return

            # Get frame
            ticks = int(time.time() * frame_rate.get(sprite_name, 1))
            frame_index = ticks % len(weather_sprite)

            self.led.draw_frame(mirror(weather_sprite[frame_index]), 0, 0)


    # def draw_blinker():
    #     ticks = get_time().second % 2 == 0
    #     color = [0, 0, 0]
    #     if ticks % 2 == 0:
    #         if get_time_updated():
    #             color = [128, 128, 128]
    #         else:
    #             color = [255, 0, 0] # red
    #     # set_px(0, 15, color, filters)


    def draw(self):
        self.led.draw_function(self.draw_weather)
        # self.draw_weather()
        # draw_blinker()
