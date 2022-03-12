import time
from rpi_ws281x import PixelStrip, Color
import argparse
import serial
import requests
import json
import socketio
import asyncio
from LEDStrip import LEDStrip
import numpy as np
from PIL import Image
import threading

# Needed to allow for apps to imported from upper directory
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

# App imports
from apps.MenuApp import MenuApp
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

# Device ID for the website connection
device_ID = 0
ser = serial.Serial("/dev/ttyS0", 115200)  # Open port with baud rate
touch_arr = [0] * 192
sio = socketio.AsyncClient()
# The website ip address
ip = 'http://10.19.76.51:5000'
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
sim_array = ['Menu', 'Painting', 'tictactoe', 'chess', 'animation',
            'Brick Shooter', 'Tug of War', 'Simon Says', 'Pong', 'Image Show', 'Stacker']

async def connect_to_server():
    '''
    Connects to the remote web app server
    '''
    await sio.connect(ip)
    await sio.sleep(1)

# The json array sent to the website
json_array = {"array": touch_arr}

# Allows for testing the pixel grid by choosing between app grids or a user
# made grid
grid_select = 1

# Used to track the last four inputs to go back to the menu
last_four_unique_inputs = [(-1, -1)] * 4
touch_index = 0


def read_UART():
    '''
    Reads the UART data from STM32 and converts it to the grid location
    Also sends this to the proper app or determines if the "back to menu" sequence 
    was performed
    '''
    global grid_loc, pressed_index, grid_select, apps, current_app, touch_index, last_four_unique_inputs
    received_data = ser.read()  # read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()  # check for remaining byte
    received_data += ser.read(data_left)
    ser.write(received_data)
    grid_loc = interpret_UART(received_data)
    global pressed_index
    global grid_select
    if (grid_select == 1):
        apps[current_app].paint(grid_loc[0], grid_loc[1])
    # Menu App Logic
    if ((grid_loc[0], grid_loc[1]) != last_four_unique_inputs[touch_index]):
        if (touch_index >= 3):
            touch_index = 0
        else:
            touch_index = touch_index + 1
        last_four_unique_inputs[touch_index] = (grid_loc[0], grid_loc[1])

        # Checks if "back to menu" sequence was performed. Sequence is each corner of the grid 
        if ((0, 0) in last_four_unique_inputs and (11, 0) in last_four_unique_inputs and (
                0, 15) in last_four_unique_inputs and (11, 15) in last_four_unique_inputs):
            current_app = 'Menu'
            apps['Menu'].setup_menu()

    pressed_index = convert(grid_loc[0], grid_loc[1])
    return received_data

def interpret_UART(uart_data):
    '''
    Converts the UART data to the grid_loc format of [x, y]
    '''
    data_end = uart_data.index(b'\r\n')
    grid_loc_string = uart_data[0:data_end]
    grid_loc_string = grid_loc_string.decode('utf-8')
    first_val_end = grid_loc_string.index(',')
    grid_loc = [int(grid_loc_string[3:first_val_end]),
               int(grid_loc_string[first_val_end + 5:])]
    return grid_loc

data_array = []

async def timer_reaction():
    '''
    If an app has timer based movement, for example animation, this advances
    the animation by the apps set speed. Otherwise it does nothing
    '''
    while True:
        if (apps[current_app].IS_TIMER_BASED):
            apps[current_app].move()
            await asyncio.sleep(apps[current_app].SPEED)
        else:
            await asyncio.sleep(.01)

def array_convert(grid):
    '''
    Used to convert the grid to have another format 
    '''
    blank_array = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blank_array[convert(i, j)] = grid[i + j * 12]
    return blank_array

def convert(x, y):
    '''
    Converts an inputed x, y value to the equivalent index in the
    pixel array
    '''
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex


def rgb_to_hex(r, g, b):
    '''
    Converts a given rgb value to a hex format
    in the form: #FFFFFF
    '''
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


stored_grid = []


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
            # array_convert(strip.touch_array)
            strip.json_array["array"] = strip.touch_array
            r = requests.post(ip + '/array?id=' + str(device_ID),
                              json=json.dumps(strip.json_array))
            stored_grid = selected_grid.copy()
        await asyncio.sleep(0.1)


async def main(strip):
    '''
    Starts the process for the board by first waiting for a connection to the server.
    Then activates the main_program and timer_reaction functions which run until
    the board is turned off
    '''
    await connect_to_server()
    asyncio.create_task(main_program(strip))
    asyncio.create_task(timer_reaction())


@sio.on('my_response')
async def response(data):
    '''
    Listens to the website and takes an input
    if the website data has the same deviceID as the board
    This input is then passed to the web_paint function of the current app
    to allow for the web user to interact with the board
    '''
    if (data['data']['deviceID'] == device_ID):
        global apps, current_app
        read_from = data['data']
        #print("okay 2: ", read_from)
        read_color = read_from['color']
        new_color = (int(read_color[1:3], 16), int(
            read_color[3:5], 16), int(read_color[5:7], 16))
        apps[current_app].web_paint(read_from['index'], new_color)


@sio.on('appChange')
async def change_app(data):
    '''
    Listens to the app change socket of the website.
    This allows the web user to change the app on the board
    '''
    global current_app
    if (data['data']['deviceID'] == device_ID):
        current_app = data['data']['appName']


@sio.on('connected')
async def on_connected(data):
    '''
    When the board connects to the website, it will be sent a device ID
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


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true',
                        help='clear the display on exit')
    args = parser.parse_args()
    # pApp = TicTacToeApp()
    apps = {'Menu': MenuApp(0), 'Painting': PaintingApp(), 'tictactoe': TicTacToeApp(), 'chess': ChessApp(), 'animation': AnimationApp(), 'Brick Shooter': BrickShooterApp(
    ), 'Simon Says': SimonSaysApp(), 'Tug of War': TugOfWarApp(), 'Pong': PongApp(), 'Image Show': ImageShowApp(), 'Stacker': StackerApp()}
   # Create LED_Strip object with appropriate configuration.
    strip = LEDStrip()
    # ()
    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(ser, read_UART)
        loop.run_until_complete(main(strip))
        loop.run_forever()

    except KeyboardInterrupt:
        if args.clear:
            strip.color_wipe(strip, Color(0, 0, 0))