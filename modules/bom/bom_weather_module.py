# -*- coding: UTF-8 -*-
""" Shows weather conditions for the current day from the Australian
    Bureau of Meteorology
"""

import time
from os import remove

import pygame

import config.settings as settings
import config.translations as translations
from debug_output import timestamp


class BOMWeatherModule(object):
    """Displays weather data from the Australian Bureau of Meteorology"""

    def __init__(self, width, height, colour):
        timestamp("Initialising BOMWeatherModule module...")
        self.url = "ftp://ftp2.bom.gov.au/anon/gen/fwo/IDA00100.dat"
        self.width, self.height = width, height
        self.colour = colour
        self.fonts = self.getfonts()
        self.savepath = settings.saved_weather_data_path
        self.weatherdata = None
        self.connectionattempts = 0
        self.nextupdatetime = time.time()

    def update(self):
        """Returns updated weather display"""
        return self.parse_weather_info()

    def need_update(self):
        """Returns true if update required"""
        if time.time() >= self.nextupdatetime:
            self.nextupdatetime = time.time() + settings.weather_update_delay
            return True
        else:
            return False

    def parse_weather_info(self):
        """Parses the weather from the BOM data file"""

        # Planned features:
        #  - Ability to use multiple services

        # Catch errors from python 2
        try:
            # noinspection PyUnboundLocalVariable
            FileNotFoundError
        except NameError:
            # noinspection PyPep8Naming,PyShadowingBuiltins
            FileNotFoundError = IOError

        try:
            with open(settings.saved_weather_data_path, "r") as save_data:
                # Get elapsed time since update and check against update delay:
                last_check = self.nextupdatetime - float(save_data.readline())
                if last_check > settings.weather_update_delay:
                    # Raises to trigger data update in except clause:
                    raise FileNotFoundError("Old file")
                else:
                    self.weatherdata = str(save_data.read())
        # Exception if weather_data can't be opened:
        except FileNotFoundError:
            self.ioerror()
            return self.parse_weather_info()
        except ValueError:
            remove(settings.saved_weather_data_path)
            self.ioerror()
            return self.parse_weather_info()
        string, result = "", []
        index = self.weatherdata.find(settings.weather_city.title())
        while True:
            string += self.weatherdata[index]
            index += 1
            if self.weatherdata[index] == "#":
                result.append(string[1:])
                string = ""
            if self.weatherdata[index] == "\n":
                break
        desc = result[-1].lower()
        condition = [item for item in translations.conditions
                     if desc.find(item) != -1]
        if len(condition) > 0:
            icon = translations.conditions[condition[0]]
        else:
            icon = u""
        temp = result[-2]
        desc = result[-1].title()
        item = (
            self.fonts[1].render(settings.weather_city, 1, self.colour),
            self.fonts[2].render(icon[0], 1, self.colour),
            self.fonts[3].render(desc, 1, self.colour),
            self.fonts[0].render("{}\xb0c".format(temp), 1, self.colour)
        )
        heights = (
            item[0].get_rect(left=0, top=0)[3],
            item[1].get_rect(left=0, top=0)[3] * 0.8,
            item[2].get_rect(left=0, top=0)[3],
            item[3].get_rect(left=0, top=0)[3]
        )
        itempos = (
            item[0].get_rect(left=self.width / 100, top=0),
            item[1].get_rect(left=self.width / 100, top=heights[0] * 0.5),
            item[2].get_rect(left=self.width / 100, top=sum(heights[0:2])),
            item[3].get_rect(left=self.width / 100, top=sum(heights[0:3]))
        )
        return (
            (item[0], itempos[0]),
            (item[1], itempos[1]),
            (item[2], itempos[2]),
            (item[3], itempos[3])
        )

    # noinspection PyCompatibility,PyCompatibility
    def ioerror(self):
        """Called in the case of a file read error. Re-downloads the file"""
        timestamp("Save file read error occurred. Trying again.")
        try:
            from urllib.request import Request, urlopen, URLError
        # For python 2 compatibility:
        except ImportError:
            # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
            from urllib2 import Request, urlopen, URLError
        try:
            with open(settings.saved_weather_data_path, "w") as save_data:
                weatherurl = urlopen(Request(self.url))
                self.weatherdata = weatherurl.read().decode("utf-8")
                save_data.write(str(self.nextupdatetime))
                save_data.write("\n{}".format(self.weatherdata))
        except URLError:
            self.ioerror()

    def getfonts(self):
        """Returns the fonts for the module"""
        fonts = [pygame.font.Font(ttf, int(size * self.height))
                 for ttf, size in settings.fonts]
        return fonts[2], fonts[1], fonts[5], fonts[3]
