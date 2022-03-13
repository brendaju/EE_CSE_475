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
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI
# /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 5

set_colors = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (148, 0, 211),
    (255, 255, 255),
    (0, 0, 0)
]


class LEDStrip:
    def __init__(self):
        """
        Initializes the strip and sets strips stored states to zero
        """
        # Create NeoPixel object with appropriate configuration.
        self.Strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                                LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.Strip.begin()
        self.num_pixels = self.Strip.numPixels()
        self.stored_color = Color(0, 0, 0)
        self.send_color = self.rgb_to_hex(0, 0, 0)
        self.stored_R = 0
        self.stored_G = 0
        self.stored_B = 0
        self.touch_array = [0] * 192
        self.json_array = {"array": self.touch_array}

        for i in range(self.num_pixels):
            self.turn_on_led(i, Color(0, 0, 0))

    def rgb_to_hex(self, r, g, b):
        """
        Converts from RGB to HEX
        """
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def color_wipe(self, color, wait_ms=50):
        """
        Wipe color across display a pixel at a time.
        """
        for i in range(self, self.num_pixels):
            # print(i)
            self.Strip.setPixelColor(i, color)
            self.Strip.show()
            #time.sleep(wait_ms / 1000.0)

    def turn_on_led(self, n, color, wait_ms=50):
        """
        Turns on a specified led
        """
        self.Strip.setPixelColor(n, color)
        self.Strip.show()
        #time.sleep(wait_ms / 1000.0)

    async def update_buffer(self, grid):
        """
        Updates the strip buffer
        """
        for i in range(0, len(grid)):
            R = grid[i][0]
            G = grid[i][1]
            B = grid[i][2]
            color = Color(R, G, B)
            self.Strip.setPixelColor(i, color)
            self.send_color = self.rgb_to_hex(R, G, B)
            self.touch_array[i] = self.send_color
        self.Strip.show()

    def convert(self, x, y):
        """
        Converts from x and y to index in our led array
        """
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y
