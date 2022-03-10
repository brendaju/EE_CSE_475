"""
Creates the classic "brick shooter" game where a small sliding board
shoots/bounces a ball to break various bricks in the playing field.
Once all of the bricks are broken, the game resets with the player/ball
returned to the start position and all of the bricks refilled.
"""
import asyncio

set_colors = [
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
    def __init__(self):
        self.x_loc = 5
        self.y_loc = 15
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
        self.y_loc = 14
        self.length = 1
        self.height = 1
        self.x_max = 12 - self.length
        self.y_max = 14 - self.height
        self.is_moving = False
        self.x_velocity = 0
        self.y_velocity = 0


class target:
    """
    Two by two pixel size target
    """
    def __init__(self, x_loc=0, y_loc=0):
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.length = 2
        self.height = 2


class brick_shooter_app:
    """
    Main app logic
    """
    def __init__(self):
        """
        Stores app's state
        """
        self.touchGrid = [(0, 0, 0)] * 192
        self.slider = slider()
        self.ball = ball()
        self.targets = []
        self.target_locations = set()
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
        # create targets
        self.targets.append(target(2, 1))
        self.targets.append(target(8, 3))
        self.targets.append(target(1, 9))
        self.targets.append(target(6, 7))

        # draw slider
        self.draw_slider()

        # draw ball
        for i in range(self.ball.length):
            self.touchGrid[self.convert(
                self.ball.x_loc + i, self.ball.y_loc)] = (255, 255, 255)

        # draw targets (uses slightly different form but does same as below)
        for t in self.targets:
            for x in range(t.x_loc, t.x_loc + t.length):
                for y in range(t.y_loc, t.y_loc + t.height):
                    self.target_locations.add((x, y))
                    self.touchGrid[self.convert(x, y)] = (0, 0, 255)

    async def get_grid(self):
        """
        Returns the current state of the board to be displayed
        """
        return self.touchGrid

    def web_paint(self, n, webColor):
        """
        Performs paint function in website format to allow
        for website live updates
        """
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def draw_slider(self):
        """
        Draws slider at updated location
        """
        for i in range(self.slider.length):
            # paint the middle dot red and other dots white
            if (i == 1):
                self.touchGrid[self.convert(
                    self.slider.x_loc + i, self.slider.y_loc)] = (255, 0, 0)
            else:
                self.touchGrid[self.convert(
                    self.slider.x_loc + i, self.slider.y_loc)] = (255, 255, 255)

    def move(self, x=0, y=0):
        """
        Updates game state based on an asynchronous timer
        """
        # clear ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (0, 0, 0)

        # check if ball should move
        location = (self.ball.x_loc, self.ball.y_loc)

        # if we're at bottom of the screen reset ball to paddle
        if self.ball.y_loc == 15:
            self.ball.y_loc = 14
            self.ball.x_loc = self.slider.x_loc + 1
            self.ball.is_moving = False
            self.ball.x_velocity = 0
            self.ball.y_velocity = 0
            self.target_locations.discard(location)

        # if we're at top of the screen rebound ball off
        if self.ball.y_loc == 0:
            self.ball.y_velocity *= -1

        # if we're at either side of the screen rebound ball off
        if self.ball.x_loc == 0 or self.ball.x_loc == 11:
            self.ball.x_velocity *= -1

        # if we hit a brick - bounce off in opposite directions
        if location in self.target_locations:
            self.ball.y_velocity *= -1
            self.ball.x_velocity *= -1
            self.target_locations.discard(location)

        # determine x and y velocity based off of where ball strickes paddle
        if self.ball.y_loc == self.slider.y_loc - 1 and self.ball.y_velocity == 1:
            if self.ball.x_loc == self.slider.x_loc + 1:
                self.ball.y_velocity = -1
                self.ball.x_velocity = 0
            elif self.ball.x_loc == self.slider.x_loc:
                self.ball.x_velocity = -1
                self.ball.y_velocity = -1
            elif self.ball.x_loc == self.slider.x_loc + 2:
                self.ball.x_velocity = 1
                self.ball.y_velocity = -1

        # update ball location based on velocity
        if self.ball.is_moving:
            self.ball.y_loc += self.ball.y_velocity
            self.ball.x_loc += self.ball.x_velocity

        # display ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (255, 255, 255)

        # gameover
        if len(self.target_locations) == 0:
            self.ball.y_loc = 14
            self.ball.x_loc = self.slider.x_loc + 1
            self.ball.is_moving = False
            self.ball.x_velocity = 0
            self.ball.y_velocity = 0
            self.setup()

    def paint(self, x, y):
        """
        Takes in an X and Y input from the touch sensors and updates app
        state based on the given input
        """
        slider_center = self.slider.x_loc + 1

        # clear slider
        for i in range(self.slider.length):
            self.touchGrid[self.convert(
                self.slider.x_loc + i, self.slider.y_loc)] = (0, 0, 0)

        # clear ball
        for i in range(self.ball.length):
            self.touchGrid[self.convert(
                self.ball.x_loc + i, self.ball.y_loc)] = (0, 0, 0)

        # define slider movement
        move_left = (y == self.slider.y_loc) and (x < slider_center)
        move_right = (y == self.slider.y_loc) and (x > slider_center)
        at_left_edge = self.slider.x_loc == 0
        at_right_edge = self.slider.x_loc == self.slider.x_max
        shoot_ball = slider_center == x

        # check if ball should move
        if shoot_ball and not self.ball.is_moving:
            self.ball.y_velocity = -1
            self.ball.is_moving = True

        # calculate slider location
        if move_left:
            if at_left_edge:
                self.slider.x_loc = self.slider.x_max
                if not self.ball.is_moving:
                    self.ball.x_loc = 10
            else:
                self.slider.x_loc -= 1
                if not self.ball.is_moving:
                    self.ball.x_loc -= 1
        elif move_right:
            if at_right_edge:
                self.slider.x_loc = 0
                if not self.ball.is_moving:
                    self.ball.x_loc = 1
            else:
                self.slider.x_loc += 1
                if not self.ball.is_moving:
                    self.ball.x_loc += 1

        # update slider location
        self.draw_slider()

        # display ball location
        self.touchGrid[self.convert(
            self.ball.x_loc, self.ball.y_loc)] = (255, 255, 255)
