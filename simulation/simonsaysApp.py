import asyncio
import random
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


class simonsaysApp:
    def __init__(self):
        self.display_pattern = 1
        self.display_square = 1
        self.curr_count = 0
        self.level = 0
        self.incorrect_touch = (0, 0)
        self.touchGrid = [(0, 0, 0)] * 192
        self.pattern = []
        self.blink = 0
        self.correct_touch = 0
        self.IS_TIMER_BASED = True
        self.SPEED = 1

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n, webColor):
        x = int(n / 16)
        y = int(n - x * 16)
        print(x, y)
        print(self.convert(x, y))
        self.touchGrid[self.convert(x, y)] = webColor

    def checkTouch(self, x, y):
        self.touch_x = x
        self.touch_y = y

    def wipescreen(self):
        for x_wipe in range(12):
            for y_wipe in range(16):
                self.touchGrid[self.convert(x_wipe, y_wipe)] = (0, 0, 0)

    def move(self, x=0, y=0):
        print(self.pattern)

        # if at game start, select random square to add to pattern
        if (self.level == 0):
            self.wipescreen()
            self.touchGrid[self.convert(
                self.incorrect_touch[0], self.incorrect_touch[1])] = (0, 0, 0)
            self.pattern = []
            self.correct_touch = 0
            self.display_pattern = 1
            self.curr_count = 0
            self.pattern.append(
                (random.randrange(0, 11, 1), random.randrange(0, 15, 1)))
            self.level += 1
            self.blink_square = 1

        # during display pattern, the user watches the pattern and tries to
        # memorize it. user inputs are not accepted
        elif (self.display_pattern):
            # blinks the square in the pattern white
            if (self.blink_square):
                self.touchGrid[self.convert(
                    self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (255, 255, 255)
                self.blink_square = 0
            # turns the previous square in the pattern back to black
            else:
                self.touchGrid[self.convert(
                    self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (0, 0, 0)
                self.curr_count += 1
                self.blink_square = 1
                # next two lines need to be moved to when the user gets to the next level
                #self.pattern.append((random.randrange(0, 11, 1), random.randrange(0, 15, 1)))
                #self.level += 1
                # checks if the pattern is done. if it is, turn control over to
                # the user and reset the current index of the pattern array
                if (self.curr_count >= self.level):
                    self.display_pattern = 0
                    self.curr_count = 0

        # now the user tries to input the pattern and is either right (new
        # square gets added to the pattern) or wrong (gameover)
        else:
            print(self.correct_touch)
            print(self.level)
            if (self.correct_touch >= self.level):
                self.curr_count += 1
                if (self.curr_count >= self.level):
                    self.display_pattern = 1
                    self.curr_count = 0
                    self.wipescreen()
                    self.pattern.append(
                        (random.randrange(0, 11, 1), random.randrange(0, 15, 1)))
                    self.level += 1
                    self.correct_touch = 0
            else:
                self.wipescreen()

    def paint(self, x, y):
        if (x == self.pattern[self.curr_count][0]
                and y == self.pattern[self.curr_count][1]):
            # blink correct touch green and move forward in pattern array
            self.touchGrid[self.convert(
                self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (0, 255, 0)
            self.correct_touch += 1
            self.curr_count += 1
        else:
            # incorrect touch: turn touched square red and restart game
            self.touchGrid[self.convert(x, y)] = (255, 0, 0)
            self.incorrect_touch = (x, y)
            self.level = 0
