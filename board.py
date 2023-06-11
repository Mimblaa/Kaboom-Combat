import pygame
import pygame.locals
from drawable import *
import sys


class Board:
    def __init__(self, width, height, background=None):
        """
        Initialize the game board.

        Args:
            width: width of the board in pixels
            height: height of the board in pixels
            background: background object for the board (optional)
        """
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption('Kaboom Combat')
        self.background = background

    def draw(self, *args):
        """
        Method to draw the board and objects on it.

        Args:
            *args: positional arguments representing the objects to be drawn
        """
        self.surface.blit(self.background.image, (0, 0))

        for arg in args:
            if isinstance(arg, pygame.sprite.Group) or isinstance(arg, Hero) or isinstance(arg, Bomb):
                # If the object is a sprite group, hero, or bomb, draw it on the board
                arg.draw_on(self.surface)
                if isinstance(arg, Hero):
                    # If the object is a hero, draw hearts representing the health points
                    for heart in arg.hearts:
                        heart.draw_on(self.surface)
                if isinstance(arg, Bomb):
                    # If the object is a bomb, draw marks indicating the places that will be destroyed
                    for mark in arg.delete_marks:
                        mark.draw_on(self.surface)
            elif not isinstance(arg, tuple):
                # If the object is not a tuple, draw it on the board
                arg.draw_on(self.surface)

        pygame.display.update()


class Background:
    def __init__(self, image_file, width, height):
        """
        Initialize the background object.

        Args:
            image_file: path to the image file for the background
            width: width of the background in pixels
            height: height of the background in pixels
        """
        self.image = pygame.transform.scale(pygame.image.load(image_file), (width, height))

    def draw_on(self, surface):
        """
        Method to draw the background on the specified surface.

        Args:
            surface: surface to draw the background on
        """
        surface.blit(self.image, (0, 0))
