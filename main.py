import pygame
import pygame.locals
import threading as th
from concurrent.futures import ThreadPoolExecutor
import time
import random
import sys


class Board:
    def __init__(self, width, height, background=None):
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption('Kaboom Combat')
        self.background = background

    def draw(self, *args):
        if self.background:
            self.surface.blit(self.background.image, (0, 0))
        else:
            self.surface.fill((255, 255, 255))

        for arg in args:
            if isinstance(arg, pygame.sprite.Group):
                arg.draw(self.surface)
            else:
                arg.draw_on(self.surface)

        pygame.display.update()


class Drawable:

    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface(
            [width, height], pygame.SRCALPHA, 32).convert_alpha()  # check it
        self.rect = self.surface.get_rect(x=x, y=y)  # check it

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)


class Hero(Drawable):
    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        super().__init__(width, height, x, y, color)
        self.surface.fill(color)
        self.width = width
        self.height = height

    def move(self, x, y, board):

        if self.rect.x + x <= board.surface.get_width()*0.25 or \
                self.rect.x + x >= board.surface.get_width() - self.width - board.surface.get_width()*0.0484:
            x = 0

        if self.rect.y + y <= board.surface.get_height()*0.04 or \
                self.rect.y + y >= board.surface.get_height() - self.height-board.surface.get_height()*0.032:
            y = 0

        self.rect.x += x
        self.rect.y += y


class Background:
    def __init__(self, image_file, width, height):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (width, height))  # resize image to fit window
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = 0

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Text:
    def __init__(self, font_size=30):
        self.font = pygame.font.SysFont(None, font_size)
        self.text = ' '
        self.color = (255, 255, 255)
        self.rect = None

    def set_text(self, text):
        self.text = text
        self.render()

    def set_color(self, color):
        self.color = color
        self.render()

    def render(self):
        self.rect = self.font.render(self.text, True, self.color)

    def draw_on(self, surface):
        if self.rect:
            surface.blit(self.rect, (0, 0))

    def show_message(self, message, board, duration=30):
        self.set_text(message)
        self.render()
        # Add a delay to show the message for `duration` seconds
        time.sleep(duration)
        # Clear the text to remove it from the screen
        self.set_text('')


class Timer:
    def __init__(self, game_time=10):
        self.clock = pygame.time.Clock()
        self.time_left = game_time

    def count_down(self):
        while self.time_left > 0:
            self.time_left -= 1
            pygame.time.wait(1000)
            self.print_time()
        pygame.event.post(pygame.event.Event(pygame.USEREVENT))
        sys.exit()

    def print_time(self):
        print(self.time_left)


class Item(Drawable):
    def __init__(self, board, width=10, height=10, color=(0, 0, 255)):
        self.width = width
        self.height = height
        self.x = random.randrange(int(board.surface.get_width(
        )*0.25), int(board.surface.get_width() - self.width - board.surface.get_width()*0.0484))
        self.y = random.randrange(int(board.surface.get_height(
        )*0.04), int(board.surface.get_height() - self.height-board.surface.get_height()*0.032))

        super().__init__(width, height, self.x, self.y, color)
        self.surface.fill(color)


class Game():
    def __init__(self, width, height):
        pygame.init()
        self.background = Background(
            'images/background.png',  width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(width=20, height=20, x=width/2, y=height/2)
        self.hero2 = Hero(width=20, height=20, x=width//3,
                          y=height//3, color=(255, 0, 0))
        self.timer = Timer()
        self.text = Text()
        self.tab = []

    def run(self):

        threads = [
            th.Thread(target=self.timer.count_down),
            th.Thread(target=self.spawn_items),
            th.Thread(target=self.text.show_message, args=("Hello, world!",self.board)),
        ]

        # Run in separate threads
        for thread in threads:
            thread.start()

        while not self.handle_events():
            self.board.draw(
                self.background,
                self.hero1,
                self.hero2,
                self.text,
                *self.tab,
            )

        # Wait until both threads have finished
        for thread in threads:
            thread.join()
        pygame.quit()

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

    def spawn_items(self):
        while True:
            item = Item(self.board)
            self.tab.append(item)
            pygame.time.wait(10000)


if __name__ == "__main__":
    game = Game(800, 400)
    game.run()
