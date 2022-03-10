"""
Creates a basic demonstration of animation
"""
import asyncio

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
    """
    Model color object for simulation
    """
    return (red << 16) | (green << 8) | blue


class animation_app:
    """
    Main app logic
    """
    def __init__(self):
        """
        Stores app's state
        """
        self.touchGrid = [(0, 0, 0)] * 192
        self.x_loc = 15
        self.y_loc = 10
        self.IS_TIMER_BASED = True
        self.SPEED = 0.1
        self.setup()

    def convert(self, x, y):
        """
        Converts x and y values into index for LED strip
        """
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def rgbToHex(self, r, g, b):
        """
        Converts RGB form to HEX
        """
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup(self):
        """
        Creates app's initial state
        """
        pass

    async def getGrid(self):
        """
        Returns the current state of the board to be displayed
        """
        return self.touchGrid

    def webPaint(self, n, webColor):
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
        self.touchGrid[self.convert(self.y_loc, self.x_loc)] = (0, 0, 0)
        self.x_loc -= 1
        if self.x_loc == X_MAX or self.y_loc == Y_MAX:
            self.x_loc = 0
        self.touchGrid[self.convert(self.y_loc, self.x_loc)] = (255, 255, 255)
