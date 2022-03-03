import numpy as np
import math
import asyncio
import json

def Color(red, green, blue):
    return (red << 16) | (green << 8) | blue

class imageshowApp:
    def __init__(self):
        self.touchGrid = [(0,0,0)]*192
        self.IS_TIMER_BASED = False
        self.showimage=0
        self.file=None
        self.setup()
    
    def paint(self,x,y):
        pass
    def setup(self):
        pass

    def read_new(self,img):
        self.showimage=1
        self.file=img

    def convert(self, x, y):
        # if in an odd column, reverse the order
        if (x % 2 != 0):
            y = 15 - y
        return (x * 16) + y
    
    async def getGrid(self):
        return self.touchGrid

    def display(self):
        self.touchGrid=self.arrayConvert(self.image_processing())
        self.showimage=0

    def arrayConvert(self, grid):
        blankArray = [(0,0,0)]*192
        for i in range(12):
            for j in range(16):
                blankArray[self.convert(i,j)] = tuple(grid[j,i]) # haven't tested
        return blankArray

    def image_processing(self):
        if self.file != None:
            decodedArray = json.loads(self.file["file"])
            image = np.asarray(decodedArray["array"])
            x=image.shape[1]
            y=image.shape[0]
            rotate_image=image.copy()
            if x>y:
                rotate_image=np.zeros((x,y,3), dtype='int')
                rotate_image[:,:,0] = image[:,:,0].T
                rotate_image[:,:,0] = np.fliplr(rotate_image[:,:,0])  # transpose and flip can rotate 90 degree
                rotate_image[:,:,1] = image[:,:,1].T
                rotate_image[:,:,1] = np.fliplr(rotate_image[:,:,1])
                rotate_image[:,:,2] = image[:,:,2].T
                rotate_image[:,:,2] = np.fliplr(rotate_image[:,:,2])
                x=image.shape[0]
                y=image.shape[1]
            output=np.zeros((16,12,3), dtype='int')
            x_ds=float(x-1)/(12 - 1)
            y_ds=float(y-1)/(16 - 1)
            for k in range(0,3):
                for i in range(0,16):
                    for j in range(0,12):
                        x_low=math.floor(x_ds*j)
                        x_high=math.ceil(x_ds*j)
                        y_low=math.floor(y_ds*i)
                        y_high=math.ceil(y_ds*i)
                            
                        fir_pix=rotate_image[y_low, x_low, k]
                        sec_pix=rotate_image[y_low, x_high, k]
                        thir_pix=rotate_image[y_high, x_low, k]
                        four_pix=rotate_image[y_high, x_high, k]
                            
                        x_weight = (x_ds * j) - x_low
                        y_weight = (y_ds * i) - y_low
                            
                        output[i,j,k]=fir_pix * (1 - x_weight) * (1 - y_weight) + sec_pix * x_weight * (1 - y_weight) + thir_pix * y_weight * (1 - x_weight) + four_pix * x_weight * y_weight
            return output
        return self.touchGrid