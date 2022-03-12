import time
#from rpi_ws281x import PixelStrip, Color
import argparse
#import serial
import requests
import json
import socketio
import asyncio
from neopixel_neomatrix import Adafruit_NeoMatrix
from PIL import Image

# Needed to allow for apps to imported from upper directory
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

# App imports
from MenuApp import MenuApp
from apps.PaintApp import PaintingApp
from apps.TicTacToeApp import TicTacToeApp
from apps.ChessApp import ChessApp
from apps.AnimationApp import AnimationApp
from apps.BrickShooterApp import BrickShooterApp
from apps.TugOfWarApp import TugOfWarApp
from apps.SimonSaysApp import SimonSaysApp
from apps.PongApp import PongApp
from apps.StackerApp import StackerApp
from apps.ImageShowApp import ImageShowApp

import numpy as np
import threading

# Device ID for the website connection
device_ID = 0
touch_arr = [0] * 192
sio = socketio.AsyncClient()
# The website ip address
ip = 'http://192.168.0.11:5000/'
# Data received from the UART connection to the STM32
received_data = "0"
# Converted touch grid location from STM32 [x, y]
grid_loc = [0, 0]
last_pressed_index = -1
pressed_index = -1
strip = 0

# Variables to allow for each app to be switch between
apps = {}
current_app = 'Menu'

# Values used to allow for the simulation to change between apps
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

# The json array sent to the website
json_array = {"array": touch_arr}

# Allows for testing the pixel grid by choosing between app grids or a user
# made grid
grid_select = 1

# Used to track the last four inputs to go back to the menu
last_four_unique_inputs = [(-1, -1)] * 4
touch_index = 0
data_array = []


async def connect_to_server():
    '''
    Connects to the remote web app server
    '''
    await sio.connect(ip)
    print(sio.sid)
    await sio.sleep(1)


async def simulation_input(strip):
    '''
    Takes the simulation inputs and passes them to the appropriate app. Also allows
    for the user to either go back to the menu by clicking the four corners or switch apps
    by right clicking
    '''
    global apps, current_app, sim_index, last_four_unique_inputs, touch_index
    while True:
        # If the app is timer based runs the code as well as the user input code
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
    '''
    Used to convert the grid to have another format 
    '''
    blank_array = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blank_array[convert(i, j)] = grid[i + j * 12]
    return blank_array


def grid_make():
    '''
    Creates an example 192 index grid from an imported image
    '''
    global data_array, data_rotate
    image = Image.open('../images/pixel.png')
    image = image.rotate(180)
    image = image.convert('RGB')
    data = image.getdata()
    data_array = list(data)
    data_array = array_convert(data_array)
    image = image.save("mario.png")


def convert(x, y):
    '''
    Converts an inputed x, y value to the equivalent index in the
    pixel array
    '''
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y


def rgb_to_hex(r, g, b):
    '''
    Converts a given rgb value to a hex format
    in the form: #FFFFFF
    '''
    numbers = [r, g, b]
    return '#' + ''.join('{:02X}'.format(a) for a in numbers)


async def main_program(strip):
    '''
    The main program of the array which updates the pixel grid and strip based on the 
    current app as well as sends the updated array to the website as a json post
    If the current app is a menu, it also handles moving to the next app if it was selected
    '''
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
    '''
    Updates the simulation screen
    '''
    while True:
        strip.show()
        await asyncio.sleep(0.1)


async def main(strip):
    '''
    Starts the process for the simulation by first waiting for a connection to the server.
    Then activates the main_program, update_sim, and timer_reaction functions which run until
    the simulation is turned off
    '''
    await connect_to_server()
    asyncio.create_task(main_program(strip))
    asyncio.create_task(update_sim(strip))
    asyncio.create_task(simulation_input(strip))


@sio.on('my_response')
async def catch_all(data):
    '''
    Listens to the website and takes an input
    if the website data has the same deviceID as the simulation
    This input is then passed to the web_paint function of the current app
    to allow for the web user to interact with the simulation
    '''
    if (data['data']['deviceID'] == device_ID):
        global apps, current_app
        readFrom = data['data']
        read_color = readFrom['color']
        newColor = (int(read_color[1:3], 16), int(
            read_color[3:5], 16), int(read_color[5:7], 16))
        apps[current_app].web_paint(readFrom['index'], newColor)


@sio.on('appChange')
async def change_app(data):
    '''
    Listens to the app change socket of the website.
    This allows the web user to change the app on the simulation
    '''
    global current_app
    if (data['data']['deviceID'] == device_ID):
        current_app = data['data']['appName']


@sio.on('connected')
async def onConnected(data):
    '''
    When the simulation connects to the website, it will be sent a device ID
    This sets the Menu apps device_ID value to the websites device ID
    and re-runs the setup_menu function to show the new device ID
    '''
    global device_ID
    print(data['deviceID'])
    device_ID = data['deviceID']
    apps['Menu'].device_ID = device_ID
    apps['Menu'].setup_menu()


@sio.on('sendimg')
async def receive(file):
    '''
    Takes in the latest loaded image from the website for the
    Image Show app
    '''
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
