class NumberDisplay:
    def __init__(self, x=0, y=0, num=0):
        self.start_x = x
        self.start_y = y
        self.current = num
        self.array = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1]

    def display_number(self):

        if self.number.current == 1:
            self.number.array = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]

        if self.number.current == 2:
            self.number.array = [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1]

        if self.number.current == 3:
            self.number.array = [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]

        if self.number.current == 4:
            self.number.array = [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1]

        if self.number.current == 5:
            self.number.array = [1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1]

        if self.number.current == 6:
            self.number.array = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1]

        if self.number.current == 7:
            self.number.array = [1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]

        if self.number.current == 8:
            self.number.array = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]

        if self.number.current == 9:
            self.number.array = [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1]

        for i in range(0, 5):
            for j in range(0, 3):
                if (self.number.array[i * 3 + j] == 1):
                    self.touch_grid[self.convert(
                        self.number.start_x + j, self.number.start_y + i)] = (255, 255, 255)
                else:
                    self.touch_grid[self.convert(
                        self.number.start_x + j, self.number.start_y + i)] = (0, 0, 0)
