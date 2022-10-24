import pygame
from Cubics import Cubics, colors
import minizinc
from datetime import timedelta
import os
import threading

width = 700
height = 650
gameWidth = 100  # meaning 300 // 10 = 30 width per block
gameHeight = 400  # meaning 600 // 20 = 20 height per blo ck
blockSize = 20
 
topLeft_x = (width - gameWidth) // 2
topLeft_y = height - gameHeight - 50

font_small_size = 18
font_medium_size = 35
font_big_size = 60
font_bigger_size = 80

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cubics")
pygame.init()

font_small = pygame.font.SysFont('hpsimplified', font_small_size, False, False) 
font_medium = pygame.font.SysFont('hpsimplified', font_medium_size, False, False) 
font_big = pygame.font.SysFont('hpsimplified', font_big_size, False, False)
font_bigger = pygame.font.SysFont('hpsimplified', font_bigger_size, True, False)

class Button:

    def __init__(self, rect, text, function, kwargs=None):
        self.rect = rect
        self.text = text
        self.function = function
        self.args = kwargs
        self.background = "#202020"

    def on_click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    if self.args == None:
                        self.function()
                    else:
                        self.function(**self.args)

    def show(self):
        draw_box(screen, self.rect, self.background)
        rendered_text = font_medium.render(self.text, True, "#A5C9CA")
        displace_h = rendered_text.get_bounding_rect()[2] // 2
        displace_v = rendered_text.get_bounding_rect()[3] // 2

        screen.blit(rendered_text, (self.rect[0] + self.rect[2]//2 - displace_h, self.rect[1] + self.rect[3]//2 - displace_v))

    def on_hover(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x,y):
            self.background = "#404040"
        else:
            self.background = "#202020"

def draw_box(screen, rect, background):
    pygame.draw.rect(
        screen,
        background,
        rect
    )
    pygame.draw.rect(
        screen,
        "#E7F6F2",
        [rect[0] - 1, rect[1] - 1, rect[2] + 2, rect[3] + 3],
        1
    )

def update_UI(game):
    cubics_label = font_big.render("Cubics", True, '#A5C9CA')
    screen.blit(cubics_label, [(width // 2) - 60, 30])

    draw_box(screen, [game.x + game.width * game.zoom + 50, game.y + 50, 260, 50], "#202020")
    score_text = font_medium.render("Score", True, '#A5C9CA')
    score_points = font_medium.render(str(game.score),True, "#A5C9CA")
    screen.blit(score_text, [game.x + game.width * game.zoom + 140, game.y + 8])
    screen.blit(score_points, [game.x + game.width * game.zoom + 60, game.y + 58])
        
    label = font_medium.render("Next Shape", True, '#A5C9CA')        
    draw_box(screen,[game.x + game.width * game.zoom + 50, game.y + 199, 260, 300], "#202020")
    screen.blit(label, [game.x + game.width * game.zoom + 100, game.y + 148])    
        
    sy =  game.x + game.width * game.zoom + 180 - ((game.next_block.width * 50) // 2)
    sx = game.y + 350 - ((game.next_block.height * 50) // 2)

    for i in range(game.next_block.width):
        for j in range(game.next_block.height):
            pygame.draw.rect(screen, '#202020', [sy + 50*i, sx + 50*j, 50, 50], 1)
            pygame.draw.rect(screen, colors[game.next_block.color],[sy + i*50 + 1, sx + j*50 + 1, 48, 49])

def update_field_UI(game):
    #displaying field
        screen.fill('#2C3333')
        pygame.draw.rect(
            screen,
            "#E7F6F2",
            [game.x - 1, game.y - 1,game.width * game.zoom + 3, game.height * game.zoom + 3],
            1
        )
        pygame.draw.rect(
            screen,
            "#202020",
            [game.x, game.y,game.width * game.zoom, game.height * game.zoom ],
        )

        #displaying blocks
        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(screen, '#202020', [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                if game.field[i][j] > 0:
                    pygame.draw.rect(screen, colors[game.field[i][j]],
                                     [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 1, game.zoom - 1])

#regular game
def start_game():    
    done = False
    clock = pygame.time.Clock()
    fps = 25
    game = Cubics(10,20)
    counter = 0

    while not done:
        
        #checks for current block to be initialized
        if game.current_block is None:
            game.gen_new_block()
        if game.next_block is None:
            game.gen_next_block()
        
        #keep track of time
        counter += 1 
        if counter > 100000:
            counter = 0

        #move piece down based on level
        if counter % (fps // game.level // 2) == 0:
            if game.state == "start":
                game.move_down() 
        
        #event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_LEFT:
                    game.move_hor(-1)
                if event.key == pygame.K_RIGHT:
                    game.move_hor(1)
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)

        if game.state == "game over":
            pygame.quit()

        #UI updates
        update_field_UI(game)        
        update_UI(game)        
        pygame.display.flip()
        clock.tick(fps)

#just for testing
def load_data():
    
    instance_path = 'ins-39.txt'

    file = open(instance_path, 'r')
    lines = file.readlines()
    count = 0
    widths = []
    heights = []

    for line in lines:

        if count == 0:
            w = int(line)

        elif count == 1:
            n = int(line)

        else:
            chip_wh = line.split()
            widths.append(int(chip_wh[0]))
            heights.append(int(chip_wh[1]))

        count += 1

    return w, n, widths, heights

#send the informations to the minizinc solver
def solve(return_storing):
    model = minizinc.Model(os.path.join(
        os.path.dirname("__file__"),
        'MODEL_STD.mzn'
    ))
    w, n, widths, heights = load_data()
    solver = minizinc.Solver.lookup('chuffed')
    inst = minizinc.Instance(solver, model)
    inst["w"] = w
    inst["n"] = n
    inst["widths"] =widths
    inst["heights"] = heights

    out = inst.solve(timeout=timedelta(seconds=300), free_search=True)
    return_storing["solutions"] = out.solution

#automatic computer playing
def start_game_solver():
    done = False
    clock = pygame.time.Clock()
    fps = 25
    game = Cubics(10,20)
    counter = 0
    return_storing = {}
    
    #creates the main thread for solving and start it
    thread = threading.Thread(target = solve, args=(return_storing,))
    thread.start()
    while not done:
        
        #checks for current block to be initialized
        if game.current_block is None:
            game.gen_new_block()
        if game.next_block is None:
            game.gen_next_block()
        
        #keep track of time
        counter += 1 
        if counter > 100000:
            counter = 0

        #move piece down based on level
        if counter % (fps // game.level // 2) == 0:
            if game.state == "start":
                game.move_down() 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_LEFT:
                    game.move_hor(-1)
                if event.key == pygame.K_RIGHT:
                    game.move_hor(1)
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)
        
        #todo minizinc solver
        if not thread.is_alive(): 
            print(return_storing["solutions"]) 

            #update view

            thread = threading.Thread(target=solve, args=(return_storing, ))
            thread.start()

        #UI updates
        update_field_UI(game)
        update_UI(game)        
        pygame.display.flip()
        clock.tick(fps)



run = True
while run:    
    
    screen.fill("#2C3333")

    title = font_bigger.render("Cubics", True, "#A5C9CA")
    screen.blit(title, [width//2 - title.get_bounding_rect()[2]//2, 50])
    
    button1 = Button(
        pygame.Rect(width//2 - 125, 250, 250, 70),
        "Play", 
        start_game
    )
    button1.on_hover()

    button2 = Button(
        pygame.Rect(width//2 - 125, 370, 250, 70), 
        "Computer",
        start_game_solver
    )
    button2.on_hover()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        button1.on_click(event)
        button2.on_click(event)

    button1.show()
    button2.show()

    bottom_page = font_small.render("Lorenzo Tribuiani | Matteo Rossi - 2022", True, "#A5C9CA")
    screen.blit(bottom_page, [width//2 - bottom_page.get_bounding_rect()[2]//2, 600])
    pygame.display.update()
pygame.quit()