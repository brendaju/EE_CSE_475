import time
from rpi_ws281x import PixelStrip, Color
import argparse

# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 5


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        print(i)
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def turn_on_led(strip, n, color, wait_ms=50):
    strip.setPixelColor(n, color)
    strip.show()
    time.sleep(wait_ms / 1000.0)


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    print("Convert:", convert(2, 2))
    print("Convert:", convert(4, 4))
    print("Convert:", convert(0, 0))
    print("Convert:", convert(10, 13))
    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
#             print("Testing turn on correct")
#             n = convert(2,2)
#             turn_on_led(strip, n, Color(200, 200, 200), wait_ms=50)
#             n1 = convert(4,4)
#             turn_on_led(strip, n1, Color(200, 200, 200), wait_ms=50)
#             n2 = convert(0,0)
#             turn_on_led(strip, n2, Color(200, 200, 200), wait_ms=50)
#             n3 = convert(10,13)
#             turn_on_led(strip, n3, Color(200, 200, 200), wait_ms=50)
            colorWipe(strip, Color(255, 0, 0))  # Red wipe


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0))
