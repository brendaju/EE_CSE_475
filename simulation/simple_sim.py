import time
#from rpi_ws281x import PixelStrip, Color
import argparse
#import serial
import requests
import json
import socketio
import asyncio
#from led_strip import led_strip
from paintApp import paintingApp
from tictactoeApp import tictactoeApp
from chessApp import chessApp
import numpy as np
from PIL import Image
from neopixel_neomatrix import Adafruit_NeoMatrix
from animation import animation_app
import time
import threading


deviceID = 0
#ser = serial.Serial("/dev/ttyS0", 115200)    #Open port with baud rate
touchArr = [0]*192
sio = socketio.AsyncClient()
ip = 'http://10.19.148.197:5000/'
received_data = "0"
gridLoc = [0,0]
lastPressedIndex = -1
pressedIndex = -1
strip = 0
apps = []
currentApp = 2

async def connectToServer():
    await sio.connect(ip)
    await sio.sleep(1)

json_array = {"array": touchArr}

gridSelect = 1

def readUART():
    global gridLoc, pressedIndex, gridSelect, apps, currentApp
    received_data = ser.read()              #read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    gridLoc = interpretUART(received_data)
    global pressedIndex
    global gridSelect
    if (gridSelect == 1):
        apps[currentApp].paint(gridLoc[0], gridLoc[1])
    pressedIndex = convert(gridLoc[0],gridLoc[1])
    return received_data

IS_TIMER_BASED = False
SPEED = 0.1

async def simulationInput(strip):
    global apps, currentApp
    while True:
        if (IS_TIMER_BASED):
            apps[currentApp].paint()
            await asyncio.sleep(SPEED)
        elif (strip.new_touch == 1):
            apps[currentApp].paint(strip.new_touch_cord[0], strip.new_touch_cord[1])
            strip.pixels.gui.new_touch = 0
            if (strip.was_right_click):
                currentApp = currentApp + 1
                if (currentApp > 3):
                    currentApp = 0
                strip.pixels.gui.was_right_click = False
        await asyncio.sleep(0.1)

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
    image = Image.open('../images/pixel.png')
    image = image.rotate(180)
    # convert image to numpy array
    image = image.convert('RGB')
    data = image.getdata()
    data_array = list(data)
    #print(data_array)
    data_array = arrayConvert(data_array)
    image = image.save("mario.png")
    #print(data_array)


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)

storedGrid = []
async def mainProgram(strip):
    while True:
        global gridSelect, storedGrid, apps, currentApp
        if (gridSelect == 1):
            selectedGrid = apps[currentApp].touchGrid
        elif (gridSelect == 0):
            selectedGrid = data_array
        loop = asyncio.get_event_loop()
        if (storedGrid != selectedGrid):
            await strip.update_buffer(selectedGrid)
            strip.json_array["array"] = arrayConvert(strip.touch_array)
            r = requests.post(ip + '/array?id='+str(deviceID), json=json.dumps(strip.json_array))
            storedGrid = selectedGrid.copy()
        await asyncio.sleep(0.1)

async def updateSim(strip):
    while True:
        strip.show()
        await asyncio.sleep(0.1)

async def main(strip):
    await connectToServer()
    asyncio.create_task(mainProgram(strip))
    asyncio.create_task(updateSim(strip))
    asyncio.create_task(simulationInput(strip))

@sio.on('my_response')
async def catch_all(data):
    if (data['data']['deviceID'] == deviceID):
        global apps, currentApp
        #print("Okay: ", data)
        readFrom = data['data']
        #print("okay 2: ", readFrom)
        readColor = readFrom['color']
        newColor = (int(readColor[1:3], 16), int(readColor[3:5], 16), int(readColor[5:7], 16))
        apps[currentApp].webPaint(readFrom['index'], newColor)

@sio.on('connected')
async def onConnected(data):
    global deviceID
    print(data['deviceID'])
    deviceID = data['deviceID']

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    # pApp = tictactoeApp()
    apps = [paintingApp(), tictactoeApp(), chessApp(), animation_app()]
    # Create led_strip object with appropriate configuration.
    strip = Adafruit_NeoMatrix()
    gridMake()
    strip.show()
    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        #loop.add_reader(ser, readUART, pApp)
        loop.run_until_complete(main(strip))
        loop.run_forever()


    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, Color(0, 0, 0))