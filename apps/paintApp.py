import asyncio
#from rpi_ws281x import Color

# The default set of colors that can be selected
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

'''
Takes in the red, green, and blue values and converts them to the
proper format for the LED strip. From the LED strip library
'''
def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue


class paintingApp:
    '''
    Initiates the painting app as a non-timer based app
    '''
    def __init__(self):
        self.stored_color = Color(0, 0, 0) # Current color being used
        self.clearingMode = 1 # Set to 1 if each input should set pixels to be off
        self.send_color = self.rgbToHex(0, 0, 0) # Color to be sent to the website
        self.stored_R = 0
        self.stored_G = 0
        self.stored_B = 0
        self.touchGrid = [(0, 0, 0)] * 192
        self.IS_TIMER_BASED = False
        self.SPEED = 0
        self.setup_painting()

    '''
    Converts a given x and y value to the proper index for the touch grid
    '''
    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    '''
    Converts an give r g b value to the equivalent Hex form with
    the format #FFFFFF
    '''
    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    '''
    Sets up the painting app. This sets the selection row pixels
    to all have the correct selection colors 
    '''
    def setup_painting(self):
        for i in range(8):
            n = self.convert(i, 15)
            self.touchGrid[n] = (
                setColors[i][0], setColors[i][1], setColors[i][2])
        self.touchGrid[self.convert(8, 15)] = (0, 0, 255)
        self.touchGrid[self.convert(9, 15)] = (0, 255, 0)
        self.touchGrid[self.convert(10, 15)] = (255, 0, 0)
        self.touchGrid[self.convert(11, 15)] = (
            self.stored_R, self.stored_G, self.stored_B)

    '''
    Gets the current grid with all pixel colors from the app
    '''
    async def getGrid(self):
        return self.touchGrid

    '''
    Determines the x and y value of the grid based on the
    input from the remote website. Then sets that index in the
    to be equal to the color sent from the website
    '''
    def webPaint(self, n, webColor):
        x = int(n / 16)
        y = int(n - x * 16)
        self.touchGrid[self.convert(x, y)] = webColor
    '''
    Takes in x and y from board input and either changes
    that pixel to be the current selected color, or, if the pixel
    touched is in the selection row, changes the selected color accordingly
    '''
    def paint(self, x, y):
        if y == 15:
            if x < 8:
                self.stored_R, self.stored_G, self.stored_B = setColors[x]
            elif x == 8:
                self.stored_B = self.stored_B + 10
                if self.stored_B < 50 or self.stored_B > 255:
                    self.stored_B = 50
            elif x == 9:
                self.stored_G = self.stored_G + 10
                if self.stored_G < 50 or self.stored_G > 255:
                    self.stored_G = 50
            elif x == 10:
                self.stored_R = self.stored_R + 10
                if self.stored_R < 50 or self.stored_R > 255:
                    self.stored_R = 50
            self.touchGrid[176] = (self.stored_R, self.stored_G, self.stored_B)
            self.clearingMode = (x == 7)
            self.send_color = self.rgbToHex(
                self.stored_R, self.stored_G, self.stored_B)
        else:
            self.touchGrid[self.convert(x, y)] = (
                self.stored_R, self.stored_G, self.stored_B)
            print(self.stored_R, self.stored_G, self.stored_B)
            if(self.clearingMode):
                self.send_color = '#505050'
            elif (self.stored_R == self.stored_G and self.stored_R == self.stored_B):
                self.send_color = '#FFFFFF'
            else:
                self.send_color = self.rgbToHex(
                    self.stored_R, self.stored_G, self.stored_B)
