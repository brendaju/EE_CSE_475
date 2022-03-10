"""
Creates the classic "pong" game where two small sliding boards
shoots/bounces a ball around and whenever the ball hit the top
or bottom of the board. it counts as point. Players and ball
are then returned to the middle so game can start again.
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


def Color(red, green, blue):
    """
    Model color object for simulation
    """
    return (red << 16) | (green << 8) | blue


class slider:
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


class ball:
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


class pong_app:
    """
    Main app logic
    """
    def __init__(self):
        """
        Stores app's state
        """
        self.touchGrid = [(0, 0, 0)] * 192
        self.p1 = slider(15)
        self.p2 = slider(0)
        self.ball = ball()
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
        for i in range(self.ball.length):
            self.touchGrid[self.convert(
                self.ball.x_loc + i, self.ball.y_loc)] = (255, 255, 255)

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

    def draw_sliders(self):
        """
        Draws slider at updated location
        """
        for i in range(self.p1.length):
            self.touchGrid[self.convert(
                self.p1.x_loc + i, self.p1.y_loc)] = (255, 255, 255)
        for i in range(self.p2.length):
            self.touchGrid[self.convert(
                self.p2.x_loc + i, self.p2.y_loc)] = (255, 255, 255)

    def move(self, x=0, y=0):
        """
        Updates game state based on an asynchronous timer
        """
        # clear ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (0, 0, 0)

        # if we're at bottom or top of the screen set ball to middle
        if self.ball.y_loc == 15 or self.ball.y_loc == 0:
            self.ball.y_loc = 7
            self.ball.x_loc = 6
            self.ball.is_moving = False
            self.ball.x_velocity = 0
            self.ball.y_velocity = 0

        # if we're at either side of the screen rebound ball off
        if self.ball.x_loc == 0 or self.ball.x_loc == 11:
            self.ball.x_velocity *= -1

        # determine x and y velocity based off of where ball strickes paddle
        # for P1
        if self.ball.y_loc == self.p1.y_loc - 1 and self.ball.y_velocity == 1:
            if self.ball.x_loc == self.p1.x_loc + 1:
                self.ball.y_velocity = -1
                self.ball.x_velocity = 0
            elif self.ball.x_loc == self.p1.x_loc:
                self.ball.x_velocity = -1
                self.ball.y_velocity = -1
            elif self.ball.x_loc == self.p1.x_loc + 2:
                self.ball.x_velocity = 1
                self.ball.y_velocity = -1

        # determine x and y velocity based off of where ball strickes paddle
        # for P2
        if self.ball.y_loc == self.p2.y_loc + 1 and self.ball.y_velocity == -1:
            if self.ball.x_loc == self.p2.x_loc + 1:
                self.ball.y_velocity = 1
                self.ball.x_velocity = 0
            elif self.ball.x_loc == self.p2.x_loc:
                self.ball.x_velocity = -1
                self.ball.y_velocity = 1
            elif self.ball.x_loc == self.p2.x_loc + 2:
                self.ball.x_velocity = 1
                self.ball.y_velocity = 1

        if self.ball.is_moving:
            self.ball.y_loc += self.ball.y_velocity
            self.ball.x_loc += self.ball.x_velocity

        # display ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (255, 255, 255)

        score = 0
        #  gameover
        if score == 10:
            self.ball.y_loc = 7
            self.ball.x_loc = 6
            self.ball.is_moving = False
            self.ball.x_velocity = 0
            self.ball.y_velocity = 0
            self.setup()

    def paint(self, x, y):
        """
        Takes in an X and Y input from the touch sensors and updates app
        state based on the given input
        """
        # clear p1
        for i in range(self.p1.length):
            self.touchGrid[self.convert(
                self.p1.x_loc + i, self.p1.y_loc)] = (0, 0, 0)

        # clear p2
        for i in range(self.p2.length):
            self.touchGrid[self.convert(
                self.p2.x_loc + i, self.p2.y_loc)] = (0, 0, 0)

        # clear ball
        for i in range(self.ball.length):
            self.touchGrid[self.convert(
                self.ball.x_loc + i, self.ball.y_loc)] = (0, 0, 0)

        # define slider movement for p1
        slider_center_p1 = self.p1.x_loc + 1
        move_left_p1 = (y == self.p1.y_loc) and (x < slider_center_p1)
        move_right_p1 = (y == self.p1.y_loc) and (x > slider_center_p1)
        at_left_edge_p1 = self.p1.x_loc == 0
        at_right_edge_p1 = self.p1.x_loc == self.p1.x_max
        shoot_ball_p1 = (x == slider_center_p1) and (y == self.p1.y_loc)

        # calculate p1 location
        if move_left_p1:
            if at_left_edge_p1:
                self.p1.x_loc = self.p1.x_max
            else:
                self.p1.x_loc -= 1
        elif move_right_p1:
            if at_right_edge_p1:
                self.p1.x_loc = 0
            else:
                self.p1.x_loc += 1

        # define slider movement for p2
        slider_center_p2 = self.p2.x_loc + 1
        move_left_p2 = (y == self.p2.y_loc) and (x < slider_center_p2)
        move_right_p2 = (y == self.p2.y_loc) and (x > slider_center_p2)
        at_left_edge_p2 = self.p2.x_loc == 0
        at_right_edge_p2 = self.p2.x_loc == self.p2.x_max

        # calculate p1 location
        if move_left_p2:
            if at_left_edge_p2:
                self.p2.x_loc = self.p2.x_max
            else:
                self.p2.x_loc -= 1
        elif move_right_p2:
            if at_right_edge_p2:
                self.p2.x_loc = 0
            else:
                self.p2.x_loc += 1

        # check if ball should move
        if shoot_ball_p1 and not self.ball.is_moving:
            self.ball.y_velocity = 1
            self.ball.is_moving = True

        # update p1 and p2 sliders location
        self.draw_sliders()

        # display ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (255, 255, 255)
