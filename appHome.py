import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import requests
import json
import socketio
import asyncio
from led_strip import led_strip
from paintApp import paintingApp
import numpy as np
from PIL import Image

ser = serial.Serial("/dev/ttyS0", 115200)    #Open port with baud rate
touchArr = [0]*192
sio = socketio.AsyncClient()
ip = 'http://10.19.148.197:5000'
received_data = "0"
gridLoc = [0,0]
lastPressedIndex = -1
pressedIndex = -1
strip = 0

async def connectToServer():
    await sio.connect(ip)
    await sio.sleep(1)

json_array = {"array": touchArr}

gridSelect = 0

def readUART(pApp):
    received_data = ser.read()              #read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    global gridLoc
    gridLoc = interpretUART(received_data)
    global pressedIndex
    global gridSelect
    if (gridSelect == 1):
        pApp.paint(gridLoc[0], gridLoc[1])
    pressedIndex = convert(gridLoc[0],gridLoc[1])
    return received_data


def interpretUART(uartData):
    dataEnd = uartData.index(b'\r\n')
    gridLocString = uartData[0:dataEnd]
    gridLocString = gridLocString.decode('utf-8')
    firstValEnd = gridLocString.index(',')
    gridLoc = [int(gridLocString[3:firstValEnd]), int(gridLocString[firstValEnd+5:])]
    return gridLoc

data_array = []

def arrayConvert(grid):
    blankArray = [(0,0,0)]*192
    for i in range(12):
        for j in range(16):
            blankArray[convert(i,j)] = grid[i+j*12]
    return blankArray
    #return [[m[j][i] for j in range(len(m))] for i in range(len(m[0])-1,-1,-1)]

def gridMake():
    global data_array, data_rotate
    image = Image.open('pixel.png')
    image = image.rotate(180)
    # convert image to numpy array
    image = image.convert('RGB')
    data = image.getdata()
    data_array = list(data)
    print(data_array)
    data_array = arrayConvert(data_array)
    image = image.save("mario.png")
    print(data_array)


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)

DRAWING = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[200,200,200],[200,200,200],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[200,200,200],[200,200,200],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
           [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]


async def mainProgram(strip, pApp):
    while True:
        global gridSelect
        if (gridSelect == 1):
            selectedGrid = pApp.touchGrid
        elif (gridSelect == 0):
            selectedGrid = data_array
        loop = asyncio.get_event_loop()
        '''for i in range(0, len(selectedGrid)):
            R = selectedGrid[i][0]
            G = selectedGrid[i][1]
            B = selectedGrid[i][2]
            color = Color(R, G, B)
            await loop.run_in_executor(None, strip.turn_on_led, i, color)
            strip.send_color = await loop.run_in_executor(None, rgbToHex, R, G, B)
            strip.touch_array[i] = strip.send_color
        '''
        await strip.update_buffer(selectedGrid)
        strip.json_array["array"] = arrayConvert(strip.touch_array)
        r = requests.post(ip + '/array', json=json.dumps(strip.json_array))
        await asyncio.sleep(0.1)


async def main(strip, pApp):
    await connectToServer()
    asyncio.create_task(mainProgram(strip, pApp))

@sio.on('my_response')
async def catch_all(data):
    print("Okay: ", data)
    readFrom = data['data']
    print("okay 2: ", readFrom)
    readColor = readFrom['color']
    newColor = Color(int(readColor[1:3], 16), int(readColor[3:5], 16), int(readColor[5:7], 16))
    strip.turn_on_led(readFrom['index'], newColor)
    strip.touch_array[readFrom['index']] = newColor

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    pApp = paintingApp()
    # Create led_strip object with appropriate configuration.
    strip = led_strip()
    gridMake()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(ser, readUART, pApp)
        loop.run_until_complete(main(strip, pApp))
        loop.run_forever()


    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, Color(0, 0, 0))