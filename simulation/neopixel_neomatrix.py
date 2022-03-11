from emulator_backend import Adafruit_NeoPixel
from neopixel_gfx import Adafruit_GFX
from time import sleep
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


class Adafruit_NeoMatrix(Adafruit_GFX):

    def __init__(self):
        self.create_matrix(12, 16, 6, self.positions["NEO_MATRIX_TOP"] + self.positions["NEO_MATRIX_LEFT"] +
                           self.positions["NEO_MATRIX_COLUMNS"] + self.positions["NEO_MATRIX_PROGRESSIVE"])
        # Create NeoPixel object with appropriate configuration.
       # self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.begin()
        self.stored_color = (0, 0, 0)
        self.send_color = self.rgbToHex(0, 0, 0)
        self.stored_R = 0
        self.stored_G = 0
        self.stored_B = 0
        self.touch_array = [0] * 192
        self.json_array = {"array": self.touch_array}

    positions = {"NEO_MATRIX_TOP": 0, "NEO_MATRIX_BOTTOM": 1, "NEO_MATRIX_LEFT": 0, "NEO_MATRIX_RIGHT": 2,
                 "NEO_MATRIX_CORNER": 3, "NEO_MATRIX_ROWS": 0, "NEO_MATRIX_COLUMNS": 4, "NEO_MATRIX_AXIS": 4,
                 "NEO_MATRIX_PROGRESSIVE": 0, "NEO_MATRIX_ZIGZAG": 8, "NEO_MATRIX_SEQUENCE": 8}

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def rgbToHex(self, r, g, b):
        numbers = [r, g, b]
        return '#' + ''.join('{:02X}'.format(a) for a in numbers)

    def turn_on_led(self, n, color, wait_ms=50):
        self.pixels.setPixelColor(n, color)
        self.show()

    def create_matrix(self, width, height, pin, matrix_type):
        self.width = width
        self.height = height
        self.absoluteWidth = width
        self.absoluteHeight = height
        self.pin = pin
        self.matrix_type = matrix_type
        self.pixels = Adafruit_NeoPixel(
            self.width * self.height, self.pin, "NEO_GRB + NEO_KHZ800")
        self.new_touch = 0
        self.new_touch_cord = [0] * 2
        self.was_right_click = False

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    def arrayConvert(self, grid):
        blankArray = [(0, 0, 0)] * 192
        for i in range(12):
            for j in range(16):
                blankArray[i + j * 12] = grid[self.convert(i, j)]
        return blankArray

    async def update_buffer(self, grid):
        newGrid = self.arrayConvert(grid)
        for i in range(0, len(grid)):

            R = newGrid[i][0]
            G = newGrid[i][1]
            B = newGrid[i][2]
            color = (R, G, B)
            self.pixels.setPixelColor(i, color)
            self.send_color = self.rgbToHex(R, G, B)
            self.touch_array[i] = self.send_color
        self.show()

    def delay(self, ms):
        sleep(ms / 1000)

    def begin(self):
        self.new_touch_cord = [0] * 2
        needed_w = self.width * 35
        needed_h = self.height * 34 + 4
        self.pixels.begin(draw_matrix=True, width=self.width,
                          height=self.height, window_w=needed_w, window_h=needed_h)

    def drawPixel(self, x, y, color):
        x, y = self.mapPixelToRotation(x, y)
        if x is None or y is None:
            pass
        else:
            self.pixels.setPixelColor(y * self.width + x, color)

    def show(self):
        self.pixels.gui.render()
        self.new_touch = self.pixels.gui.new_touch
        self.new_touch_cord = self.pixels.gui.new_touch_cord
        self.was_right_click = self.pixels.gui.was_right_click
        event = self.pixels.gui.dispatch_events()

    def setBrightness(self, new_brightness):  # use opacity to represent this
        if new_brightness >= 0 and new_brightness <= 100:
            self.brightness = new_brightness
            self.pixels.gui.change_brightness(self.brightness)
        else:
            return False


bitmap_array = [0x00, 0x84 >> 1, 0x84 >> 1,
                0x00, 0x00, 0x84 >> 1, 0x78 >> 1, 0x00]


if __name__ == "__main__":
    matrix = Adafruit_NeoMatrix()
    matrix.create_matrix(12, 16, 6, matrix.positions["NEO_MATRIX_TOP"] + matrix.positions["NEO_MATRIX_LEFT"] +
                         matrix.positions["NEO_MATRIX_COLUMNS"] + matrix.positions["NEO_MATRIX_PROGRESSIVE"])
    matrix.begin()
    matrix.show()
    matrix.setRotation(0)
    matrix.setBrightness(90)
    matrix.show()
    matrix.drawPixel(0, 0, (200, 0, 0))
    matrix.drawPixel(5, 5, (200, 0, 100))
    matrix.drawPixel(0, 1, (0, 200, 0))
    matrix.drawPixel(0, 2, (0, 0, 200))
    matrix.show()
    matrix.delay(6000)
    while True:
        matrix.show()
        matrix.delay(10)
        if (matrix.new_touch == 1):
            matrix.drawPixel(
                matrix.new_touch_cord[0], matrix.new_touch_cord[1], (200, 0, 0))
            matrix.pixels.gui.new_touch = 0
