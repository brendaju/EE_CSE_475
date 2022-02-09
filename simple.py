import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import requests
import json

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

json_array = {"array": touchArr}

def readUART(ser):
    received_data = ser.read()              #read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    return received_data

def interpretUART(uartData):
    dataEnd = uartData.index(b'\r\n')
    #gridLocString = uartData.replace(b'\x00',b'')
    #gridLocString = gridLocString.replace(b'\xff',b'')
    #gridLocString = gridLocString.replace(b'\r',b'')
    #gridLocString = gridLocString.replace(b'\n',b'')
    gridLocString = uartData[0:dataEnd]
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


storedR = 0
storedG = 0
storedB = 0
clearingMode = 1
storedColor = Color(0, 0, 0)
sendColor = rgbToHex(0,0,0)
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

def setupPainting(strip, touchArr):
    '''turn_on_led(strip, convert(0, 15), Color(255, 0, 0))
    turn_on_led(strip, convert(1, 15), Color(255, 127, 0))
    turn_on_led(strip, convert(2, 15), Color(255, 255, 0))
    turn_on_led(strip, convert(3, 15), Color(0, 255, 0))
    turn_on_led(strip, convert(4, 15), Color(0, 0, 255))
    turn_on_led(strip, convert(6, 15), Color(148, 0, 211))
    turn_on_led(strip, convert(7, 15), Color(255, 255, 255))'''
    
    for i in range(8):
        n = convert(i, 15)
        turn_on_led(strip, n, Color(setColors[i][0], setColors[i][1], setColors[i][2]))
        touchArr[n] = rgbToHex(setColors[i][0], setColors[i][1], setColors[i][2])
    turn_on_led(strip, convert(8,15), Color(0, 0, 255))
    touchArr[convert(8, 15)] = rgbToHex(0, 0, 255)
    turn_on_led(strip, convert(9,15), Color(0, 255, 0))
    touchArr[convert(9, 15)] = rgbToHex(0, 255, 0)
    turn_on_led(strip, convert(10,15), Color(255, 0, 0))
    touchArr[convert(10, 15)] = rgbToHex(255, 0, 0)

    turn_on_led(strip, convert(11,15), storedColor)
    touchArr[convert(11, 15)] = rgbToHex(storedR, storedG, storedB)

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
    
    for i in range(192):
        turn_on_led(strip, i, Color(0,0,0))
    setupPainting(strip, touchArr)

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
            
            print(gridLoc)
            n = convert(gridLoc[0], gridLoc[1])
            if gridLoc[1] == 15:
                if gridLoc[0] < 8:
                    storedR, storedG, storedB = setColors[gridLoc[0]]
                elif gridLoc[0] == 8:
                    storedB = storedB + 10
                    if storedB < 50 or storedB == 260:
                        storedB = 50
                elif gridLoc[0] == 9:
                    storedG = storedG + 10
                    if storedG < 50 or storedG == 260:
                        storedG = 50
                elif gridLoc[0] == 10:
                    storedR = storedR + 10
                    if storedR < 50 or storedR == 260:
                        storedR = 50
                storedColor = Color(storedR, storedG, storedB)
                n = convert(11, 15)
                turn_on_led(strip, n, storedColor)
                clearingMode = (gridLoc[0] == 7)
                sendColor = rgbToHex(storedR, storedG, storedB)
                #touchArr[n] = sendColor
            else:
                #touchArr[n] = rgbToHex(storedR, storedG, storedB)
                turn_on_led(strip, n, storedColor)
                
            if(clearingMode):
                sendColor = rgbToHex(80, 80, 80)
            elif (storedR == storedG and storedR == storedB):
                sendColor = rgbToHex(255, 255, 255)
            else:
                sendColor = rgbToHex(storedR, storedG, storedB)
            touchArr[n] = sendColor

            json_array["array"] = touchArr
            print(json.dumps(json_array))
            try:
                r = requests.post('http://10.19.103.196:5000/array', json=json.dumps(json_array))
            except Exception as ex:
                print('Error, is flask site on?')


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0))
