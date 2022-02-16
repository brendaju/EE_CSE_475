import asyncio
#from rpi_ws281x import Color

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

def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class paintingApp:
    def __init__(self):
        self.stored_color = Color(0, 0, 0)
        self.clearingMode = 1
        self.send_color = self.rgbToHex(0,0,0)
        self.stored_R = 0
        self.stored_G = 0
        self.stored_B = 0
        self.touchGrid = [(0,0,0)]*192
        self.setup_painting()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_painting(self):
        for i in range(8):
            n = self.convert(i, 15)
            self.touchGrid[n] = (setColors[i][0], setColors[i][1], setColors[i][2])
        self.touchGrid[self.convert(8, 15)] = (0, 0, 255)
        self.touchGrid[self.convert(9, 15)] = (0, 255, 0)
        self.touchGrid[self.convert(10, 15)] = (255, 0, 0)
        self.touchGrid[self.convert(11, 15)] = (self.stored_R, self.stored_G, self.stored_B)
    
    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        print(x,y)
        print(self.convert(x,y))
        self.touchGrid[self.convert(x,y)] = webColor

    def paint(self, x, y):
        if y == 15:
            if x < 8:
                self.stored_R, self.stored_G, self.stored_B = setColors[x]
            elif x == 8:
                self.stored_B = self.stored_B + 10
                if self.stored_B < 50 or self.stored_B > 255:
                    self.stored_B = 50
            elif x == 9:
                self.stored_G = self.stored_G + 10
                if self.stored_G < 50 or self.stored_G > 255:
                    self.stored_G = 50
            elif x == 10:
                self.stored_R = self.stored_R + 10
                if self.stored_R < 50 or self.stored_R > 255:
                    self.stored_R = 50
            self.touchGrid[176] = (self.stored_R, self.stored_G, self.stored_B)
            self.clearingMode = (x == 7)
            self.send_color = self.rgbToHex(self.stored_R, self.stored_G, self.stored_B)
            print(self.stored_R, self.stored_G, self.stored_B)
            #touchArr[n] = sendColor
        else:
            #touchArr[n] = rgbToHex(storedR, storedG, storedB)
            self.touchGrid[self.convert(x,y)] = (self.stored_R, self.stored_G, self.stored_B)

            if(self.clearingMode):
                self.send_color = '#505050'
            elif (self.stored_R == self.stored_G and self.stored_R == self.stored_B):
                self.send_color = '#FFFFFF'
            else:
                self.send_color = self.rgbToHex(self.stored_R, self.stored_G, self.stored_B)
        #json_array["array"] = touchArr
        #print(json.dumps(json_array))
        #global lastPressedIndex
        #if (pressedIndex != lastPressedIndex):
        #    r = requests.post(ip + '/array', json=json.dumps(json_array))
        #    lastPressedIndex = pressedIndex
        #await loop.run_in_executor(None, show, matrix)
        #show(matrix)
        #await asyncio.sleep(0.1)