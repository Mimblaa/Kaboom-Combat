import pygame
import pygame.locals
from drawable import *
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


class Background:
    def __init__(self, image_file, width, height):
        self.image = pygame.image.load(image_file)
        self.width = width
        self.height = height

    def draw_on(self, surface):
        scaled_image = pygame.transform.scale(
            self.image, (self.width, self.height))
        surface.blit(scaled_image, (0, 0))
