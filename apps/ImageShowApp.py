"""
Creates the image show app. It reads a jpg file and downscale it to 12x16 size 
so that the board can display the image.
"""
import numpy as np
import math
import asyncio
import json

class ImageShowApp: 
    def __init__(self):
        """
        Initiates the Image Show app as a non-timer based app
        with the current file.
        """
        self.touch_grid = [(0, 0, 0)] * 192
        self.IS_TIMER_BASED = False
        self.file = None
        self.SPEED = 0.1
        self.setup()

    def paint(self, x, y):
        pass

    def setup(self):
        pass

    def read_new(self, img):
        """
        Change the current file to the given image and make
        the app as a timer based app.
        """
        self.IS_TIMER_BASED = True
        self.file = img

    def convert(self, x, y):
        '''
        Convert a given x and y value to the proper index for the touch grid
        '''
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y

    async def get_grid(self):
        '''
        Get the current grid with all pixel colors from the app
        '''
        return self.touch_grid

    def move(self):
        """
        Update the touch grid based on current timer status
        """
        self.touch_grid = self.array_convert(self.image_processing())
        self.IS_TIMER_BASED = False

    def array_convert(self, grid):
        """
        Convert the processed image to touch grid
        """
        blank_array = [(0, 0, 0)] * 192
        for i in range(12):
            for j in range(16):
                current_r = np.int32(grid[j, i][0])
                current_r = current_r.item()
                current_g = np.int32(grid[j, i][1])
                current_g = current_g.item()
                current_b = np.int32(grid[j, i][2])
                current_b = current_b.item()
                blank_array[self.convert(i, j)] = (current_r, current_g, current_b)
        return blank_array

    def image_processing(self):
        """
        Process the current file. Rotate 90 degrees if the image's width is
        bigger than height. Then use bilinear interpolation to downscale the image
        to 12x16 size.
        """
        if self.file is not None:
            decoded_array = json.loads(self.file["file"])
            image = np.asarray(decoded_array["array"])
            x = image.shape[1]
            y = image.shape[0]
            rotate_image = image.copy()
            # rotate the image based on the size
            if x > y:
                rotate_image = np.zeros((x, y, 3), dtype='int')
                rotate_image[:, :, 0] = image[:, :, 0].T
                # transpose and flip can rotate 90 degree
                rotate_image[:, :, 0] = np.fliplr(rotate_image[:, :, 0])
                rotate_image[:, :, 1] = image[:, :, 1].T
                rotate_image[:, :, 1] = np.fliplr(rotate_image[:, :, 1])
                rotate_image[:, :, 2] = image[:, :, 2].T
                rotate_image[:, :, 2] = np.fliplr(rotate_image[:, :, 2])
                x = image.shape[0]
                y = image.shape[1]
            # bilinear interpolation
            output = np.zeros((16, 12, 3), dtype='int')
            x_ds = float(x - 1) / (12 - 1)
            y_ds = float(y - 1) / (16 - 1)
            for k in range(0, 3):
                for i in range(0, 16):
                    for j in range(0, 12):
                        x_low = math.floor(x_ds * j)
                        x_high = math.ceil(x_ds * j)
                        y_low = math.floor(y_ds * i)
                        y_high = math.ceil(y_ds * i)

                        fir_pix = rotate_image[y_low, x_low, k]
                        sec_pix = rotate_image[y_low, x_high, k]
                        thir_pix = rotate_image[y_high, x_low, k]
                        four_pix = rotate_image[y_high, x_high, k]

                        x_weight = (x_ds * j) - x_low
                        y_weight = (y_ds * i) - y_low

                        output[i, j, k] = fir_pix * (1 - x_weight) * (1 - y_weight) + sec_pix * x_weight * (
                            1 - y_weight) + thir_pix * y_weight * (1 - x_weight) + four_pix * x_weight * y_weight
            return output
        return self.touch_grid
