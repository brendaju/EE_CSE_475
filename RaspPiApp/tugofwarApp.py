import asyncio
#from rpi_ws281x import Color


def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue


class rope:
    def __init__(self):
        self.start = 4
        self.end = 12


class tugofwarApp:
    def __init__(self):
        self.touchGrid = [(0, 0, 0)]*192
        self.gameGrid = ['-']*10
        self.gameOver = 0
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.rope = rope()
        self.setup_tug()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_tug(self):

        for i in range(0, 12):
            self.touchGrid[self.convert(i, 0)] = (0, 0, 255)
            self.touchGrid[self.convert(i, 15)] = (0, 255, 0)

        self.touchGrid[self.convert(0, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(1, 8)] = (255, 255, 255)
        self.touchGrid[self.convert(2, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(3, 8)] = (255, 255, 255)
        self.touchGrid[self.convert(4, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(5, 8)] = (255, 255, 255)
        self.touchGrid[self.convert(6, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(7, 8)] = (255, 255, 255)
        self.touchGrid[self.convert(8, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(9, 8)] = (255, 255, 255)
        self.touchGrid[self.convert(10, 7)] = (255, 255, 255)
        self.touchGrid[self.convert(11, 8)] = (255, 255, 255)
        self.draw_rope()

    def draw_rope(self):
        for i in range(self.rope.start, 8):
            self.touchGrid[self.convert(5, i)] = (0, 0, 255)
            self.touchGrid[self.convert(6, i)] = (0, 0, 255)
        for i in range(8, self.rope.end):
            self.touchGrid[self.convert(5, i)] = (0, 255, 0)
            self.touchGrid[self.convert(6, i)] = (0, 255, 0)

    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        self.paint(x, y)

    def paint(self, x, y):
        win_left = (self.rope.start == 0)
        win_right = (self.rope.end == 15)
        move_left = (y < 7)
        move_right = (y > 8)
        game_over = win_left or win_right

        if game_over:

            if win_left:
                self.touchGrid = [(0, 0, 255)]*192

            else:
                self.touchGrid = [(0, 255, 0)]*192

            for i in range(4, 12):
                self.touchGrid[self.convert(2, i)] = (255, 255, 255)
                self.touchGrid[self.convert(9, i)] = (255, 255, 255)

            for i in range(2, 9):
                self.touchGrid[self.convert(i, 11)] = (255, 255, 255)

            for i in range(5, 9):
                self.touchGrid[self.convert(i, 4)] = (255, 255, 255)

            self.touchGrid[self.convert(5, 3)] = (255, 255, 255)
            self.touchGrid[self.convert(6, 2)] = (255, 255, 255)
            self.touchGrid[self.convert(7, 1)] = (255, 255, 255)

            self.touchGrid[self.convert(5, 5)] = (255, 255, 255)
            self.touchGrid[self.convert(6, 6)] = (255, 255, 255)
            self.touchGrid[self.convert(7, 7)] = (255, 255, 255)

            if (x < 10) and (x > 1) and (y < 12) and (y > 3):
                game_over = False
                self.touchGrid = [(0, 0, 0)]*192
                self.rope.start = 4
                self.rope.end = 12
                self.draw_rope()
                self.setup_tug()

        else:
            for i in range(self.rope.start, self.rope.end):
                self.touchGrid[self.convert(5, i)] = (0, 0, 0)
                self.touchGrid[self.convert(6, i)] = (0, 0, 0)

            if move_left:
                self.rope.start = self.rope.start - 1
                self.rope.end = self.rope.end - 1

            if move_right:
                self.rope.start = self.rope.start + 1
                self.rope.end = self.rope.end + 1

            if win_left:
                self.touchGrid = [(0, 0, 255)]*192

            elif win_right:
                self.touchGrid = [(0, 255, 0)]*192

            else:
                self.draw_rope()
