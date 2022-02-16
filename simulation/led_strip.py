"""
LED Class for Canvas Board
"""

import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import requests
import json
import socketio
import asyncio

# LED strip configuration:
LED_COUNT = 192        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 5

setColors = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (148, 0, 211),
    (255, 255, 255),
    (0, 0, 0)
]

class led_strip:
    def __init__(self):
        # Create NeoPixel object with appropriate configuration.
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.num_pixels = self.strip.numPixels()
        self.stored_color = Color(0, 0, 0)
        self.send_color = self.rgbToHex(0,0,0)
        self.stored_R = 0
        self.stored_G = 0
        self.stored_B = 0
        self.touch_array = [0] * 192
        self.json_array = {"array": self.touch_array}

        for i in range(self.num_pixels):
            self.turn_on_led(i, Color(0,0,0))
       # self.setup_painting()

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def color_wipe(self, color, wait_ms=50):
        """
        Wipe color across display a pixel at a time.
        """
        for i in range(self, self.num_pixels):
            #print(i)
            self.strip.setPixelColor(i, color)
            self.strip.show()
            #time.sleep(wait_ms / 1000.0)

    def turn_on_led(self, n, color, wait_ms=50):
        self.strip.setPixelColor(n, color)
        self.strip.show()
        #time.sleep(wait_ms / 1000.0)

    async def update_buffer(self, grid):
        for i in range(0, len(grid)):
            R = grid[i][0]
            G = grid[i][1]
            B = grid[i][2]
            color = Color(R, G, B)
            self.strip.setPixelColor(i, color)
            self.send_color = self.rgbToHex(R, G, B)
            self.touch_array[i] = self.send_color
        self.strip.show()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    '''def setup_painting(self):
        for i in range(8):
            n = self.convert(i, 15)
            self.turn_on_led(n, Color(setColors[i][0], setColors[i][1], setColors[i][2]))
            self.touch_array[n] = self.rgbToHex(setColors[i][0], setColors[i][1], setColors[i][2])
        self.turn_on_led(self.convert(8,15), Color(0, 0, 255))
        self.touch_array[self.convert(8, 15)] = self.rgbToHex(0, 0, 255)
        self.turn_on_led(self.convert(9,15), Color(0, 255, 0))
        self.touch_array[self.convert(9, 15)] = self.rgbToHex(0, 255, 0)
        self.turn_on_led(self.convert(10,15), Color(255, 0, 0))
        self.touch_array[self.convert(10, 15)] = self.rgbToHex(255, 0, 0)
        self.turn_on_led(self.convert(11,15), self.stored_color)
        self.touch_array[self.convert(11, 15)] = self.rgbToHex(self.stored_R, self.stored_G, self.stored_B)
'''

