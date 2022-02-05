import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import request

# LED strip configuration:
LED_COUNT = 192        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 5

ser = serial.Serial("/dev/ttyS0", 115200)    #Open port with baud rate
touchArr = [0]*192

json_arr = {"array": touchArr}

def readUART(ser):
    received_data = ser.read()              #read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    return received_data

def interpretUART(uartData):
    gridLocString = uartData.replace(b'\x00',b'')
    gridLocString = gridLocString.replace(b'\xff',b'')
    gridLocString = gridLocString.replace(b'\r',b'')
    gridLocString = gridLocString.replace(b'\n',b'')
    gridLocString = gridLocString.decode('utf-8')
    firstValEnd = gridLocString.index(',')

    gridLoc = [int(gridLocString[3:firstValEnd]), int(gridLocString[firstValEnd+5:])]
    return gridLoc

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

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


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
            print("Testing turn on correct")
            
            #n = convert(2,2)
            #turn_on_led(strip, n, Color(200, 200, 200))
            
            # n1 = convert(4,4)
            # turn_on_led(strip, n1, Color(200, 200, 200))
            
            # n2 = convert(0,0)
            # turn_on_led(strip, n2, Color(200, 200, 200))
            
            # n3 = convert(10,13)
            # turn_on_led(strip, n3, Color(200, 200, 200))

            received_data = readUART(ser)
            gridLoc = interpretUART(received_data)
            

            n = convert(gridLoc[0], gridLoc[1])
            touchArr[n] = rgbToHex(200,5,10)
            turn_on_led(strip, n, Color(200, 200, 200))
            
            json_array[name] = touchArr
            r = requests.post('http://10.19.80.19/array', json=json_array)


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0))
