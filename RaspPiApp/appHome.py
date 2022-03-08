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
from tictactoeApp import tictactoeApp
from chessApp import chessApp
import numpy as np
from PIL import Image
from animation import animation_app
import time
import threading
from brick_shooter import brick_shooter_app
from tugofwarApp import tugofwarApp
from simonsaysApp import simonsaysApp
from menuApp import menuApp
from pong import pong_app
from stacker import stacker_app
from imageshowApp import imageshowApp

deviceID = 0
ser = serial.Serial("/dev/ttyS0", 115200)  # Open port with baud rate
touchArr = [0] * 192
sio = socketio.AsyncClient()
ip = 'http://10.19.76.51:5000'
received_data = "0"
gridLoc = [0, 0]
lastPressedIndex = -1
pressedIndex = -1
strip = 0
apps = {}
currentApp = 'Menu'
simIndex = 0
simArray = ['Menu', 'Painting', 'tictactoe', 'chess', 'animation',
            'Brick Shooter', 'Tug of War', 'Simon Says', 'Pong', 'Image Show', 'Stacker']


async def connectToServer():
    await sio.connect(ip)
    await sio.sleep(1)

json_array = {"array": touchArr}

gridSelect = 1

lastFourUniqueInputs = [(-1, -1)] * 4
touchIndex = 0


def readUART():
    global gridLoc, pressedIndex, gridSelect, apps, currentApp, touchIndex, lastFourUniqueInputs
    received_data = ser.read()  # read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()  # check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    gridLoc = interpretUART(received_data)
    global pressedIndex
    global gridSelect
    if (gridSelect == 1):
        apps[currentApp].paint(gridLoc[0], gridLoc[1])
    print(gridLoc[0], gridLoc[1])
    # Menu App Logic
    if ((gridLoc[0], gridLoc[1]) != lastFourUniqueInputs[touchIndex]):
        if (touchIndex >= 3):
            touchIndex = 0
        else:
            touchIndex = touchIndex + 1
        lastFourUniqueInputs[touchIndex] = (gridLoc[0], gridLoc[1])
        if ((0, 0) in lastFourUniqueInputs and (11, 0) in lastFourUniqueInputs and (
                0, 15) in lastFourUniqueInputs and (11, 15) in lastFourUniqueInputs):
            currentApp = 'Menu'
            apps['Menu'].setup_menu()

    pressedIndex = convert(gridLoc[0], gridLoc[1])
    return received_data


def interpretUART(uartData):
    dataEnd = uartData.index(b'\r\n')
    gridLocString = uartData[0:dataEnd]
    gridLocString = gridLocString.decode('utf-8')
    firstValEnd = gridLocString.index(',')
    gridLoc = [int(gridLocString[3:firstValEnd]),
               int(gridLocString[firstValEnd + 5:])]
    return gridLoc


data_array = []


async def timerReaction():
    while True:
        if (apps[currentApp].IS_TIMER_BASED):
            apps[currentApp].move()
            print("move")
            await asyncio.sleep(apps[currentApp].SPEED)
        else:
            await asyncio.sleep(.01)


def arrayConvert(grid):
    blankArray = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blankArray[convert(i, j)] = grid[i + j * 12]
    return blankArray


    # return [[m[j][i] for j in range(len(m))] for i in
    # range(len(m[0])-1,-1,-1)]
'''
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
'''


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex


def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


DRAWING = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [200, 200, 200], [200, 200, 200], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [200, 200, 200], [200, 200, 200], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [
               0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
           [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]


storedGrid = []


async def mainProgram(strip):
    while True:
        global gridSelect, storedGrid, apps, currentApp
        if (currentApp == 'Menu' and apps['Menu'].newAppSelected == 1):
            currentApp = apps['Menu'].nextApp
        if (gridSelect == 1):
            selectedGrid = apps[currentApp].touchGrid
        elif (gridSelect == 0):
            selectedGrid = data_array
        loop = asyncio.get_event_loop()
        if (storedGrid != selectedGrid):
            await strip.update_buffer(selectedGrid)
            # arrayConvert(strip.touch_array)
            strip.json_array["array"] = strip.touch_array
            r = requests.post(ip + '/array?id=' + str(deviceID),
                              json=json.dumps(strip.json_array))
            storedGrid = selectedGrid.copy()
        await asyncio.sleep(0.1)


async def main(strip):
    await connectToServer()
    asyncio.create_task(mainProgram(strip))
    asyncio.create_task(timerReaction())


@sio.on('my_response')
async def response(data):
    print(data)
    if (data['data']['deviceID'] == deviceID):
        global apps, currentApp
        readFrom = data['data']
        #print("okay 2: ", readFrom)
        readColor = readFrom['color']
        newColor = (int(readColor[1:3], 16), int(
            readColor[3:5], 16), int(readColor[5:7], 16))
        apps[currentApp].webPaint(readFrom['index'], newColor)


@sio.on('appChange')
async def changeApp(data):
    print(data)
    global currentApp
    if (data['data']['deviceID'] == deviceID):
        currentApp = data['data']['appName']


@sio.on('connected')
async def onConnected(data):
    global deviceID
    print(data['deviceID'])
    # await sio.emit('deviceConnected', {'foo': 'bar'})
    deviceID = data['deviceID']
    apps['Menu'].deviceID = deviceID
    apps['Menu'].setup_menu()


@sio.on('sendimg')
async def receive(file):
    if (currentApp == 'Image Show'):
        apps[currentApp].read_new(file)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true',
                        help='clear the display on exit')
    args = parser.parse_args()
    # pApp = tictactoeApp()
    apps = {'Menu': menuApp(0), 'Painting': paintingApp(), 'tictactoe': tictactoeApp(), 'chess': chessApp(), 'animation': animation_app(), 'Brick Shooter': brick_shooter_app(
    ), 'Simon Says': simonsaysApp(), 'Tug of War': tugofwarApp(), 'Pong': pong_app(), 'Image Show': imageshowApp(), 'Stacker': stacker_app()}
   # Create led_strip object with appropriate configuration.
    strip = led_strip()
    # ()
    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(ser, readUART)
        loop.run_until_complete(main(strip))
        loop.run_forever()

    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, Color(0, 0, 0))
