"""
Creates the classic "pong" game where two small sliding boards
shoots/bounces a ball around and whenever the ball hit the top
or bottom of the board. it counts as point. Players and ball
are then returned to the middle so game can start again.
"""
from ast import Not
import asyncio
from shutil import move

def color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class Slider:
    """
    Three pixel wide slider
    """
    def __init__(self, y_loc):
        self.x_loc = 5
        self.y_loc = y_loc
        self.length = 3
        self.height = 1
        self.x_max = 12 - self.length
        self.y_max = 15 - self.height


class Ball:
    """
    One pixel wide ball
    """
    def __init__(self):
        self.x_loc = 6
        self.y_loc = 7
        self.length = 1
        self.height = 1
        self.x_max = 12 - self.length
        self.y_max = 14 - self.height
        self.is_moving = False
        self.x_velocity = 0
        self.y_velocity = 0


class PongApp:
    """
    Main app logic
    """
    def __init__(self):
        """
        Stores app's state
        """
        self.touch_grid = [(0, 0, 0)] * 192
        self.P1 = Slider(15)
        self.P2 = Slider(0)
        self.Ball = Ball()
        self.IS_TIMER_BASED = True
        self.SPEED = 0.08
        self.setup()

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

    def setup(self):
        """
        Creates app's initial state
        """
        # draw slider
        self.draw_sliders()

        # draw ball
        for i in range(self.Ball.length):
            self.touch_grid[self.convert(
                self.Ball.x_loc + i, self.Ball.y_loc)] = (255, 255, 255)

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

    def draw_sliders(self):
        """
        Draws slider at updated location
        """
        for i in range(self.P1.length):
            self.touch_grid[self.convert(
                self.P1.x_loc + i, self.P1.y_loc)] = (255, 255, 255)
        for i in range(self.P2.length):
            self.touch_grid[self.convert(
                self.P2.x_loc + i, self.P2.y_loc)] = (255, 255, 255)

    def move(self, x=0, y=0):
        """
        Updates game state based on an asynchronous timer
        """
        # clear ball location
        self.touch_grid[self.convert(
            self.Ball.x_loc, self.Ball.y_loc)] = (0, 0, 0)

        # if we're at bottom or top of the screen set ball to middle
        if self.Ball.y_loc == 15 or self.Ball.y_loc == 0:
            self.Ball.y_loc = 7
            self.Ball.x_loc = 6
            self.Ball.is_moving = False
            self.Ball.x_velocity = 0
            self.Ball.y_velocity = 0

        # if we're at either side of the screen rebound ball off
        if self.Ball.x_loc == 0 or self.Ball.x_loc == 11:
            self.Ball.x_velocity *= -1

        # determine x and y velocity based off of where ball strickes paddle
        # for P1
        if self.Ball.y_loc == self.P1.y_loc - 1 and self.Ball.y_velocity == 1:
            if self.Ball.x_loc == self.P1.x_loc + 1:
                self.Ball.y_velocity = -1
                self.Ball.x_velocity = 0
            elif self.Ball.x_loc == self.P1.x_loc:
                self.Ball.x_velocity = -1
                self.Ball.y_velocity = -1
            elif self.Ball.x_loc == self.P1.x_loc + 2:
                self.Ball.x_velocity = 1
                self.Ball.y_velocity = -1

        # determine x and y velocity based off of where ball strickes paddle
        # for P2
        if self.Ball.y_loc == self.P2.y_loc + 1 and self.Ball.y_velocity == -1:
            if self.Ball.x_loc == self.P2.x_loc + 1:
                self.Ball.y_velocity = 1
                self.Ball.x_velocity = 0
            elif self.Ball.x_loc == self.P2.x_loc:
                self.Ball.x_velocity = -1
                self.Ball.y_velocity = 1
            elif self.Ball.x_loc == self.P2.x_loc + 2:
                self.Ball.x_velocity = 1
                self.Ball.y_velocity = 1

        if self.Ball.is_moving:
            self.Ball.y_loc += self.Ball.y_velocity
            self.Ball.x_loc += self.Ball.x_velocity

        # display ball location
        self.touch_grid[self.convert(
            self.Ball.x_loc, self.Ball.y_loc)] = (255, 255, 255)

        score = 0
        #  gameover
        if score == 10:
            self.Ball.y_loc = 7
            self.Ball.x_loc = 6
            self.Ball.is_moving = False
            self.Ball.x_velocity = 0
            self.Ball.y_velocity = 0
            self.setup()

    def paint(self, x, y):
        """
        Takes in an X and Y input from the touch sensors and updates app
        state based on the given input
        """
        # clear P1
        for i in range(self.P1.length):
            self.touch_grid[self.convert(
                self.P1.x_loc + i, self.P1.y_loc)] = (0, 0, 0)

        # clear P2
        for i in range(self.P2.length):
            self.touch_grid[self.convert(
                self.P2.x_loc + i, self.P2.y_loc)] = (0, 0, 0)

        # clear ball
        for i in range(self.Ball.length):
            self.touch_grid[self.convert(
                self.Ball.x_loc + i, self.Ball.y_loc)] = (0, 0, 0)

        # define slider movement for P1
        slider_center_P1 = self.P1.x_loc + 1
        move_left_P1 = (y == self.P1.y_loc) and (x < slider_center_P1)
        move_right_P1 = (y == self.P1.y_loc) and (x > slider_center_P1)
        at_left_edge_P1 = self.P1.x_loc == 0
        at_right_edge_P1 = self.P1.x_loc == self.P1.x_max
        shoot_ball_P1 = (x == slider_center_P1) and (y == self.P1.y_loc)

        # calculate P1 location
        if move_left_P1:
            if at_left_edge_P1:
                self.P1.x_loc = self.P1.x_max
            else:
                self.P1.x_loc -= 1
        elif move_right_P1:
            if at_right_edge_P1:
                self.P1.x_loc = 0
            else:
                self.P1.x_loc += 1

        # define slider movement for P2
        slider_center_P2 = self.P2.x_loc + 1
        move_left_P2 = (y == self.P2.y_loc) and (x < slider_center_P2)
        move_right_P2 = (y == self.P2.y_loc) and (x > slider_center_P2)
        at_left_edge_P2 = self.P2.x_loc == 0
        at_right_edge_P2 = self.P2.x_loc == self.P2.x_max

        # calculate P1 location
        if move_left_P2:
            if at_left_edge_P2:
                self.P2.x_loc = self.P2.x_max
            else:
                self.P2.x_loc -= 1
        elif move_right_P2:
            if at_right_edge_P2:
                self.P2.x_loc = 0
            else:
                self.P2.x_loc += 1

        # check if ball should move
        if shoot_ball_P1 and self.Ball.is_moving == False:
            self.Ball.y_velocity = 1
            self.Ball.is_moving = True

        print("P2 loc", self.P2.x_loc, self.P2.y_loc)
        print("x and y", x, y)
        # update P1 and P2 sliders location
        self.draw_sliders()

        # display ball location
        self.touch_grid[self.convert(
            self.Ball.x_loc, self.Ball.y_loc)] = (255, 255, 255)
