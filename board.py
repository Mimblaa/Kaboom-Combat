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
        self.surface.blit(self.background.image, (0, 0))

        for arg in args:
            if isinstance(arg, pygame.sprite.Group) or isinstance(arg, Hero):
                arg.draw_on(self.surface)
                if isinstance(arg, Hero):
                    for heart in arg.hearts:
                        heart.draw_on(self.surface)
            elif not isinstance(arg, tuple):
                arg.draw_on(self.surface)

        pygame.display.update()


class Background:
    def __init__(self, image_file, width, height):
        self.image = pygame.transform.scale(pygame.image.load(image_file), (width, height))

    def draw_on(self, surface):
        surface.blit(self.image, (0, 0))


