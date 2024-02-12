import os
from dataclasses import fields
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
import numpy as np
import ST7735

class LCD:

    COLORS = ((20, 255, 20), (200, 200, 0), (255, 0, 0))

    def __init__(self):
        # Initialize LCD screen
        self.__st7735 = ST7735.ST7735(
            port=0,
            cs=1,
            dc=9,
            backlight=12,
            rotation=270,
            spi_speed_hz=10000000
        )
        self.__st7735.begin()
        self.__width = self.__st7735.width
        self.__height = self.__st7735.height
        # Set up drawing canvas and font
        self.__image = Image.new('RGB', (self.__width, self.__height),
                                 color=(0, 0, 0))
        self.__icons = self.__load_resources('resources')
        self.__canvas = ImageDraw.Draw(self.__image)
        font_size = 9
        self.__font = ImageFont.truetype(UserFont, font_size)

    def display(self, data):
        x = 1
        y = 2
        self.__canvas.rectangle((0, 0, self.__width, self.__height),
                                (255, 255, 255))
        i = 0
        data_fields = list(fields(data))
        del data_fields[0]
        for field in data_fields:
            message = "%.1f" %  getattr(data, field.name).value + \
                " %s" % getattr(data, field.name).unit.value
            self.__canvas.text((x, y + 27), message, font=self.__font,
                               fill=(125, 125, 0))
            j = 0
            for limit in getattr(data, field.name).limits:
                if(getattr(data, field.name).value < limit):
                    break
                j += 1
            color = self.COLORS[j]
            if(type(self.__icons[field.name]) is list):
                if(j >= len(self.__icons[field.name])):
                    j = len(self.__icons[field.name]) - 1
                self.__canvas.bitmap((x,y), self.__icons[field.name][j],
                                     fill=color)
            else:
                self.__canvas.bitmap((x,y), self.__icons[field.name],
                                     fill=color)
            if(i % 2 == 0):
                y = 40
            else:
                x += 41
                y = 2
            i += 1
        self.__st7735.display(self.__image)

    def __load_resources(self, directory):
        bitmaps = {}
        for filename in os.listdir(directory):
            if(filename.endswith('.png')):
                if(len(filename.split('-')) > 1):
                    pattern = filename.split('-')[0]
                    matched_list = []
                    for f in os.listdir(directory):
                        if(pattern in f):
                            matched_list.append(f)
                    matched_list = sorted(matched_list)
                    bitmap_list = [self.__read_bitmap(
                        os.path.join(directory, file)) for file in matched_list]
                    bitmaps[filename.split('-')[0]] = bitmap_list
                    continue
                bitmaps[filename.split('.')[0]] = \
                    self.__read_bitmap('resources/%s' % filename)
        return bitmaps

    def __read_bitmap(self, filename):
        png_source = Image.open(filename)
        png_np = np.array(png_source)
        _, png_grayscale = np.split(png_np,2,axis=2)
        png_grayscale = png_grayscale.reshape(-1)
        bitmap = np.array(png_grayscale).reshape([png_np.shape[0],
                                                  png_np.shape[1]])
        bitmap = np.dot((bitmap > 128).astype(float),255)
        return Image.fromarray(bitmap.astype(np.uint8))