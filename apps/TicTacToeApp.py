import asyncio
#from rpi_ws281x import Color

def color(red, green, blue):
    '''
    Takes in the red, green, and blue values and converts them to the
    proper format for the LED strip. From the LED strip library
    '''
    return (red << 16) | (green << 8) | blue

class TicTacToeApp:
    '''
    Initiates the TicTacToe app. In addition to the standard
    app variables it also has:
        Current player to represent the current active player
        Game_grid, a smaller grid used to determine the game state
        Game_over to set determine whether or not the game has ended
    '''
    def __init__(self):
        self.current_player = 'X'
        self.touch_grid = [(0, 0, 0)] * 192
        self.game_grid = ['-'] * 10
        self.game_over = 0
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.setup_tictactoe()

    def convert(self, x, y):
        '''
        Converts x and y to the equivalent index in the grid
        if in an odd column, reverse the order
        '''
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def game_convert(self, x, y):
        '''
        Converts an x and y input into the equivalent
        game x and y coordinates as well as finds the
        index in the game_grid array
        '''
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

    def rgb_to_hex(self, r, g, b):
        '''
        Converts an give r g b value to the equivalent Hex form with
        the format #FFFFFF
        Based on: https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex
        '''
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_tictactoe(self):
        '''
        Initializes the tic tac toe game to have current player
        be X's, clears the game_grid and sets the touch grid to have
        the tic-tac-toe board displayed in grey
        '''
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
        '''
        Sends the touch_grid
        '''
        return self.touch_grid

    def board_check(self):
        '''
        Checks if their is a winner of the current game
        if there is, draws a red line over the middle of the
            winning line and returns 1
        Otherwise returns 0
        '''
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
        '''
        Takes the web input index and converts it to the
        equivalent x and y coordinate and then runs the user
        input function
        '''
        x = int(n / 16)
        y = int(n - x * 16)
        self.paint(x, y)

    def paint(self, x, y):
        '''
        Determines users game input based on the x and y input
            if the game is over, resets the game
            if the input is outside of the board or is in a square
                already selected, does nothing
            if it is a valid input, it sets that space in the game_grid
                to the current players symbol and then updates the
                touch_grid to display it
            At the end checks the board state for a winner and sets the
                current player to be the other player
        '''
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
