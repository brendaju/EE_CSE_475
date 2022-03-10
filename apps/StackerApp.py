from ast import Not
import asyncio
from shutil import move

def color(red, green, blue):
    return (red << 16) | (green << 8) | blue


class Stacker:
    def __init__(self):
        self.x_loc = 5
        self.y_loc = 15
        self.length = 3
        self.height = 1
        self.x_max = 12 - self.length
        self.y_max = 15 - self.height


class StackerApp:
    def __init__(self):
        self.touch_grid = [(0, 0, 0)] * 192
        self.Stacker = Stacker()
        self.direction = 1  # 1 - right -1 - left
        self.has_lost = False
        self.has_won = False
        self.IS_TIMER_BASED = True
        self.SPEED = 1
        self.blank_color = (0, 0, 0)
        self.setup()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgb_to_hex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup(self):
        # create target
        # draw slider
        self.Stacker = Stacker()
        self.SPEED = 1
        self.direction = 1
        self.touch_grid = [(0, 0, 0)] * 192
        self.has_lost = False
        self.has_won = False
        self.end_state_grid_location = 0
        self.draw_stacker()
        self.draw_change_rows()

    async def get_grid(self):
        return self.touch_grid

    def web_paint(self, n, web_color):
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def draw_change_rows(self):
        for i in range(12):
            self.touch_grid[self.convert(i, 8)] = (255, 255, 0)
            self.touch_grid[self.convert(i, 3)] = (0, 255, 255)

    def draw_stacker(self):
        for i in range(self.Stacker.length):
            self.touch_grid[self.convert(
                self.Stacker.x_loc + i, self.Stacker.y_loc)] = (255, 0, 0)

    last_color = (0, 0, 0)

    def end_game_event(self):
        global last_color
        print(self.end_state_grid_location)
        if (self.end_state_grid_location == 6):
            tmp_color = self.blank_color
            self.blank_color = last_color
            last_color = tmp_color
        for i in range(self.end_state_grid_location,
                       12 - self.end_state_grid_location):
            for j in range(self.end_state_grid_location,
                           16 - self.end_state_grid_location):
                if ((i == (self.end_state_grid_location) or i == 11 - (self.end_state_grid_location))
                        or (j == (self.end_state_grid_location) or j == 15 - (self.end_state_grid_location))):
                    self.touch_grid[self.convert(i, j)] = last_color
                else:
                    self.touch_grid[self.convert(i, j)] = self.blank_color
        if (self.end_state_grid_location == 6):
            self.end_state_grid_location = 0
        else:
            self.end_state_grid_location += 1

    def move(self, x=0, y=0):
        # Clear Stacker

        if (self.has_won or self.has_lost):
            self.end_game_event()
        else:
            for i in range(self.Stacker.length):
                self.touch_grid[self.convert(
                    self.Stacker.x_loc + i, self.Stacker.y_loc)] = (0, 0, 0)

            # Determine direction and iterate x location
            at_left_edge = self.Stacker.x_loc == 0
            at_right_edge = self.Stacker.x_loc == self.Stacker.x_max
            if (at_left_edge or at_right_edge):
                self.direction = -self.direction
            self.Stacker.x_loc += self.direction

            self.draw_stacker()

    def check_game_state(self):
        global last_color
        if (self.Stacker.y_loc == 0):
            self.has_won = True
            last_color = (0, 255, 0)
        if (self.Stacker.y_loc != 15):
            for i in range(self.Stacker.length):
                if (self.touch_grid[self.convert(
                        self.Stacker.x_loc + i, self.Stacker.y_loc + 1)] == (0, 0, 0)):
                    self.has_lost = True
                    last_color = (255, 0, 0)
        if (self.has_won or self.has_lost):
            self.blank_color = (0, 0, 0)

    def paint(self, x, y):
        if self.has_lost or self.has_won:
            self.setup()
        else:
            self.check_game_state()
            self.Stacker.y_loc = self.Stacker.y_loc - 1
            self.SPEED = self.SPEED - .05
            if (self.Stacker.y_loc == 8):
                self.Stacker.length = 2
                self.Stacker.x_max = 10
            if (self.Stacker.y_loc == 3):
                self.Stacker.length = 1
                self.Stacker.x_max = 11

            # update slider location
            self.draw_stacker()
