import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import requests
import json
import socketio
import asyncio
from led_strip import led_strip

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
sio = socketio.AsyncClient()


async def connectToServer():
    await sio.connect('http://10.18.227.28:5000')
    await sio.sleep(1)

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


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


clearingMode = 1
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

async def mainProgram(strip, clearingMode, setColors):
    while True:
        loop = asyncio.get_event_loop()
        received_data = await loop.run_in_executor(None, readUART, ser)
        gridLoc = await loop.run_in_executor(None, interpretUART, received_data)

        #print(gridLoc)
        n = await loop.run_in_executor(None, convert, gridLoc[0], gridLoc[1])
        if gridLoc[1] == 15:
            if gridLoc[0] < 8:
                strip.stored_R, strip.stored_G, strip.stored_B = setColors[gridLoc[0]]
            elif gridLoc[0] == 8:
                strip.stored_B = strip.stored_B + 10
                if strip.stored_B < 50 or strip.stored_B == 260:
                    strip.stored_B = 50
            elif gridLoc[0] == 9:
                strip.stored_G = strip.stored_G + 10
                if strip.stored_G < 50 or strip.stored_G == 260:
                    strip.stored_G = 50
            elif gridLoc[0] == 10:
                strip.stored_R = strip.stored_R + 10
            if strip.stored_R < 50 or strip.stored_R == 260:
                strip.stored_R = 50
            strip.stored_color = Color(strip.stored_R, strip.stored_G, strip.stored_B)
            n = await loop.run_in_executor(None, convert, 11, 15)
            await loop.run_in_executor(None, strip.turn_on_led, n, strip.stored_color)
            clearingMode = (gridLoc[0] == 7)
            strip.send_color = await loop.run_in_executor(None, rgbToHex, strip.stored_R, strip.stored_G, strip.stored_B)
            #touchArr[n] = sendColor
        else:
            #touchArr[n] = rgbToHex(storedR, storedG, storedB)
            await loop.run_in_executor(None, strip.turn_on_led, n, strip.stored_color)

            if(clearingMode):
                strip.send_color = await loop.run_in_executor(None, rgbToHex, 80, 80, 80)
            elif (strip.stored_R == strip.stored_G and strip.stored_R == strip.stored_B):
                strip.send_color = await loop.run_in_executor(None, rgbToHex, 255, 255, 255)
            else:
                strip.send_color = await loop.run_in_executor(None, rgbToHex, strip.stored_R, strip.stored_G, strip.stored_B)
        strip.touch_array[n] = strip.send_color

        strip.json_array["array"] = strip.touch_array
        #print(json.dumps(json_array))
        r = requests.post('http://10.18.227.28:5000/array', json=json.dumps(strip.json_array))
        await asyncio.sleep(1)


async def main(strip, clearingMode, setColors):
    await connectToServer()
    asyncio.create_task(mainProgram(strip, clearingMode, setColors))

strip = 0

@sio.on('my_response')
async def catch_all(data, strip):
    readFrom = data['data']
    readColor = readFrom['color']
    newColor = Color(int(readColor[1:2], 16), int(readColor[3:4], 16), int(readColor[5:6], 16))
    strip.turn_on_led(readFrom['index'], newColor)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create led_strip object with appropriate configuration.
    strip = led_strip()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(strip, clearingMode, setColors))
        loop.run_forever()


    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, Color(0, 0, 0))