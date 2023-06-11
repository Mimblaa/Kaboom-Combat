import pygame
import pygame.locals
from main import *
import math


class Heart:
    def __init__(self, width, height, live_type, number, player):
        """
        Initialize a heart object.

        Args:
            width: width of the heart
            height: height of the heart
            live_type: indicates whether the heart represents a live (True) or is empty (False)
            number: position of the heart in relation to other hearts
            player: player number (1 or 2)
        """
        self.image = None
        self.rect = None
        self.width = width
        self.height = height
        self.x_pos = width * 0.09 + (number - 1) * width * 0.029
        self.y_pos = height * 0.52 + (player - 1) * height * 0.308
        self.live_type = live_type
        self.update_image()

    def update_image(self):
        """
        Update the image of the heart based on its live type.
        """
        image_file = 'images/full_heart.png' if self.live_type else 'images/dead_heart.png'
        self.image = pygame.transform.scale(pygame.image.load(image_file),
                                            (int(self.width * 0.023), int(self.height * 0.035)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        """
        Draw the heart on the specified surface.

        Args:
            surface: surface to draw the heart on
        """
        surface.blit(self.image, self.rect)


class Button:
    def __init__(self, width, height, image):
        """
        Initialize a button object.

        Args:
        - width: width of the game board
        - height: height of the game board
        """
        self.image_path = image
        self.width = width
        self.height = height
        self.x_pos = width * 0.4
        self.y_pos = height * 0.81
        self.image = pygame.transform.scale(pygame.image.load(self.image_path),
                                            (int(self.width * 0.2), int(self.height * 0.118)))
        self.rect = self.image.get_rect(x=self.x_pos, y=self.y_pos)

    def draw_on(self, surface):
        """
        Draw button on the specified surface.

        Args:
            surface: surface to draw button on
        """
        surface.blit(self.image, self.rect)


class Delete:
    def __init__(self, width, height, i=0, j=0):
        """
        Initialize a delete mark object.

        Args:
            width: width of the game board
            height: height of the game board
            i: row index of the delete mark (default: 0)
            j: column index of the delete mark (default: 0)
        """
        self.image_path = 'images/delete_mark.png'
        self.width = width
        self.height = height
        rows = len(cord_list)
        columns = len(cord_list[0])
        x = math.floor((width * 0.7) / rows)
        y = math.floor((height * 0.9265) / columns)
        self.x_pos = math.ceil(
            (width * 0.25) + math.ceil((width * 0.7 / columns) * j))
        self.y_pos = math.ceil(
            (height * 0.04) + math.ceil((height * 0.9265 / rows) * i))
        self.image = pygame.transform.scale(
            pygame.image.load(self.image_path), (x, y))
        self.rect = self.image.get_rect(x=self.x_pos, y=self.y_pos)

    def draw_on(self, surface):
        """
        Draw the delete mark on the specified surface.

        Args:
            surface: surface to draw the delete mark on
        """
        surface.blit(self.image, self.rect)


class Timer:
    def __init__(self, width, game_time=10):
        """
        Initialize a timer object.

        Args:
            width: width of the game board
            game_time: total game time in seconds (default: 10)
        """
        self.clock_format = None
        self.time_left = game_time
        self.font = pygame.font.SysFont('monospace', int(width * 0.045))

    def count_down(self):
        """
        Count down the time until it reaches 0.
        """
        while self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.clock_format = f"{minutes:02}:{seconds:02}"
            pygame.time.wait(1000)

        pygame.event.post(pygame.event.Event(pygame.USEREVENT))

    def draw_on(self, surface):
        """
        Draw the timer on the specified surface.

        Args:
            surface: surface to draw the timer on
        """
        text = self.font.render(self.clock_format, True, (0, 0, 0))
        surface.blit(text, (surface.get_width() /
                     21, surface.get_height() / 9))


class Text:
    def __init__(self, width, text, x, y):
        """
        Initialize a text object.

        Args:
            width: font width
            text: the text to display
            x: x-coordinate of the text
            y: y-coordinate of the text
        """
        self.font = pygame.font.SysFont('monospace', int(width))
        self.text = text
        self.x = x
        self.y = y

    def draw_on(self, surface):
        """
        Draw the text on the specified surface.

        Args:
            surface: surface to draw the text on
        """
        text = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text, (self.x, self.y))
