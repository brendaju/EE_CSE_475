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


class tictactoeApp:
    def __init__(self):
        self.currentPlayer = 'X'
        self.touchGrid = [(0, 0, 0)]*192
        self.gameGrid = ['-']*10
        self.gameOver = 0
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.setup_tictactoe()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def gameConvert(self, x, y):
        if (y >= 3 and y <= 5):
            gameIndex = 0
            gameY = 0
        elif (y >= 7 and y <= 9):
            gameIndex = 3
            gameY = 1
        elif (y >= 11 and y <= 13):
            gameIndex = 6
            gameY = 2
        else:
            return -1, -1, -1

        if (x >= 1 and x <= 3):
            gameIndex = gameIndex
            gameX = 0
        elif (x >= 5 and x <= 7):
            gameIndex = gameIndex + 1
            gameX = 1
        elif (x >= 9 and x <= 11):
            gameIndex = gameIndex + 2
            gameX = 2
        else:
            return -1, -1, -1

        return gameIndex, gameX, gameY

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex

    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_tictactoe(self):
        for i in range(1, 12):
            self.touchGrid[self.convert(i, 6)] = (200, 200, 200)
            self.touchGrid[self.convert(i, 10)] = (200, 200, 200)

        for i in range(3, 14):
            self.touchGrid[self.convert(4, i)] = (200, 200, 200)
            self.touchGrid[self.convert(8, i)] = (200, 200, 200)

    async def getGrid(self):
        return self.touchGrid

    def boardCheck(self):
        if (self.gameGrid[0] == self.gameGrid[1] == self.gameGrid[2] and self.gameGrid[0] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(i+1, 4)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[3] == self.gameGrid[4] == self.gameGrid[5] and self.gameGrid[3] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(i+1, 8)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[6] == self.gameGrid[7] == self.gameGrid[8] and self.gameGrid[6] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(i+1, 12)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[0] == self.gameGrid[3] == self.gameGrid[6] and self.gameGrid[0] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(2, 3+i)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[1] == self.gameGrid[4] == self.gameGrid[7] and self.gameGrid[1] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(6, 3+i)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[2] == self.gameGrid[5] == self.gameGrid[8] and self.gameGrid[2] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(10, 3+i)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[0] == self.gameGrid[4] == self.gameGrid[8] and self.gameGrid[0] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(i+1, i+4)] = (255, 0, 0)
            return 1
        elif (self.gameGrid[2] == self.gameGrid[4] == self.gameGrid[6] and self.gameGrid[2] != '-'):
            for i in range(11):
                self.touchGrid[self.convert(i+1, 13-i)] = (255, 0, 0)
            return 1
        else:
            return 0

    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        self.paint(x, y)

    def paint(self, x, y):
        gameIndex, gameX, gameY = self.gameConvert(x, y)
        if (gameIndex == -1 or self.gameGrid[gameIndex] != '-' or self.gameOver == 1):
            return

        self.gameGrid[gameIndex] = self.currentPlayer

        if (self.currentPlayer == 'X'):
            self.touchGrid[self.convert(
                (gameX*4+1), (gameY*4+3))] = (255, 0, 255)
            self.touchGrid[self.convert(
                (gameX*4+3), (gameY*4+3))] = (255, 0, 255)
            self.touchGrid[self.convert(
                (gameX*4+2), (gameY*4+4))] = (255, 0, 255)
            self.touchGrid[self.convert(
                (gameX*4+1), (gameY*4+5))] = (255, 0, 255)
            self.touchGrid[self.convert(
                (gameX*4+3), (gameY*4+5))] = (255, 0, 255)
        else:
            self.touchGrid[self.convert(
                (gameX*4+2), (gameY*4+3))] = (0, 255, 255)
            self.touchGrid[self.convert(
                (gameX*4+1), (gameY*4+4))] = (0, 255, 255)
            self.touchGrid[self.convert(
                (gameX*4+3), (gameY*4+4))] = (0, 255, 255)
            self.touchGrid[self.convert(
                (gameX*4+2), (gameY*4+5))] = (0, 255, 255)

        self.gameOver = self.boardCheck()

        if (self.currentPlayer == 'X'):
            self.currentPlayer = 'O'
        else:
            self.currentPlayer = 'X'
