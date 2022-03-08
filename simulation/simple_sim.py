import argparse
import requests
import json
import socketio
import asyncio
from paintApp import paintingApp
from tictactoeApp import tictactoeApp
from chessApp import chessApp
from PIL import Image
from neopixel_neomatrix import Adafruit_NeoMatrix
from animation import animation_app
from brick_shooter import brick_shooter_app
from tugofwarApp import tugofwarApp
from simonsaysApp import simonsaysApp
from menuApp import menuApp
from pong import pong_app
from stacker import stacker_app
from imageshowApp import imageshowApp

deviceID = 0
touchArr = [0] * 192
sio = socketio.AsyncClient()
ip = 'http://10.19.76.51:5000/'
received_data = "0"
gridLoc = [0, 0]
lastPressedIndex = -1
pressedIndex = -1
strip = 0
apps = {}
currentApp = 'Menu'
simIndex = 0
simArray = [
    'Menu',
    'Painting',
    'tictactoe',
    'chess',
    'animation',
    'Brick Shooter',
    'Tug of War',
    'Simon Says',
    'Pong',
    'Image Show',
    'Stacker']
storedGrid = []
json_array = {"array": touchArr}
gridSelect = 1
lastFourUniqueInputs = [(-1, -1)] * 4
touchIndex = 0
data_array = []


async def connectToServer():
    await sio.connect(ip)
    print(sio.sid)
    await sio.sleep(1)


async def simulationInput(strip):
    global apps, currentApp, simIndex, lastFourUniqueInputs, touchIndex
    while True:
        if (apps[currentApp].IS_TIMER_BASED):
            apps[currentApp].move()
            await asyncio.sleep(apps[currentApp].SPEED)
        if (strip.new_touch == 1):
            apps[currentApp].paint(
                strip.new_touch_cord[0],
                strip.new_touch_cord[1])
            strip.pixels.gui.new_touch = 0
            if ((strip.new_touch_cord[0], strip.new_touch_cord[1])
                    != lastFourUniqueInputs[touchIndex]):
                if (touchIndex >= 3):
                    touchIndex = 0
                else:
                    touchIndex = touchIndex + 1
                lastFourUniqueInputs[touchIndex] = (
                    strip.new_touch_cord[0], strip.new_touch_cord[1])
                if ((0, 0) in lastFourUniqueInputs and (11, 0) in lastFourUniqueInputs and (
                        0, 15) in lastFourUniqueInputs and (11, 15) in lastFourUniqueInputs):
                    currentApp = 'Menu'
                    apps['Menu'].setup_menu()
        await asyncio.sleep(0.1)


def arrayConvert(grid):
    blankArray = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blankArray[convert(i, j)] = grid[i + j * 12]
    return blankArray


def gridMake():
    global data_array, data_rotate
    image = Image.open('../images/pixel.png')
    image = image.rotate(180)
    image = image.convert('RGB')
    data = image.getdata()
    data_array = list(data)
    data_array = arrayConvert(data_array)
    image = image.save("mario.png")


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y


def rgbToHex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


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
            strip.json_array["array"] = arrayConvert(strip.touch_array)
            r = requests.post(
                ip + '/array?id=' + str(deviceID),
                json=json.dumps(
                    strip.json_array))
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
        readFrom = data['data']
        readColor = readFrom['color']
        newColor = (int(readColor[1:3], 16), int(
            readColor[3:5], 16), int(readColor[5:7], 16))
        apps[currentApp].webPaint(readFrom['index'], newColor)


@sio.on('appChange')
async def changeApp(data):
    global currentApp
    if (data['data']['deviceID'] == deviceID):
        currentApp = data['data']['appName']


@sio.on('connected')
async def onConnected(data):
    global deviceID
    print(data['deviceID'])
    deviceID = data['deviceID']
    apps['Menu'].deviceID = deviceID
    apps['Menu'].setup_menu()


@sio.on('sendimg')
async def receive(file):
    if (currentApp == 'Image Show'):
        apps[currentApp].read_new(file)


if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--clear',
        action='store_true',
        help='clear the display on exit')
    args = parser.parse_args()
    apps = {
        'Menu': menuApp(0),
        'Painting': paintingApp(),
        'tictactoe': tictactoeApp(),
        'chess': chessApp(),
        'animation': animation_app(),
        'Brick Shooter': brick_shooter_app(),
        'Simon Says': simonsaysApp(),
        'Tug of War': tugofwarApp(),
        'Pong': pong_app(),
        'Image Show': imageshowApp(),
        'Stacker': stacker_app()}
    # Create led_strip object with appropriate configuration.
    strip = Adafruit_NeoMatrix()
    gridMake()
    strip.show()
    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(strip))
        loop.run_forever()

    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, (0, 0, 0))
