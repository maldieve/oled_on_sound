#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Unicode font rendering & scrolling.
"""

import os
import random
import sys
import requests
import pprint
import time
import RPi.GPIO as GPIO
from datetime import datetime, timedelta 
from demo_opts import get_device
from luma.core.virtual import viewport, snapshot, range_overlap
from luma.core.sprite_system import framerate_regulator
from PIL import ImageFont
#from weather import Weather, Unit

reload(sys)  
sys.setdefaultencoding('utf8')

GPIO.setmode(GPIO.BCM)
channel = 18
GPIO.setup(channel, GPIO.IN)

class LastClap:
    lastClap = 0

    def setLastClap(self, clap):
        self.lastClap = clap

    def getLastClap(self):
        return self.lastClap

def callback(channel):
        if GPIO.input(channel):
                lastClap.setLastClap(0)
        else:
                lastClap.setLastClap(0)

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

class Unit:
    CELSIUS = 'c'
    FAHRENHEIT = 'f'

class Weather(object):
    URL = 'http://query.yahooapis.com/v1/public/yql'
    
    def __init__(self, unit=Unit.CELSIUS):
        self.unit = unit

    def lookup(self, woeid):
        url = "%s?q=select * from weather.forecast where woeid = '%s' and u='%s' &format=json" % (self.URL, woeid, self.unit)
        results = self._call(url)
        return results

    def lookup_by_location(self, location):
        url = "%s?q=select* from weather.forecast " \
              "where woeid in (select woeid from geo.places(1) where text='%s') and u='%s' &format=json" % (self.URL, location, self.unit)
        results = self._call(url)
        return results

    @staticmethod
    def _call(url):
        req = requests.get(url)

        if not req.ok:
            req.raise_for_status()

        results = req.json()

        if int(results['query']['count']) > 0:
            wo = WeatherObject(results['query']['results']['channel'])
            return wo
        else:
            pprint.pprint(results)

class Location(object):
    def __init__(self, location_data):
        self._location_data = location_data

    def city(self):
        return self._location_data['city']

    def country(self):
        return self._location_data['country']
        
    def region(self):
        return self._location_data['region']

class Forecast(object):
    def __init__(self, forecast_data):
        self._forecast_data = forecast_data

    def text(self):
        return self._forecast_data['text']

    def date(self):
        return self._forecast_data['date']

    def high(self):
        return self._forecast_data['high']

    def low(self):
        return self._forecast_data['low']

class Condition(object):
    def __init__(self, condition_data):
        self._condition_data = condition_data

    def date(self):
        return self._condition_data['date']

    def text(self):
        return self._condition_data['text']

    def code(self):
        return self._condition_data['code']

    def temp(self):
        return self._condition_data['temp']

class WeatherObject(object):
    def __init__(self, weather_data):
        self._weather_data = weather_data

    def last_build_date(self):
        return self._weather_data['lastBuildDate']

    def title(self):
        return self._weather_data['title']

    def description(self):
        return self._weather_data['description']

    def language(self):
        return self._weather_data['language']

    def astronomy(self):
        return self._weather_data['astronomy']

    def atmosphere(self):
        return self._weather_data['atmosphere']

    def image(self):
        return self._weather_data['image']

    def condition(self):
        return Condition(self._weather_data['item']['condition'])

    def forecast(self):
        forecasts = []
        [forecasts.append(Forecast(res)) for res in self._weather_data['item']['forecast']]
        return forecasts

    def latitude(self):
        return self._weather_data['item']['lat']

    def longitude(self):
        return self._weather_data['item']['long']

    def location(self):
        return Location(self._weather_data['location'])

    def units(self):
        return self._weather_data['units']

    def wind(self):
        return self._weather_data['wind']

    def print_obj(self):
        return self._weather_data

colors = [
    "lightpink", "pink", "crimson", "lavenderblush", "palevioletred", "hotpink",
    "deeppink", "mediumvioletred", "orchid", "thistle", "plum", "violet",
    "magenta", "fuchsia", "darkmagenta", "purple", "mediumorchid", "darkviolet",
    "darkorchid", "indigo", "blueviolet", "mediumpurple", "mediumslateblue",
    "slateblue", "darkslateblue", "lavender", "ghostwhite", "blue", "mediumblue",
    "midnightblue", "darkblue", "navy", "royalblue", "cornflowerblue",
    "lightsteelblue", "lightslategray", "slategray", "dodgerblue", "aliceblue",
    "steelblue", "lightskyblue", "skyblue", "deepskyblue", "lightblue",
    "powderblue", "cadetblue", "azure", "lightcyan", "paleturquoise", "cyan",
    "aqua", "darkturquoise", "darkslategray", "darkcyan", "teal",
    "mediumturquoise", "lightseagreen", "turquoise", "aquamarine",
    "mediumaquamarine", "mediumspringgreen", "mintcream", "springgreen",
    "mediumseagreen", "seagreen", "honeydew", "lightgreen", "palegreen",
    "darkseagreen", "limegreen", "lime", "forestgreen", "green", "darkgreen",
    "chartreuse", "lawngreen", "greenyellow", "darkolivegreen", "yellowgreen",
    "olivedrab", "beige", "lightgoldenrodyellow", "ivory", "lightyellow",
    "yellow", "olive", "darkkhaki", "lemonchiffon", "palegoldenrod", "khaki",
    "gold", "cornsilk", "goldenrod", "darkgoldenrod", "floralwhite", "oldlace",
    "wheat", "moccasin", "orange", "papayawhip", "blanchedalmond", "navajowhite",
    "antiquewhite", "tan", "burlywood", "bisque", "darkorange", "linen", "peru",
    "peachpuff", "sandybrown", "chocolate", "saddlebrown", "seashell", "sienna",
    "lightsalmon", "coral", "orangered", "darksalmon", "tomato", "mistyrose",
    "salmon", "snow", "lightcoral", "rosybrown", "indianred", "red", "brown",
    "firebrick", "darkred", "maroon", "white", "whitesmoke", "gainsboro",
    "lightgrey", "silver", "darkgray", "gray", "dimgray", "black"
]


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)


def lerp_1d(start, end, n):
    delta = float(end - start) / float(n)
    for i in range(n):
        yield int(round(start + (i * delta)))
    yield end


def lerp_2d(start, end, n):
    x = lerp_1d(start[0], end[0], n)
    y = lerp_1d(start[1], end[1], n)

    try:
        while True:
            yield next(x), next(y)
    except StopIteration:
        pass


def pairs(generator):
    try:
        last = next(generator)
        while True:
            curr = next(generator)
            yield last, curr
            last = curr
    except StopIteration:
        pass


def infinite_shuffle(arr):
    copy = list(arr)
    while True:
        random.shuffle(copy)
        for elem in copy:
            yield elem


def make_snapshot(width, height, text, fonts, color="white"):

    def render(draw, width, height):
        t = text

        for font in fonts:
            size = draw.multiline_textsize(t, font)
            if size[0] > width:
                t = text.replace(" ", "\n")
                size = draw.multiline_textsize(t, font)
            else:
                break

        left = (width - size[0]) // 2
        top = (height - size[1]) // 2
        draw.multiline_text((left, top), text=t, font=font, fill=color,
                            align="center", spacing=-2)

    return snapshot(width, height, render, interval=10)


def random_point(maxx, maxy):
    return random.randint(0, maxx), random.randint(0, maxy)


def overlapping(pt_a, pt_b, w, h):
    la, ta = pt_a
    ra, ba = la + w, ta + h
    lb, tb = pt_b
    rb, bb = lb + w, tb + h
    return range_overlap(la, ra, lb, rb) and range_overlap(ta, ba, tb, bb)

def main():
    weather = Weather(unit=Unit.CELSIUS)
    location = weather.lookup_by_location('Boksburg, Gauteng, South Africa')
    condition = location.condition()
    print(condition.text())
    forecasts = location.forecast()
    forecast = forecasts[0]
    regulator = framerate_regulator(fps=30)
    fonts = [make_font("code2000.ttf", sz) for sz in range(24, 8, -2)]
    sq = device.width * 3
    virtual = viewport(device, sq, sq)

    color_gen = pairs(infinite_shuffle(colors))

    reRead = 0
    while True:
        if (lastClap.getLastClap() < 10):
            device.show()
            tm = datetime.now() + timedelta(hours=2)
        
            if (reRead > 270):
                reRead = 0
                location = weather.lookup_by_location('Boksburg, Gauteng, South Africa')
                condition = location.condition()
                print(condition.text())
                forecasts = location.forecast()
                forecast = forecasts[0]

            welcome_a = tm.strftime("%e %b %Y")
            welcome_b = "-----" + condition.temp() + u"°C-----" + " " + forecast.low() + u"°C" +"-" + forecast.high() + u"°C " + condition.text()
            welcome_c = tm.strftime("%X") 
            color_a, color_b = next(color_gen)
            color_c, color_b = next(color_gen)
            widget_a = make_snapshot(device.width, device.height, welcome_a, fonts, color_a)
            widget_b = make_snapshot(device.width, device.height, welcome_b, fonts, color_b)
            widget_c = make_snapshot(device.width, device.height, welcome_c, fonts, color_c)

            posn_a = random_point(virtual.width - device.width, virtual.height - device.height)
            posn_b = random_point(virtual.width - device.width, virtual.height - device.height)
            posn_c = random_point(virtual.width - device.width, virtual.height - device.height)

            while overlapping(posn_a, posn_b, device.width, device.height):
                posn_b = random_point(virtual.width - device.width, virtual.height - device.height)

            while overlapping(posn_b, posn_c, device.width, device.height):
                posn_c = random_point(virtual.width - device.width, virtual.height - device.height)

            while overlapping(posn_c, posn_a, device.width, device.height):
                posn_a = random_point(virtual.width - device.width, virtual.height - device.height)

            virtual.add_hotspot(widget_a, posn_a)
            virtual.add_hotspot(widget_b, posn_b)
            virtual.add_hotspot(widget_c, posn_c)

            for _ in range(30):
                with regulator:
                    virtual.set_position(posn_a)

            for posn in lerp_2d(posn_a, posn_b, device.width // 4):
                with regulator:
                    virtual.set_position(posn)

            time.sleep( 2 )

            for posn in lerp_2d(posn_b, posn_c, device.width // 4):
                with regulator:
                    virtual.set_position(posn)

            virtual.remove_hotspot(widget_a, posn_a)
            virtual.remove_hotspot(widget_b, posn_b)
            virtual.remove_hotspot(widget_c, posn_c)
            reRead += 1
            lastClap.setLastClap(1 + lastClap.getLastClap())
            time.sleep( 4 )
        else:
            device.hide()


if __name__ == "__main__":
    try:
        device = get_device()
        lastClap = LastClap()
        main()
    except KeyboardInterrupt:
        pass
