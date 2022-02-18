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

X_MAX = 16
Y_MAX = 12

def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class animation_app:
    def __init__(self):
        self.touchGrid = [(0,0,0)]*192
        self.x_loc = 0
        self.y_loc = 0
        self.setup()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup(self):
        # convert (column, row)
        self.touchGrid[self.convert(0, 0)] = (255,255,255)

    async def getGrid(self):
        return self.touchGrid

    # Prolly don't work
    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        self.paint(x, y)

    def paint(self, x, y):
        self.touchGrid[self.convert(self.y_loc, self.x_loc)] = (0, 0, 0)
        self.x_loc += 1
        self.y_loc += 1
        if self.x_loc == X_MAX or self.y_loc == Y_MAX:
            self.x_loc = 0
            self.y_loc = 0
        self.touchGrid[self.convert(self.y_loc, self.x_loc)] = (255,255,255)
