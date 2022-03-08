from ast import Not
import asyncio
from shutil import move
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


class stacker:
    def __init__(self):
        self.x_loc = 5
        self.y_loc = 15
        self.length = 3
        self.height = 1
        self.x_max = 12 - self.length
        self.y_max = 15 - self.height


class stacker_app:
    def __init__(self):
        self.touchGrid = [(0, 0, 0)]*192
        self.stacker = stacker()
        self.direction = 1  # 1 - right -1 - left
        self.hasLost = False
        self.hasWon = False
        self.IS_TIMER_BASED = True
        self.SPEED = 0.1
        self.blankColor = (0, 0, 0)
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
        # create target
        # draw slider
        self.stacker = stacker()
        self.SPEED = .1
        self.direction = 1
        self.touchGrid = [(0, 0, 0)]*192
        self.hasLost = False
        self.hasWon = False
        self.endStateGridLocation = 0
        self.draw_stacker()
        self.draw_changeRows()

    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        self.paint(x, y)

    def draw_changeRows(self):
        for i in range(12):
            self.touchGrid[self.convert(i, 8)] = (255, 255, 0)
            self.touchGrid[self.convert(i, 3)] = (0, 255, 255)

    def draw_stacker(self):
        for i in range(self.stacker.length):
            self.touchGrid[self.convert(
                self.stacker.x_loc+i, self.stacker.y_loc)] = (255, 0, 0)

    lastColor = (0, 0, 0)

    def endGameEvent(self):
        global lastColor
        print(self.endStateGridLocation)
        if (self.endStateGridLocation == 6):
            tmpColor = self.blankColor
            self.blankColor = lastColor
            lastColor = tmpColor
        for i in range(self.endStateGridLocation, 12 - self.endStateGridLocation):
            for j in range(self.endStateGridLocation, 16 - self.endStateGridLocation):
                if ((i == (self.endStateGridLocation) or i == 11 - (self.endStateGridLocation)) or (j == (self.endStateGridLocation) or j == 15 - (self.endStateGridLocation))):
                    self.touchGrid[self.convert(i, j)] = lastColor
                else:
                    self.touchGrid[self.convert(i, j)] = self.blankColor
        if (self.endStateGridLocation == 6):
            self.endStateGridLocation = 0
        else:
            self.endStateGridLocation += 1

    def move(self, x=0, y=0):
        # Clear Stacker

        if (self.hasWon or self.hasLost):
            self.endGameEvent()
        else:
            for i in range(self.stacker.length):
                self.touchGrid[self.convert(
                    self.stacker.x_loc+i, self.stacker.y_loc)] = (0, 0, 0)

            # Determine direction and iterate x location
            at_left_edge = self.stacker.x_loc == 0
            at_right_edge = self.stacker.x_loc == self.stacker.x_max
            if (at_left_edge or at_right_edge):
                self.direction = -self.direction
            self.stacker.x_loc += self.direction

            self.draw_stacker()

    def checkGameState(self):
        global lastColor
        if (self.stacker.y_loc == 0):
            self.hasWon = True
            lastColor = (0, 255, 0)
        if (self.stacker.y_loc != 15):
            for i in range(self.stacker.length):
                if (self.touchGrid[self.convert(self.stacker.x_loc + i, self.stacker.y_loc + 1)] == (0, 0, 0)):
                    self.hasLost = True
                    lastColor = (255, 0, 0)
        if (self.hasWon or self.hasLost):
            self.blankColor = (0, 0, 0)

    def paint(self, x, y):
        if self.hasLost or self.hasWon:
            self.setup()
        else:
            self.checkGameState()
            self.stacker.y_loc = self.stacker.y_loc - 1
            self.SPEED = self.SPEED - .01
            if (self.stacker.y_loc == 8):
                self.stacker.length = 2
                self.stacker.x_max = 10
            if (self.stacker.y_loc == 3):
                self.stacker.length = 1
                self.stacker.x_max = 11

            # update slider location
            self.draw_stacker()
