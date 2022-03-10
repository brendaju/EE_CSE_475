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

device_ID = 0
ser = serial.Serial("/dev/ttyS0", 115200)  # Open port with baud rate
touch_arr = [0] * 192
sio = socketio.AsyncClient()
ip = 'http://10.19.76.51:5000'
received_data = "0"
grid_loc = [0, 0]
last_pressed_index = -1
pressed_index = -1
strip = 0
apps = {}
current_app = 'Menu'
sim_index = 0
sim_array = ['Menu', 'Painting', 'tictactoe', 'chess', 'animation',
            'Brick Shooter', 'Tug of War', 'Simon Says', 'Pong', 'Image Show', 'Stacker']


async def connect_to_server():
    await sio.connect(ip)
    await sio.sleep(1)

json_array = {"array": touch_arr}

grid_select = 1

last_four_unique_inputs = [(-1, -1)] * 4
touch_index = 0


def read_UART():
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
        if ((0, 0) in last_four_unique_inputs and (11, 0) in last_four_unique_inputs and (
                0, 15) in last_four_unique_inputs and (11, 15) in last_four_unique_inputs):
            current_app = 'Menu'
            apps['Menu'].setup_menu()

    pressed_index = convert(grid_loc[0], grid_loc[1])
    return received_data

def interpret_UART(uart_data):
    data_end = uart_data.index(b'\r\n')
    grid_loc_string = uart_data[0:data_end]
    grid_loc_string = grid_loc_string.decode('utf-8')
    first_val_end = grid_loc_string.index(',')
    grid_loc = [int(grid_loc_string[3:first_val_end]),
               int(grid_loc_string[first_val_end + 5:])]
    return grid_loc

data_array = []

async def timer_reaction():
    while True:
        if (apps[current_app].IS_TIMER_BASED):
            apps[current_app].move()
            await asyncio.sleep(apps[current_app].SPEED)
        else:
            await asyncio.sleep(.01)

def array_convert(grid):
    blank_array = [(0, 0, 0)] * 192
    for i in range(12):
        for j in range(16):
            blank_array[convert(i, j)] = grid[i + j * 12]
    return blank_array

def convert(x, y):
    # if in an odd column, reverse the order
    if (x % 2 != 0):
        y = 15 - y
    return (x * 16) + y

# https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex


def rgb_to_hex(r, g, b):
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
    while True:
        global grid_select, stored_grid, apps, current_app
        if (current_app == 'Menu' and apps['Menu'].new_app_selected == 1):
            current_app = apps['Menu'].nextApp
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
    await connect_to_server()
    asyncio.create_task(main_program(strip))
    asyncio.create_task(timer_reaction())


@sio.on('my_response')
async def response(data):
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
    global current_app
    if (data['data']['deviceID'] == device_ID):
        current_app = data['data']['appName']


@sio.on('connected')
async def on_connected(data):
    global device_ID
    print(data['deviceID'])
    device_ID = data['deviceID']
    apps['Menu'].device_ID = device_ID
    apps['Menu'].setup_menu()


@sio.on('sendimg')
async def receive(file):
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
