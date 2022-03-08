import asyncio
import chess
#from rpi_ws281x import Color

pieceColors = {
    'r': (255, 50, 0),
    'n': (255, 150, 0),
    'b': (255, 255, 0),
    'q': (125, 50, 0),
    'k': (125, 150, 0),
    'p': (175, 255, 0),

    'R': (0, 50, 255),
    'N': (0, 150, 255),
    'B': (0, 255, 255),
    'Q': (0, 50, 125),
    'K': (0, 150, 125),
    'P': (0, 255, 125),
    '.': (0, 0, 0)
}


def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue


class chessApp:
    def __init__(self):
        self.board = chess.Board()
        self.touchGrid = [(0, 0, 0)]*192
        self.moveState = 0  # 0 - selecting piece, 1 - selecting move
        self.moveOptions = []
        self.selectedPiece = 0
        self.checkMate = 0
        self.boardState = []
        self.IS_TIMER_BASED = False
        self.SPEED = 1
        self.setup_chess()

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def chessConvert(self, x, y):
        n = x * 8 + y
        locationCode = chr(y + 97) + str(x + 1)
        return n, locationCode

    def chessConvertToIndex(self, stringVal):
        x = int(stringVal[1]) - 1
        y = ord(stringVal[0]) - 97
        return x, y
    # https://stackoverflow.com/questions/5661725/format-ints-into-string-of-hex

    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def setup_chess(self):
        print("chess start")
        self.boardState = str(self.board).replace('\n', ' ').split(' ')
        for x in range(1, 9):
            for y in range(8):
                self.touchGrid[self.convert(
                    x-1, y)] = pieceColors[self.boardState[(8-x)*8+y]]
        # print(self.boardState)

    async def getGrid(self):
        return self.touchGrid

    def webPaint(self, n, webColor):
        x = int(n/16)
        y = int(n-x*16)
        self.paint(x, y)

    def updateBoard(self):
        self.boardState = str(self.board).replace('\n', ' ').split(' ')
        for x in range(1, 9):
            for y in range(8):
                self.touchGrid[self.convert(
                    x-1, y)] = pieceColors[self.boardState[(8-x)*8+y]]

    def paint(self, x, y):
        n, locationCode = self.chessConvert(x, y)

        if (locationCode not in self.moveOptions):
            self.moveState = 0
            self.selectedPiece = locationCode
        else:
            self.moveState = 1
        if (self.moveState == 0):
            for i, x in enumerate(list(self.board.legal_moves)):
                # print(x)
                if (str(x)[0:2] == locationCode):
                    newX, newY = self.chessConvertToIndex(str(x)[2:4])
                    self.touchGrid[self.convert(newX, newY)] = (0, 255, 255)
                    self.moveOptions.append(str(x)[2:4])
        if (self.moveState == 1):
            move = chess.Move.from_uci(
                str(self.selectedPiece) + str(locationCode))
            # print(move)
            self.board.push(move)
            self.updateBoard()
            self.selectedPiece = 0
            self.moveOptions = []
            self.moveState = 0
        # print(self.moveOptions)
