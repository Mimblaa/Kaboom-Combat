import pygame
import pygame.locals
import random
import sys
import math
from main import *


class Drawable:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect(x=x, y=y)

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)


class Hero(Drawable):
    def __init__(self, board, image_file, width, height, x, y, lives=3, name="Player", shield=0, bomb=1):
        super().__init__(width, height, x, y)
        self.board = board
        self.lives = lives
        self.name = name
        self.hearts = []
        self.load_image(image_file)
        self.shield = shield
        self.bomb = bomb

    def load_image(self, image_file):
        self.image = pygame.transform.scale(pygame.image.load(image_file), (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def set_hearts(self, hearts):
        self.hearts = hearts
        self.update_hearts()

    def update_hearts(self):
        for i, heart in enumerate(self.hearts):
            heart.live_type = i < self.lives
            heart.update_image()

    def move(self, x, y, board):
        x = max(board.surface.get_width() * 0.25 - self.rect.x, min(x, board.surface.get_width() - self.width - board.surface.get_width() * 0.0484 - self.rect.x))
        y = max(board.surface.get_height() * 0.04 - self.rect.y, min(y, board.surface.get_height() - self.height - board.surface.get_height() * 0.032 - self.rect.y))
        self.rect.x += x
        self.rect.y += y

    def get_position_j(self):
        return math.floor((self.rect.x - self.board.surface.get_width() * 0.25) / (self.board.surface.get_width() * 0.7 / len(cord_list[0])))

    def get_position_i(self):
        return math.floor((self.rect.y - self.board.surface.get_height() * 0.04) / (self.board.surface.get_height() * 0.9265 / len(cord_list)))

    def remove_live(self):
        if self.shield == 0:
            if self.lives > 1:
                self.lives -= 1
            elif self.lives == 1:
                self.lives -= 1
                print(f"Player {self.name} is dead")
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))
            self.update_hearts()
        else:
            self.shield = 0

    def add_live(self):
        if self.lives < 3:
            self.lives += 1
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
        image_file = 'images/full_heart.png' if self.live_type else 'images/dead_heart.png'
        self.image = pygame.transform.scale(pygame.image.load(image_file), (int(self.width * 0.023), int(self.height * 0.035)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Reset:
    def __init__(self, width, height):
        self.image_path = 'images/restart.png'
        self.width = width
        self.height = height
        self.x_pos = width * 0.4
        self.y_pos = height * 0.81
        self.image = pygame.transform.scale(pygame.image.load(self.image_path), (int(self.width * 0.2), int(self.height * 0.118)))
        self.rect = self.image.get_rect(x=self.x_pos, y=self.y_pos)

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Delete:
    def __init__(self, width, height, i=0, j=0):
        self.image_path = 'images/delete_mark.png'
        self.width = width
        self.height = height
        rows = len(cord_list)
        columns = len(cord_list[0])
        x = math.floor((width * 0.7) / rows)
        y = math.floor((height * 0.9265) / columns)
        self.x_pos = math.ceil((width * 0.25) + math.ceil((width * 0.7 / columns) * j))
        self.y_pos = math.ceil((height * 0.04) + math.ceil((height * 0.9265 / rows) * i))
        self.image = pygame.transform.scale(pygame.image.load(self.image_path), (x, y))
        self.rect = self.image.get_rect(x=self.x_pos, y=self.y_pos)

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Item(Drawable):
    def __init__(self, board, item_type, width=30, height=30, i=0, j=0):
        self.image = None
        self.i = i
        self.j = j
        rows = len(cord_list)
        columns = len(cord_list[0])
        x = math.ceil((board.surface.get_width() * 0.25) + math.ceil((board.surface.get_width() * 0.7 / columns) * j))
        y = math.ceil((board.surface.get_height() * 0.04) + math.ceil((board.surface.get_height() * 0.9265 / rows) * i))
        super().__init__(width, height, x, y)
        self.item_type = item_type
        image_file = {
            0: 'images/gold_heart.png',
            1: 'images/shield.png',
            2: 'images/extra_bomb.png',
        }
        self.load_image(image_file.get(item_type))

    def load_image(self, image_file):
        self.image = pygame.transform.scale(pygame.image.load(image_file), (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


class Timer:
    def __init__(self, width, game_time=10):
        self.time_left = game_time
        self.font = pygame.font.SysFont('monospace', int(width * 0.045))

    def count_down(self):
        while self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.clock_format = f"{minutes:02}:{seconds:02}"
            pygame.time.wait(1000)

        pygame.event.post(pygame.event.Event(pygame.USEREVENT))

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
        self.delete_marks = []

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def bomb_delay(self):
        if self.timer > 0:
            self.timer -= 1

    def set_marks(self, delete_marks):
        self.delete_marks = delete_marks


class Cube(Drawable):
    def __init__(self, x, y, width=50, height=50, i=0, j=0):
        super().__init__(width, height, x, y)
        self.image = None
        paths = ['images/cheese_brick.png', 'images/dirt_brick.png',
                 'images/sweet_brick.png', 'images/ice_cube.png']
        image_file = random.choice(paths)
        self.load_image(image_file)
        self.i = i
        self.j = j

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


class Profile(Drawable):
    def __init__(self, width, height, player):
        super().__init__(width, height, width * 0.0756, height * 0.394 + (player - 1) * height * 0.308)
        self.x_pos = width * 0.0756
        self.y_pos = height * 0.394 + (player - 1) * height * 0.308
        self.player = player
        self.update_image()

    def update_image(self):
        image_file = 'images/hero{}.png'.format(self.player)
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.06674), int(self.height * 0.1129)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class ProfilePowerUps(Drawable):
    def __init__(self, width, height, player, power_up):
        super().__init__(width, height, width * 0.1546, height * 0.396 + (player - 1) * height * 0.308)
        self.player = player
        self.power_up = power_up
        self.x_pos = width * 0.1546
        self.y_pos = height * 0.396 + (player - 1) * height * 0.308
        self.update_image()

    def update_image(self):
        image_file = 'images/shield.png' if self.power_up == 1 else 'images/blank.png'
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.0278), int(self.height * 0.0448)))
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def add_shield(self):
        self.power_up = 1
        self.update_image()

    def remove_shield(self):
        self.power_up = 0
        self.update_image()

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)


class Score:
    def __init__(self, width, height, player):
        self.score = 0
        self.font = pygame.font.SysFont('monospace', int(width * 0.02))
        self.position = (width * 0.045, height * 0.5197 + (player - 1) * height * 0.307)

    def draw_on(self, surface):
        text = self.font.render(str(self.score), True, (0, 0, 0))
        surface.blit(text, self.position)
