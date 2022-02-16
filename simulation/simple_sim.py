import time
import neopixel_neomatrix
import argparse
import requests
import json
import socketio
import asyncio

# LED strip configuration:
LED_COUNT = 192        # Number of LED pixels.
#LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 5

touchArr = [0]*192
json_array = {"array": touchArr}

sio = socketio.AsyncClient()
ip = 'http://10.19.148.197:5000'

received_data = "0"
gridLoc = [0,0]
lastPressedIndex = -1
pressedIndex = -1
stored_R, stored_G, stored_B = (0, 0, 0)
send_color = 0

async def connectToServer():
    await sio.connect(ip)
    await sio.sleep(1)

json_array = {"array": touchArr}

def show(matrix):
        matrix.pixels.gui.render()
        matrix.new_touch = matrix.pixels.gui.new_touch
        matrix.new_touch_cord = matrix.pixels.gui.new_touch_cord
        event = matrix.pixels.gui.dispatch_events()

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

async def mainProgram(matrix, clearingMode, setColors):
    while True:
        loop = asyncio.get_event_loop()
        global gridLoc, stored_R, stored_G, stored_B, send_color, touchArr, json_array, pressedIndex
        gridLoc[0] = matrix.new_touch_cord[0]
        gridLoc[1] = matrix.new_touch_cord[1]

        pressedIndex = (gridLoc[0] * 16) + (15 - gridLoc[1] if (gridLoc[0] % 2 != 0) else gridLoc[1])
        #received_data = await loop.run_in_executor(None, readUART, ser)
        #gridLoc = await loop.run_in_executor(None, interpretUART, received_data)
        #print(gridLoc)
        #n = await loop.run_in_executor(None, convert, gridLoc[0], gridLoc[1])
        if gridLoc[1] == 15:
            if gridLoc[0] < 8:
                stored_R, stored_G, stored_B = setColors[gridLoc[0]]
            elif gridLoc[0] == 8:
                stored_B = stored_B + 10
                if stored_B < 50 or stored_B == 260:
                    stored_B = 50
            elif gridLoc[0] == 9:
                stored_G = stored_G + 10
                if stored_G < 50 or stored_G == 260:
                    stored_G = 50
            elif gridLoc[0] == 10:
                stored_R = stored_R + 10
                if stored_R < 50 or stored_R == 260:
                    stored_R = 50
            await loop.run_in_executor(None, matrix.drawPixel, 11, 15, (stored_R, stored_G, stored_B))
            clearingMode = (gridLoc[0] == 7)
            send_color = await loop.run_in_executor(None, rgbToHex, stored_R, stored_G, stored_B)
            #touchArr[n] = sendColor
        else:
            #touchArr[n] = rgbToHex(storedR, storedG, storedB)
            await loop.run_in_executor(None, matrix.drawPixel, gridLoc[0], gridLoc[1], (stored_R, stored_G, stored_B))

            if(clearingMode):
                send_color = '#505050'
            elif (stored_R == stored_G and stored_R == stored_B):
                send_color = '#FFFFFF'
            else:
                send_color = await loop.run_in_executor(None, rgbToHex, stored_R, stored_G, stored_B)
        touchArr[pressedIndex] = send_color

        json_array["array"] = touchArr
        #print(json.dumps(json_array))
        global lastPressedIndex
        if (pressedIndex != lastPressedIndex):
            r = requests.post(ip + '/array', json=json.dumps(json_array))
            lastPressedIndex = pressedIndex
        #await loop.run_in_executor(None, show, matrix)
        show(matrix)
        await asyncio.sleep(0.1)

async def showMatrix(matrix):
    matrix.show()
    matrix.delay(10)
    #await asyncio.sleep(0.1)

async def main(matrix, clearingMode, setColors):
    await connectToServer()
    #asyncio.create_task(showMatrix(matrix))
    asyncio.create_task(mainProgram(matrix, clearingMode, setColors))

strip = 0

@sio.on('my_response')
async def catch_all(data):
    print("Okay: ", data)
    readFrom = data['data']
    print("okay 2: ", readFrom)
    readColor = readFrom['color']
    #newColor = Color(int(readColor[1:3], 16), int(readColor[3:5], 16), int(readColor[5:7], 16))
    #gridLoc[0] * 16) + (15 - gridLoc[1] if (gridLoc[0] % 2 != 0) else gridLoc[1]
    x = int(readFrom['index']/16)
    y = int(readFrom['index'] - x * 16)
    #print(x, y)
    await loop.run_in_executor(None, matrix.drawPixel, x, y, (int(readColor[1:3], 16), int(readColor[3:5], 16), int(readColor[5:7], 16)))
    touchArr[readFrom['index']] = readColor

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

def setup_painting(matrix):
        for i in range(8):
            matrix.drawPixel(i, 15, setColors[i])
            touchArr[(i * 16) + (15 - 15 if (i % 2 != 0) else 15)] = rgbToHex(setColors[i][0], setColors[i][1], setColors[i][2])
        
        matrix.drawPixel(8, 15, (0, 0, 255))
        touchArr[(8 * 16) + (15 - 15 if (8 % 2 != 0) else 15)] = rgbToHex(0,0,255)
        touchArr[(9 * 16) + (15 - 15 if (9 % 2 != 0) else 15)] = rgbToHex(0,255,0)
        touchArr[(10 * 16) + (15 - 15 if (10 % 2 != 0) else 15)] = rgbToHex(255,0,0)
        matrix.drawPixel(9, 15, (0, 255, 0))
        matrix.drawPixel(10, 15, (255, 0 ,0))

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    #args = parser.parse_args()

    # Create led_strip object with appropriate configuration.
    #strip = led_strip()
    matrix = neopixel_neomatrix.Adafruit_NeoMatrix()
    matrix.create_matrix(12,16,6,matrix.positions["NEO_MATRIX_TOP"]+matrix.positions["NEO_MATRIX_LEFT"]+\
        matrix.positions["NEO_MATRIX_COLUMNS"]+matrix.positions["NEO_MATRIX_PROGRESSIVE"])
    matrix.begin()
    matrix.show()
    matrix.drawPixel(0,0,(200, 0, 0))
    matrix.drawPixel(5,5,(200, 0, 100))
    matrix.drawPixel(0,1,(0, 200, 0))
    matrix.drawPixel(0,2,(0, 0, 200))
    matrix.setRotation(0)
    matrix.setBrightness(90)
    matrix.show()
    matrix.delay(10)
    print(matrix.new_touch_cord)
    setup_painting(matrix)

    try:
        loop = asyncio.get_event_loop()
        #loop.add_reader(ser, readUART)
        loop.run_until_complete(main(matrix, clearingMode, setColors))
        loop.run_forever()
    except:
        print("closing")