from random import randint
import numpy as np
from copy import deepcopy

#GLOBAL VARIABLE DECLARATIONS
#---------------------------------
colors = {
    5 : "#0341AE",
    6 : "#72CB3B",
    7 : "#FFD500",
    8 : "#FF971C",
    9 : "#FF3213" 
}

min_size = 1
max_size = 3
max_color_key = max(colors.keys()) 
min_color_key = min(colors.keys())


#MAIN CLASSES
#------------------------------------------

class Block:

    width = 0
    height = 0
    x = 0
    y = 0
    color = 0
    game_size = None
    field_view = None

    def __init__(self, width, height, x, y, color, game_size):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = color
        self.game_size = game_size
        self.update_field()

    def move_ver(self, value):
        self.y += value
        self.update_field()

    def move_hor(self, value):
        self.x += value
        self.update_field()

    def rotate(self):
        temp = self.width
        self.width = self.height
        self.height = temp
        self.update_field()

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.update_field()

    def update_field(self):
        self.field_view = np.zeros((self.game_size[1], self.game_size[0]), dtype= np.int8)
        self.field_view[self.y:(self.y + self.height), self.x:(self.x+self.width)] = self.color



class Cubics:

    state = "start"
    level = 1
    score = 0
    height = 0
    width = 0
    x = 100
    y = 120
    zoom = 25
    field = []

    def __init__(self, width, height):
        self.height = height
        self.width = width  
        self.state = "start"   
        self.score = 0
        self.blocks = []
        self.current_block = None
        self.next_block = None
        self.update_field()
    
    #generates a new block
    def gen_new_block(self):

        width = randint(min_size, max_size)
        height = randint(min_size, max_size)
        pos_x = (self.width // 2) - (width // 2)
        
        self.current_block = Block(
            width,
            height,
            pos_x,
            0,
            randint(min_color_key, max_color_key),
            (self.width, self.height)
        )
        self.blocks.append(self.current_block)
        self.update_field()
        
    
    #generate next block
    def gen_next_block(self):
        width = randint(min_size, max_size)
        height = randint(min_size, max_size)
        pos_x = (self.width // 2) - (width // 2)

        self.next_block = Block(
            width,
            height,
            pos_x,
            0,
            randint(min_color_key, max_color_key),
            (self.width, self.height)
        )

    def remove_current_block(self):
        self.blocks.remove(self.current_block)
        self.update_field()
    
    #update matrix
    def update_field(self):
        self.field = np.zeros((self.height, self.width), dtype=np.int8)
        for block in self.blocks:
            self.field = self.field + block.field_view

    #collision detection algorithm
    def check_sides(self):
        
        if self.current_block.x < 0 or \
            self.current_block.x + self.current_block.width - 1 > self.width - 1 or \
                self.current_block.y + self.current_block.height - 1 > self.height - 1:
                return True

        for i in range(self.current_block.x, self.current_block.x + self.current_block.width):
            if self.field[self.current_block.y + self.current_block.height - 1][i] > 9 :
                return True

        for i in range(self.current_block.y, self.current_block.y + self.current_block.height):
            if self.field[i][self.current_block.x] > 9 or \
                self.field[i][self.current_block.x + self.current_block.width-1] > 9:
                return True

        return False

    #move the current block down
    def move_down(self):
        self.current_block.move_ver(1)
        self.update_field()
        if self.check_sides():
            self.current_block.move_ver(-1)
            self.update_field()
            self.freeze()

    #move the current block horizontally
    def move_hor(self, value):
        self.current_block.move_hor(value)
        self.update_field()
        if self.check_sides():
            self.current_block.move_hor(-value)
            self.update_field()         

    #rotate the current block
    def rotate(self):
        self.current_block.rotate() 
        self.update_field()
        if self.check_sides():
            self.current_block.rotate() 
            self.update_field()

    def move_to(self,x, y):
        self.current_block.move_to(x,y)
        self.update_field()
        self.freeze()
        

    #check for lines deletion
    def check_lines(self):
        lines = []
        for i in range(self.height):
            if np.all(self.field[:][i]):
                lines.append(i)

        if len(lines) > 0:

            self.score += len(lines)*10
            eliminated = []

            for block in self.blocks:
                for i in lines:

                    if block.y <= i < block.y + block.height:
                        block.y += 1
                        block.height -= 1
                        if block.height <= 0:
                            eliminated.append(block)
                        else:
                            block.update_field()

                    elif block.y < i:
                        block.y += 1
                        block.update_field()

            for i in eliminated:
                self.blocks.remove(i)

            self.update_field()        

    #check game state afert a collision
    def freeze(self):
        self.check_lines()
        self.current_block = self.next_block
        self.gen_next_block()
        self.blocks.append(self.current_block)
        if self.check_sides():
            self.remove_current_block()
            self.current_block = None
            self.state = "game over"

    def get_y_positions(self):
        y_pos = []
        temp_field = self.field - self.current_block.field_view
        temp_field[temp_field < 0] = 0
        for i in range(10):
            for j in range(20):
                if temp_field[j][i] != 0:
                    y_pos.append(19 - j + 1)
                    break
                elif temp_field[j][i] == 0 and j == 19:
                    y_pos.append(0)

        return y_pos

    def get_normalized_field(self):
        field = deepcopy(self.field)
        field -= self.current_block.field_view
        field[field < 0] = 0
        field[field > 0] = 1
        return field





    
        






