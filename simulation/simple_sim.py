import time
#from rpi_ws281x import PixelStrip, Color
import argparse
#import serial
import requests
import json
import socketio
import asyncio
from LEDStrip import LEDStrip
from PaintApp import PaintingApp
from TicTacToeApp import TicTacToeApp
from ChessApp import ChessApp
import numpy as np
from PIL import Image
from neopixel_neomatrix import Adafruit_NeoMatrix
from AnimationApp import AnimationApp
import threading
from BrickShooterApp import BrickShooterApp
from TugOfWarApp import TugOfWarApp
from SimonSaysApp import SimonSaysApp
from MenuApp import MenuApp
from PongApp import PongApp
from StackerApp import StackerApp
from ImageShowApp import ImageShowApp

device_ID = 0
touch_arr = [0] * 192
sio = socketio.AsyncClient()
ip = 'http://172.20.20.20:5000/'
received_data = "0"
grid_loc = [0, 0]
last_pressed_index = -1
pressed_index = -1
strip = 0
apps = {}
current_app = 'Menu'
sim_index = 0
sim_array = [
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
stored_grid = []
json_array = {"array": touch_arr}
grid_select = 1
last_four_unique_inputs = [(-1, -1)] * 4
touch_index = 0
data_array = []


async def connect_to_server():
    await sio.connect(ip)
    print(sio.sid)
    await sio.sleep(1)


async def simulation_input(strip):
    global apps, current_app, sim_index, last_four_unique_inputs, touch_index
    while True:
        if (apps[current_app].IS_TIMER_BASED):
            apps[current_app].move()
            await asyncio.sleep(apps[current_app].SPEED)
        if (strip.new_touch == 1):
            apps[current_app].paint(
                strip.new_touch_cord[0],
                strip.new_touch_cord[1])
            strip.pixels.gui.new_touch = 0
            if ((strip.new_touch_cord[0], strip.new_touch_cord[1])
                    != last_four_unique_inputs[touch_index]):
                if (touch_index >= 3):
                    touch_index = 0
                else:
                    touch_index = touch_index + 1
                last_four_unique_inputs[touch_index] = (
                    strip.new_touch_cord[0], strip.new_touch_cord[1])
                if ((0, 0) in last_four_unique_inputs and (11, 0) in last_four_unique_inputs and (
                        0, 15) in last_four_unique_inputs and (11, 15) in last_four_unique_inputs):
                    current_app = 'Menu'
                    apps['Menu'].setup_menu()
        await asyncio.sleep(0.1)


def array_convert(grid):
    blank_array = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blank_array[convert(i, j)] = grid[i + j * 12]
    return blank_array


def grid_make():
    global data_array, data_rotate
    image = Image.open('../images/pixel.png')
    image = image.rotate(180)
    image = image.convert('RGB')
    data = image.getdata()
    data_array = list(data)
    data_array = array_convert(data_array)
    image = image.save("mario.png")


def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y


def rgb_to_hex(r, g, b):
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


async def main_program(strip):
    while True:
        global grid_select, stored_grid, apps, current_app
        if (current_app == 'Menu' and apps['Menu'].new_app_selected == 1):
            current_app = apps['Menu'].next_app
        if (grid_select == 1):
            selected_grid = apps[current_app].touch_grid
        elif (grid_select == 0):
            selected_grid = data_array
        loop = asyncio.get_event_loop()
        if (stored_grid != selected_grid):
            await strip.update_buffer(selected_grid)
            strip.json_array["array"] = array_convert(strip.touch_array)
            r = requests.post(
                ip + '/array?id=' + str(device_ID),
                json=json.dumps(
                    strip.json_array))
            stored_grid = selected_grid.copy()
        await asyncio.sleep(0.1)


async def update_sim(strip):
    while True:
        strip.show()
        await asyncio.sleep(0.1)


async def main(strip):
    await connect_to_server()
    asyncio.create_task(main_program(strip))
    asyncio.create_task(update_sim(strip))
    asyncio.create_task(simulation_input(strip))


@sio.on('my_response')
async def catch_all(data):
    if (data['data']['deviceID'] == device_ID):
        global apps, current_app
        readFrom = data['data']
        read_color = readFrom['color']
        newColor = (int(read_color[1:3], 16), int(
            read_color[3:5], 16), int(read_color[5:7], 16))
        apps[current_app].web_paint(readFrom['index'], newColor)


@sio.on('appChange')
async def change_app(data):
    global current_app
    if (data['data']['deviceID'] == device_ID):
        current_app = data['data']['appName']


@sio.on('connected')
async def onConnected(data):
    global device_ID
    print(data['deviceID'])
    device_ID = data['deviceID']
    apps['Menu'].device_ID = device_ID
    apps['Menu'].setup_menu()


@sio.on('sendimg')
async def receive(file):
    if (current_app == 'Image Show'):
        apps[current_app].read_new(file)


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
        'Menu': MenuApp(0),
        'Painting': PaintingApp(),
        'tictactoe': TicTacToeApp(),
        'chess': ChessApp(),
        'animation': AnimationApp(),
        'Brick Shooter': BrickShooterApp(),
        'Simon Says': SimonSaysApp(),
        'Tug of War': TugOfWarApp(),
        'Pong': PongApp(),
        'Image Show': ImageShowApp(),
        'Stacker': StackerApp()}
    # Create led_strip object with appropriate configuration.
    strip = Adafruit_NeoMatrix()
    grid_make()
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
