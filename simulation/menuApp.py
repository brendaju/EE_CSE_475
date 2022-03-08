import asyncio
#from rpi_ws281x import Color


def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue


class menuApp:
    def __init__(self, deviceID):
        self.deviceID = deviceID
        self.nextApp = ''
        self.appArray = ['Painting', 'tictactoe', 'chess', 'animation',
                         'Brick Shooter', 'Tug of War', 'Simon Says', 'Pong', 'Image Show', 'Stacker']
        self.newAppSelected = 0
        self.touchGrid = [(0, 0, 0)] * 192
        self.IS_TIMER_BASED = False
        self.SPEED = 0

    def displayNumber(self, number, startx, starty):

        array = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1]
        if number == 1:
            array = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]

        if number == 2:
            array = [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1]

        if number == 3:
            array = [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]

        if number == 4:
            array = [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1]

        if number == 5:
            array = [1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1]

        if number == 6:
            array = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1]

        if number == 7:
            array = [1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]

        if number == 8:
            array = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]

        if number == 9:
            array = [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1]

        for i in range(0, 5):
            for j in range(0, 3):

                if (array[i * 3 + j] == 1):
                    self.touchGrid[self.convert(
                        startx + j, starty + i)] = (255, 255, 255)
                else:
                    self.touchGrid[self.convert(
                        startx + j, starty + i)] = (0, 0, 0)

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_menu(self):
        self.newAppSelected = 0
        self.selectedApp = ''
        self.displayNumber(int(self.deviceID / 10), 2, 2)
        self.displayNumber(int(self.deviceID % 10), 6, 2)

        self.touchGrid[self.convert(2, 10)] = (255, 0, 255)
        self.touchGrid[self.convert(3, 10)] = (255, 255, 255)
        self.touchGrid[self.convert(4, 10)] = (255, 255, 0)
        self.touchGrid[self.convert(5, 10)] = (0, 0, 255)
        self.touchGrid[self.convert(6, 10)] = (0, 255, 0)
        self.touchGrid[self.convert(7, 10)] = (0, 255, 255)
        self.touchGrid[self.convert(8, 10)] = (0, 255, 170)
        self.touchGrid[self.convert(9, 10)] = (255, 120, 0)
        self.touchGrid[self.convert(2, 11)] = (255, 0, 120)
        self.touchGrid[self.convert(3, 11)] = (120, 120, 255)

    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n):
        x = int(n / 16)
        y = int(n - x * 16)
        print(x, y)
        print(self.convert(x, y))

    def paint(self, x, y):
        print(x, y)
        if y == 10:
            if (x >= 2 and x <= 9):
                self.nextApp = self.appArray[x - 2]
                self.newAppSelected = 1
        if y == 11:
            if (x >= 2 and x <= 3):
                self.nextApp = self.appArray[x + 6]
                self.newAppSelected = 1
        print(self.nextApp)
