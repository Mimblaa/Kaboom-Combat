import pygame
import pygame.locals
import random
import sys
import math
from main import *


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
    def __init__(self, board,image_file, width, height, x, y, color=(0, 255, 0), lives=3, name="Player", shield=0, bomb=1):
        super().__init__(width, height, x, y, color)
        self.image = None
        self.width = width
        self.height = height
        self.lives = lives
        self.name = name
        self.hearts = []
        self.load_image(image_file)
        self.shield = shield
        self.bomb = bomb
        self.board=board

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

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

        if self.rect.x + x <= board.surface.get_width() * 0.25 or \
                self.rect.x + x >= board.surface.get_width() - self.width - board.surface.get_width() * 0.0484:
            x = 0

        if self.rect.y + y <= board.surface.get_height() * 0.04 or \
                self.rect.y + y >= board.surface.get_height() - self.height - board.surface.get_height() * 0.032:
            y = 0

        self.rect.x += x
        self.rect.y += y

    def get_position_j(self):
        i = math.floor((
            (self.rect.x - self.board.surface.get_width() * 0.25) / (
                    (self.board.surface.get_width() * 0.7) / len(cord_list[0]))))
        return i

    def get_position_i(self):
        j = math.floor(((self.rect.y - self.board.surface.get_height() * 0.04)/ (
                (self.board.surface.get_height() * 0.9265) / len(cord_list))))
        return j


    def activate_shield(self):
        self.shield = 1

    def deactivate_shield(self):
        self.shield = 0

    def remove_live(self):
        if self.shield == 0:
            if self.lives > 1:
                self.lives -= 1
            elif self.lives == 1:
                self.lives -= 1
                print("Player " + self.name + " is dead")
            self.update_hearts()
        else:
            self.deactivate_shield()

    def add_live(self):
        if self.lives < 3:
            self.lives += 1
            self.update_hearts()


class Heart:
    def __init__(self, width, height, live_type, number, player):
        self.image = None
        self.rect = None
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


class Item(Drawable):
    def __init__(self, board, item_type, width=30, height=30, i=0, j=0):
        self.image = None
        self.width = width
        self.height = height
        self.i = i
        self.j = j
        rows = len(cord_list)
        columns = len(cord_list[0])
        self.item_type = item_type
        self.x = math.ceil((board.surface.get_width() * 0.25) +
                           math.ceil((board.surface.get_width() * 0.7 / columns) * j))
        self.y = math.ceil(
            (board.surface.get_height() * 0.04) + math.ceil((board.surface.get_height() * 0.9265 / rows) * i))
        super().__init__(width, height, self.x, self.y)
        image_file = {
            0: 'images/gold_heart.png',
            1: 'images/shield.png',
            2: 'images/extra_bomb.png',
        }
        self.load_image(image_file.get(item_type))

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def get_type(self):
        return self.item_type


class Timer:
    def __init__(self, width, game_time=10):
        self.clock = pygame.time.Clock()
        self.time_left = game_time
        self.clock_format = ""
        # calculate font size based on screen width
        self.font = pygame.font.SysFont('monospace', int(width * 0.045))

    def count_down(self):
        while self.time_left > 0:
            self.time_left -= 1
            # Divide by 60 to get total minutes
            minutes = self.time_left // 60
            # Use modulus (remainder) to get seconds
            seconds = self.time_left % 60
            self.clock_format = "{0:02}:{1:02}".format(minutes, seconds)
            pygame.time.wait(1000)

        pygame.event.post(pygame.event.Event(pygame.USEREVENT))
        sys.exit()

    def draw_on(self, surface):
        text = self.font.render(self.clock_format, True, (0, 0, 0))
        surface.blit(text, (surface.get_width() / 21, surface.get_height() / 9))


class Text:
    def __init__(self, width,text, x, y):
        self.font = pygame.font.SysFont('monospace', int(width))
        self.text = text
        self.x = x
        self.y = y

    def draw_on(self,surface):
        text = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text, (self.x, self.y))


class Bomb(Drawable):
    def __init__(self, image_file, player, i, j, timer=250, width=30, height=30, x=0, y=0):
        self.image = None
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        super().__init__(width, height, self.x, self.y)
        self.load_image(image_file)
        self.timer = timer
        self.player = player
        self.i = i
        self.j = j

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def bomb_delay(self):
        if self.timer > 0:
            self.timer -= 1


class Cube(Drawable):
    def __init__(self, x, y, width=50, height=50, color=(255, 255, 0),i=0,j=0):
        super().__init__(width, height, x, y, color)
        self.image = None
        paths = ['images/cheese_brick.png', 'images/dirt_brick.png',
                 'images/sweet_brick.png', 'images/ice_cube.png']
        image_file = paths[random.randrange(len(paths))]
        self.load_image(image_file)
        self.i=i
        self.j=j

    def check_collision(self, rect):
        return self.rect.colliderect(rect)

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


class Profile(Drawable):
    def __init__(self, width, height, player):
        self.image = None
        self.width = width
        self.height = height
        self.x_pos = width * 0.0756
        self.y_pos = height * 0.394 + (player - 1) * height * 0.308
        self.player = player

        self.update_image()

    def update_image(self):
        if self.player == 1:
            image_file = 'images/hero1.png'
        else:
            image_file = 'images/hero2.png'

        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.06674), int(self.height * 0.1129)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Profile_power_ups(Drawable):
    def __init__(self, width, height, player, power_up):
        self.image = None
        self.width = width
        self.height = height
        self.x_pos = width * 0.1546
        self.y_pos = height * 0.396 + (player - 1) * height * 0.308
        self.player = player
        self.power_up = power_up

        self.update_image()

    def update_image(self):
        if self.power_up == 1:
            image_file = 'images/shield.png'
        else:
            image_file = 'images/blank.png'

        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.0278), int(self.height * 0.0448)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)

    def add_shield(self):
        self.power_up = 1
        self.update_image()

    def remove_shield(self):
        self.power_up = 0
        self.update_image()


class Score:
    def __init__(self, width, height, player):
        self.score = 0
        self.font = pygame.font.SysFont('monospace', int(width * 0.02))
        self.x_pos = width * 0.045
        self.y_pos = height * 0.5197 + (player - 1) * height * 0.307

    def increase_score(self, points):
        self.score += points

    def reset_score(self):
        self.score = 0

    def draw_on(self, surface):
        text = self.font.render(str(self.score), True, (0, 0, 0))
        surface.blit(text, (self.x_pos, self.y_pos))
