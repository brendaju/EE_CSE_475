import asyncio
#from rpi_ws281x import Color

def color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class TicTacToeApp:
    def __init__(self):
        self.current_player = 'X'
        self.touch_grid = [(0, 0, 0)] * 192
        self.game_grid = ['-'] * 10
        self.game_over = 0
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.setup_tictactoe()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def game_convert(self, x, y):
        if (y >= 3 and y <= 5):
            game_index = 0
            game_y = 0
        elif (y >= 7 and y <= 9):
            game_index = 3
            game_y = 1
        elif (y >= 11 and y <= 13):
            game_index = 6
            game_y = 2
        else:
            return -1, -1, -1

        if (x >= 1 and x <= 3):
            game_index = game_index
            game_x = 0
        elif (x >= 5 and x <= 7):
            game_index = game_index + 1
            game_x = 1
        elif (x >= 9 and x <= 11):
            game_index = game_index + 2
            game_x = 2
        else:
            return -1, -1, -1

        return game_index, game_x, game_y

    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
    def rgb_to_hex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_tictactoe(self):
        self.current_player = 'X'
        self.touch_grid = [(0, 0, 0)] * 192
        self.game_grid = ['-'] * 10
        self.game_over = 0
        for i in range(1, 12):
            self.touch_grid[self.convert(i, 6)] = (200, 200, 200)
            self.touch_grid[self.convert(i, 10)] = (200, 200, 200)

        for i in range(3, 14):
            self.touch_grid[self.convert(4, i)] = (200, 200, 200)
            self.touch_grid[self.convert(8, i)] = (200, 200, 200)

    async def get_grid(self):
        return self.touch_grid

    def board_check(self):
        if (self.game_grid[0] == self.game_grid[1] ==
                self.game_grid[2] and self.game_grid[0] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(i + 1, 4)] = (255, 0, 0)
            return 1
        elif (self.game_grid[3] == self.game_grid[4] == self.game_grid[5] and self.game_grid[3] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(i + 1, 8)] = (255, 0, 0)
            return 1
        elif (self.game_grid[6] == self.game_grid[7] == self.game_grid[8] and self.game_grid[6] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(i + 1, 12)] = (255, 0, 0)
            return 1
        elif (self.game_grid[0] == self.game_grid[3] == self.game_grid[6] and self.game_grid[0] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(2, 3 + i)] = (255, 0, 0)
            return 1
        elif (self.game_grid[1] == self.game_grid[4] == self.game_grid[7] and self.game_grid[1] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(6, 3 + i)] = (255, 0, 0)
            return 1
        elif (self.game_grid[2] == self.game_grid[5] == self.game_grid[8] and self.game_grid[2] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(10, 3 + i)] = (255, 0, 0)
            return 1
        elif (self.game_grid[0] == self.game_grid[4] == self.game_grid[8] and self.game_grid[0] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(i + 1, i + 3)] = (255, 0, 0)
            return 1
        elif (self.game_grid[2] == self.game_grid[4] == self.game_grid[6] and self.game_grid[2] != '-'):
            for i in range(11):
                self.touch_grid[self.convert(i + 1, 13 - i)] = (255, 0, 0)
            return 1
        else:
            return 0

    def web_paint(self, n, web_color):
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def paint(self, x, y):
        game_index, game_x, game_y = self.game_convert(x, y)
        if (self.game_over == 1):
            self.setup_tictactoe()
            return
        if (game_index == -1 or self.game_grid[game_index] != '-'):
            return

        self.game_grid[game_index] = self.current_player

        if (self.current_player == 'X'):
            self.touch_grid[self.convert(
                (game_x * 4 + 1), (game_y * 4 + 3))] = (255, 0, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 3), (game_y * 4 + 3))] = (255, 0, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 2), (game_y * 4 + 4))] = (255, 0, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 1), (game_y * 4 + 5))] = (255, 0, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 3), (game_y * 4 + 5))] = (255, 0, 255)
        else:
            self.touch_grid[self.convert(
                (game_x * 4 + 2), (game_y * 4 + 3))] = (0, 255, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 1), (game_y * 4 + 4))] = (0, 255, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 3), (game_y * 4 + 4))] = (0, 255, 255)
            self.touch_grid[self.convert(
                (game_x * 4 + 2), (game_y * 4 + 5))] = (0, 255, 255)

        self.game_over = self.board_check()

        if (self.current_player == 'X'):
            self.current_player = 'O'
        else:
            self.current_player = 'X'
