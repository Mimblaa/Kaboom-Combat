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
            elif isinstance(arg, Hero):
                arg.draw_on(self.surface)
                for heart in arg.hearts:
                    heart.draw_on(self.surface)
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
    def __init__(self, width, height, x, y, color=(0, 255, 0), lives=3, name="Player"):
        super().__init__(width, height, x, y, color)
        self.surface.fill(color)
        self.width = width
        self.height = height
        self.lives = lives
        self.name = name
        self.hearts = []

    def set_hearts(self, hearts):
        self.hearts = hearts
        self.update_hearts()

    def update_hearts(self):
        for i, heart in enumerate(self.hearts):
            if i < self.lives:
                heart.live_type = True
            else:
                heart.live_type = False
            heart.update_image()

    def move(self, x, y, board):

        if self.rect.x + x <= board.surface.get_width()*0.25 or \
                self.rect.x + x >= board.surface.get_width() - self.width - board.surface.get_width()*0.0484:
            x = 0

        if self.rect.y + y <= board.surface.get_height()*0.04 or \
                self.rect.y + y >= board.surface.get_height() - self.height-board.surface.get_height()*0.032:
            y = 0

        self.rect.x += x
        self.rect.y += y

    def remove_live(self):
        if self.lives > 1:
            self.lives -= 1
        elif self.lives == 1:
            self.lives -= 1
            print("Player " + self.name + " is dead")
        self.update_hearts()


class Heart:
    def __init__(self, width, height, live_type, number, player):
        self.width = width
        self.height = height
        self.x_pos = width * 0.09 + (number - 1) * width * 0.029
        self.y_pos = height * 0.52 + (player - 1) * height * 0.308
        self.live_type = live_type
        self.update_image()

    def update_image(self):
        if self.live_type:
            image_file = 'images/full_heart.png'
        else:
            image_file = 'images/dead_heart.png'

        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.023), int(self.height * 0.035)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


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


class Timer():
    def __init__(self, width,game_time=10):
        self.clock = pygame.time.Clock()
        self.time_left = game_time
        self.clock_format = ""
        #calculate font size based on screen width
        self.font = pygame.font.SysFont('monospace', int(width*0.045))

    def count_down(self):
        while self.time_left > 0:
            self.time_left -=1
            # Divide by 60 to get total minutes
            minutes = self.time_left// 60
            # Use modulus (remainder) to get seconds
            seconds = self.time_left % 60
            self.clock_format ="{0:02}:{1:02}".format(minutes, seconds)
            pygame.time.wait(1000)

        pygame.event.post(pygame.event.Event(pygame.USEREVENT))
        sys.exit()

    def draw_on(self, surface):
        text = self.font.render(self.clock_format, True,  (0, 0, 0))
        surface.blit(text, (surface.get_width()/21, surface.get_height()/9))


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


class Bomb(Drawable):
    def __init__(self, board, image_file, width=30, height=30):
        self.width = width
        self.height = height
        self.x = random.randrange(int(board.surface.get_width() * 0.25),
                                  int(board.surface.get_width() - self.width - board.surface.get_width() * 0.0484))
        self.y = random.randrange(int(board.surface.get_height() * 0.04),
                                  int(board.surface.get_height() - self.height - board.surface.get_height() * 0.032))

        super().__init__(width, height, self.x, self.y)
        self.load_image(image_file)

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


class Game:
    def __init__(self, width, height):
        pygame.init()
        self.background = Background(
            'images/background.png',  width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(width=20, height=20, x=width/2, y=height/2, name="Player 1")
        self.hero2 = Hero(width=20, height=20, x=width//3,
                          y=height//3, color=(255, 0, 0), name="Player 2")
        hearts1 = [Heart(width=width, height=height, live_type=True, player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=width, height=height, live_type=True, player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)
        self.timer = Timer(width, 80)
        self.tab = []
        self.bombs = []

    def run(self):

        threads = [
            th.Thread(target=self.timer.count_down),
            th.Thread(target=self.spawn_items),
            th.Thread(target=self.spawn_bombs),
        ]

        # Run in separate threads
        for thread in threads:
            thread.start()

        while not self.handle_events():
            self.bomb_colision()  # Sprawdzanie kolizji dla każdej bomby


            self.board.draw(
                self.background,
                self.hero1,
                self.hero2,
                self.timer,
                *self.tab,
                *self.bombs,
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
        if key_input[pygame.K_b]:
            self.hero1.remove_live()

        if key_input[pygame.K_a]:
            self.hero2.move(x=-1, y=0, board=self.board)
        if key_input[pygame.K_w]:
            self.hero2.move(x=0, y=-1, board=self.board)
        if key_input[pygame.K_d]:
            self.hero2.move(x=1, y=0, board=self.board)
        if key_input[pygame.K_s]:
            self.hero2.move(x=0, y=1, board=self.board)
        if key_input[pygame.K_n]:
            self.hero2.remove_live()

    #check colision between hero and bombs
    def bomb_colision(self):
        for bomb in self.bombs:
            if self.hero1.rect.colliderect(bomb.rect):
                self.hero1.remove_live()
                self.bombs.remove(bomb)
                del bomb
                break  # Dodajemy break, aby przerwać pętlę po znalezieniu kolizji

        for bomb in self.bombs:
            if self.hero2.rect.colliderect(bomb.rect):
                self.hero2.remove_live()
                self.bombs.remove(bomb)
                del bomb
                break  # Dodajemy break, aby przerwać pętlę po znalezieniu kolizji

    def spawn_items(self):
        while True:
            item = Item(self.board)
            self.tab.append(item)
            pygame.time.wait(10000)

    def spawn_bombs(self):
        while True:
            bomb = Bomb(self.board, image_file='images/bomb.png')
            self.bombs.append(bomb)
            pygame.time.wait(10000)


if __name__ == "__main__":
    game = Game(1200, 600)
    game.run()
