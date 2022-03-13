"""
Creates a tug of war game where two players compete
on opposite sides of the board to 'pull' a rope to 
their side. The color of the winning side is displayed
at the end of each game.
"""

import asyncio

def color(red, green, blue):
    """
    Takes in the red, green, and blue values and converts them to the
    proper format for the LED strip. From the LED strip library
    """
    return (red << 16) | (green << 8) | blue

class Rope:
    """
    Eight pixel wide rope
    """
    def __init__(self):
        self.start = 4
        self.end = 12

class TugOfWarApp:
    """
    Main app logic
    """
    def __init__(self):
        """
        Stores app's state
        """
        self.touch_grid = [(0, 0, 0)] * 192
        self.game_grid = ['-'] * 10
        self.game_over = 0
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.Rope = Rope()
        self.setup_tug()

    def convert(self, x, y):
        """
        Converts x and y values into index for LED strip
        """
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def rgb_to_hex(self, r, g, b):
        """
        Converts RGB form to HEX
        """
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_tug(self):
        """
        Creates app's initial state
        """
        # Draws color of each side
        for i in range(0, 12):
            self.touch_grid[self.convert(i, 0)] = (0, 0, 255)
            self.touch_grid[self.convert(i, 15)] = (0, 255, 0)

        # Draws centerline
        self.touch_grid[self.convert(0, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(1, 8)] = (255, 255, 255)
        self.touch_grid[self.convert(2, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(3, 8)] = (255, 255, 255)
        self.touch_grid[self.convert(4, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(5, 8)] = (255, 255, 255)
        self.touch_grid[self.convert(6, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(7, 8)] = (255, 255, 255)
        self.touch_grid[self.convert(8, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(9, 8)] = (255, 255, 255)
        self.touch_grid[self.convert(10, 7)] = (255, 255, 255)
        self.touch_grid[self.convert(11, 8)] = (255, 255, 255)

        # Draws the rope
        self.draw_rope()

    def draw_rope(self):
        """
        Draws the rope by coloring pixels between rope's start
        and end. 
        """
        for i in range(self.Rope.start, 8):
            self.touch_grid[self.convert(5, i)] = (0, 0, 255)
            self.touch_grid[self.convert(6, i)] = (0, 0, 255)
        for i in range(8, self.Rope.end):
            self.touch_grid[self.convert(5, i)] = (0, 255, 0)
            self.touch_grid[self.convert(6, i)] = (0, 255, 0)

    async def get_grid(self):
        """
        Returns the current state of the board to be displayed
        """
        return self.touch_grid

    def web_paint(self, n, web_color):
        """
        Performs paint function in website format to allow
        for website live updates
        """
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def paint(self, x, y):
        """
        Takes in an X and Y input from the touch sensors and updates app
        state based on the given input
        """
        # Define how a winner is defined
        win_left = (self.Rope.start == 0)
        win_right = (self.Rope.end == 15)
        move_left = (y < 7)
        move_right = (y > 8)
        game_over = win_left or win_right

        # Define app state at the end of a game
        if game_over:

            if win_left:
                self.touch_grid = [(0, 0, 255)] * 192

            else:
                self.touch_grid = [(0, 255, 0)] * 192

            for i in range(4, 12):
                self.touch_grid[self.convert(2, i)] = (255, 255, 255)
                self.touch_grid[self.convert(9, i)] = (255, 255, 255)

            for i in range(2, 9):
                self.touch_grid[self.convert(i, 11)] = (255, 255, 255)

            for i in range(5, 9):
                self.touch_grid[self.convert(i, 4)] = (255, 255, 255)

            self.touch_grid[self.convert(5, 3)] = (255, 255, 255)
            self.touch_grid[self.convert(6, 2)] = (255, 255, 255)
            self.touch_grid[self.convert(7, 1)] = (255, 255, 255)

            self.touch_grid[self.convert(5, 5)] = (255, 255, 255)
            self.touch_grid[self.convert(6, 6)] = (255, 255, 255)
            self.touch_grid[self.convert(7, 7)] = (255, 255, 255)

            if (x < 10) and (x > 1) and (y < 12) and (y > 3):
                game_over = False
                self.touch_grid = [(0, 0, 0)] * 192
                self.Rope.start = 4
                self.Rope.end = 12
                self.draw_rope()
                self.setup_tug()

        # Define app state during gameplay
        else:
            for i in range(self.Rope.start, self.Rope.end):
                self.touch_grid[self.convert(5, i)] = (0, 0, 0)
                self.touch_grid[self.convert(6, i)] = (0, 0, 0)

            if move_left:
                self.Rope.start = self.Rope.start - 1
                self.Rope.end = self.Rope.end - 1

            if move_right:
                self.Rope.start = self.Rope.start + 1
                self.Rope.end = self.Rope.end + 1

            if win_left:
                self.touch_grid = [(0, 0, 255)] * 192

            elif win_right:
                self.touch_grid = [(0, 255, 0)] * 192

            else:
                self.draw_rope()
