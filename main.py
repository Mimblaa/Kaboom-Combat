import pygame
import pygame.locals
import threading as th
from concurrent.futures import ThreadPoolExecutor
import time


class Board:
    def __init__(self, width, height):
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption('Kaboom Combat')
        
    # TODO
    # add photo in background
    def draw(self, *args):
        self.surface.fill((230, 255, 255))
        for drawable in args:
            drawable.draw_on(self.surface)
            
        pygame.display.update()


class Drawable:

    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface([width, height], pygame.SRCALPHA, 32).convert_alpha() #check it
        self.rect = self.surface.get_rect(x=x, y=y) #check it

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)
    
        
class Hero(Drawable):
    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        super().__init__(width, height, x, y, color)
        self.surface.fill(color)
        self.width = width
        self.height = height
        
    def move(self, x, y, board):

        if self.rect.x + x <= 0 or self.rect.x + x >= board.surface.get_width() - self.width:
            x = 0
            
        if self.rect.y + y <= 0 or self.rect.y + y >= board.surface.get_height() - self.height:
            y = 0
            
        self.rect.x +=  x
        self.rect.y +=  y
            
        
class Game():
    def __init__(self, width, height):
        pygame.init()
        self.board = Board(width, height)
        self.hero1 = Hero(width=20, height=20, x=width/2, y=height/2)
        self.hero2 = Hero(width=20, height=20, x=width//3, y=height//3, color=(255, 0, 0))
        
    def run(self):
        
        while not self.handle_events():
            self.board.draw(
                self.hero1,
                self.hero2,
            )

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True
               
        key_input = pygame.key.get_pressed()   
        if key_input[pygame.K_LEFT]:
            self.hero1.move(x=-1, y=0, board=self.board)
        if key_input[pygame.K_UP]:
            self.hero1.move(x=0, y=-1, board=self.board)
        if key_input[pygame.K_RIGHT]:
            self.hero1.move(x=1, y=0, board=self.board)
        if key_input[pygame.K_DOWN]:
            self.hero1.move(x=0, y=1, board=self.board)
            
        if key_input[pygame.K_a]:
            self.hero2.move(x=-1, y=0, board=self.board)
        if key_input[pygame.K_w]:
            self.hero2.move(x=0, y=-1, board=self.board)
        if key_input[pygame.K_d]:
            self.hero2.move(x=1, y=0, board=self.board)
        if key_input[pygame.K_s]:
            self.hero2.move(x=0, y=1, board=self.board)
            
        if key_input[pygame.K_SPACE]:
                pass

   
if __name__ == "__main__":
    game = Game(800, 400)
    game.run()