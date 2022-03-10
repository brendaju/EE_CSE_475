import asyncio
import random

def color(red, green, blue):
    '''
    Takes in the red, green, and blue values and converts them to the
    proper format for the LED strip. From the LED strip library
    '''
    return (red << 16) | (green << 8) | blue

class SimonSaysApp:
    def __init__(self):
        '''
        Initiates the simon says app as a timer based app
        with a pattern of integers, a current level, and a
        current count
        '''
        self.display_pattern = 1
        self.display_square = 1
        self.curr_count = 0
        self.level = 0
        self.incorrect_touch = (0, 0)
        self.touch_grid = [(0, 0, 0)] * 192
        self.pattern = []
        self.blink = 0
        self.correct_touch = 0
        self.IS_TIMER_BASED = True
        self.SPEED = 1

    def convert(self, x, y):
        """ 
        if in an odd column, reverse the order
        """
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def rgb_to_hex(self, r, g, b):
        '''
        Converts an give r g b value to the equivalent Hex form with
        the format #FFFFFF
        Based on: https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
        '''
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    async def get_grid(self):
        '''
        Gets the current grid with all pixel colors from the app
        '''
        return self.touch_grid

    def web_paint(self, n, webColor):
        '''
        Determines the x and y value of the grid based on the
        input from the remote website. Then sets that index in the
        to be equal to the color sent from the website
        '''
        x = int(n / 16)
        y = int(n - x * 16)
        print(x, y)
        print(self.convert(x, y))
        self.touch_grid[self.convert(x, y)] = webColor

    def wipe_screen(self):
        """ 
        clear all pixels
        """
        for x_wipe in range(12):
            for y_wipe in range(16):
                self.touch_grid[self.convert(x_wipe, y_wipe)] = (0, 0, 0)

    def move(self, x=0, y=0):
        """ 
        defines behavior of the board at each time iteration, either idling 
        while waiting for the user or progressing through the pattern one integer at a time
        """
        if (self.level == 0):
            # initialize game
            self.wipe_screen()
            self.pattern = []
            self.correct_touch = 0
            self.display_pattern = 1
            self.curr_count = 0
            self.pattern.append(
                (random.randrange(0, 11, 1), random.randrange(0, 15, 1)))
            self.level += 1
            self.blink_square = 1

        elif (self.display_pattern):
            # blinks the square in the pattern white
            if (self.blink_square):
                self.touch_grid[self.convert(
                    self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (255, 255, 255)
                self.blink_square = 0
            # turns the previous square in the pattern back to black
            else:
                self.touch_grid[self.convert(
                    self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (0, 0, 0)
                self.curr_count += 1
                self.blink_square = 1
                if (self.curr_count >= self.level):
                    self.display_pattern = 0
                    self.curr_count = 0

        else:
            # waits for input from the user and updates the game based on user's touch
            if (self.correct_touch >= self.level):
                self.curr_count += 1
                if (self.curr_count >= self.level):
                    self.display_pattern = 1
                    self.curr_count = 0
                    self.wipe_screen()
                    self.pattern.append(
                        (random.randrange(0, 11, 1), random.randrange(0, 15, 1)))
                    self.level += 1
                    self.correct_touch = 0
            else:
                self.wipe_screen()

    def paint(self, x, y):
        """ 
        takes user input x, y, and determines behavior for when the touch is
        correct or incorrect
        """
        if (x == self.pattern[self.curr_count][0]
                and y == self.pattern[self.curr_count][1]):
            # correct touch
            self.touch_grid[self.convert(
                self.pattern[self.curr_count][0], self.pattern[self.curr_count][1])] = (0, 255, 0)
            self.correct_touch += 1
            self.curr_count += 1
        else:
            # incorrect touch
            self.touch_grid[self.convert(x, y)] = (255, 0, 0)
            self.incorrect_touch = (x, y)
            self.level = 0