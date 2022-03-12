"""
Creates a basic demonstration of animation
"""
import asyncio

X_MAX = 16
Y_MAX = 12

def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class AnimationApp:
    """
    Creates a basic example of a slider moving for animation
    """
    def __init__(self):
        self.touch_grid = [(0, 0, 0)] * 192
        self.x_loc = 15
        self.y_loc = 10
        self.IS_TIMER_BASED = False
        self.SPEED = 0.1
        self.setup()

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
        '''
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup(self):
        """
        Sets up app's initial state
        """
        pass

    async def getGrid(self):
        """
        Returns the current state of the board to be displayed
        """
        return self.touchGrid

    def webPaint(self, n, web_color):
        """
        Performs paint function in website format to allow
        for website live updates
        """
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def paint(self, x=0, y=0):
        """
        Takes in an X and Y input from the touch sensors and updates app
        state based on the given input
        """
        self.touch_grid[self.convert(self.y_loc, self.x_loc)] = (0, 0, 0)
        self.x_loc -= 1
        if self.x_loc == X_MAX or self.y_loc == Y_MAX:
            self.x_loc = 0
        self.touch_grid[self.convert(self.y_loc, self.x_loc)] = (255, 255, 255)
