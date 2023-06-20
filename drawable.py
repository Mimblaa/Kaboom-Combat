import pygame
import pygame.locals
import random
import sys
import math
from main import *


class Drawable:
    def __init__(self, width, height, x, y):
        """
        Initialize a drawable object.

        Args:
            width: width of the object
            height: height of the object
            x: x-coordinate of the object's position
            y: y-coordinate of the object's position
        """
        self.width = width
        self.height = height
        self.surface = pygame.Surface(
            (width, height), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect(x=x, y=y)

    def draw_on(self, surface):
        """
        Draw the object on the specified surface.

        Args:
            surface: surface to draw the object on
        """
        surface.blit(self.surface, self.rect)


class Hero(Drawable):
    def __init__(self, board, image_file, width, height, x, y, lives=3, name="Player", shield=0, bomb=1):
        """
        Initialize a hero object.

        Args:
            board: reference to the game board
            image_file: path to the image file for the hero
            width: width of the hero
            height: height of the hero
            x: x-coordinate of the hero's position
            y: y-coordinate of the hero's position
            lives: number of lives the hero starts with (default: 3)
            name: name of the hero (default: "Player")
            shield: shield level of the hero (default: 0)
            bomb: number of bombs the hero has (default: 1)
        """
        super().__init__(width, height, x, y)
        self.image = None
        self.board = board
        self.lives = lives
        self.name = name
        self.hearts = []
        self.load_image(image_file)
        self.shield = shield
        self.bomb = bomb

    def load_image(self, image_file):
        """
        Load the image for the hero and draw it on the surface.

        Args:
            image_file: path to the image file for the hero
        """
        self.image = pygame.transform.scale(
            pygame.image.load(image_file), (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def set_hearts(self, hearts):
        """
        Set the hearts representing the hero's health.

        Args:
            hearts: list of heart objects representing the hero's health
        """
        self.hearts = hearts
        self.update_hearts()

    def update_hearts(self):
        """
        Update the state of the hearts based on the hero's remaining lives.
        """
        for i, heart in enumerate(self.hearts):
            heart.live_type = i < self.lives
            heart.update_image()

    def move(self, x, y, board):
        """
        Move the hero by a given amount in the x and y directions.

        Args:
            x: amount to move in the x direction
            y: amount to move in the y direction
            board: reference to the game board
        """
        x = max(board.surface.get_width() * 0.25 - self.rect.x,
                min(x, board.surface.get_width() - self.width - board.surface.get_width() * 0.0484 - self.rect.x))
        y = max(board.surface.get_height() * 0.04 - self.rect.y,
                min(y, board.surface.get_height() - self.height - board.surface.get_height() * 0.032 - self.rect.y))
        self.rect.x += x
        self.rect.y += y

    def get_position_j(self):
        """
        Get the column index of the hero's position on the game board grid.

        Returns:
            int: The column index.
        """
        return math.floor((self.rect.x - self.board.surface.get_width() * 0.25) / (
            self.board.surface.get_width() * 0.7 / len(cord_list[0])))

    def get_position_i(self):
        """
        Get the row index of the hero's position on the game board grid.

        Returns:
            int: The row index.
        """
        return math.floor((self.rect.y - self.board.surface.get_height() * 0.04) / (
            self.board.surface.get_height() * 0.9265 / len(cord_list)))

    def remove_live(self):
        """
        Remove a life from the hero.
        """
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
        """
        Add a life to the hero.
        """
        if self.lives < 3:
            self.lives += 1
            self.update_hearts()


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
    def __init__(self, width, height, button_height, image):
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
        self.y_pos = button_height
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
        x = math.floor((width * 0.65) / rows)
        y = math.floor((height * 0.91) / columns)
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


class Item(Drawable):
    def __init__(self, board, item_type, width=30, height=30, i=0, j=0):
        """
        Initialize an item object.

        Args:
            board: the game board object
            item_type: type of the item (0: gold heart, 1: shield)
            width: width of the item (default: 30)
            height: height of the item (default: 30)
            i: row index of the item (default: 0)
            j: column index of the item (default: 0)
        """
        self.image = None
        self.i = i
        self.j = j
        rows = len(cord_list)
        columns = len(cord_list[0])
        x = math.ceil((board.surface.get_width() * 0.25) +
                      math.ceil((board.surface.get_width() * 0.7 / columns) * j))
        y = math.ceil((board.surface.get_height() * 0.04) +
                      math.ceil((board.surface.get_height() * 0.9265 / rows) * i))
        super().__init__(width, height, x, y)
        self.item_type = item_type
        image_file = {
            0: 'images/gold_heart.png',
            1: 'images/shield.png',
        }
        self.load_image(image_file.get(item_type))

    def load_image(self, image_file):
        """
        Load and set the image of the item.

        Args:
            image_file: file path of the image
        """
        self.image = pygame.transform.scale(
            pygame.image.load(image_file), (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


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


class TextField:
    def __init__(self, rect, width,color):
        """
        Initialize a TextField object.

        Args:
            rect (tuple): The position and size of the text field (x, y, width, height).
            width (int): The width of the game window.

        Attributes:
            rect (pygame.Rect): The rectangle representing the position and size of the text field.
            color (pygame.Color): The color of the text.
            text (str): The current text in the text field.
            font (pygame.font.Font): The font used for rendering the text.
            active (bool): Indicates whether the text field is currently active (editable).
        """
        self.rect = pygame.Rect(rect)
        self.color = pygame.Color(color)
        self.text = ''
        self.font = pygame.font.Font(None, int(width * 0.034))
        self.active = False

    def handle_event(self, event):
        """
        Handle events for the text field.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if the mouse click occurred within the text field
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # End editing when the Enter key is pressed
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                # Remove the last character when the Backspace key is pressed
                self.text = self.text[:-1]
            else:
                # Add the entered character to the text
                self.text += event.unicode

    def draw_on(self, surface):
        """
        Draw the text field on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        # Render the text
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))


class Bomb(Drawable):
    def __init__(self, board, image_file, player, i, j, timer=250, width=30, height=30):
        """
        Initialize a bomb object.

        Args:
            board: the game board
            image_file: path to the bomb image file
            player: the player who owns the bomb
            i: row index of the bomb's position
            j: column index of the bomb's position
            timer: countdown timer for the bomb (default: 250)
            width: width of the bomb image (default: 30)
            height: height of the bomb image (default: 30)
        """
        self.image = None
        self.width = width
        self.height = height
        rows = len(cord_list)
        columns = len(cord_list[0])
        self.x = math.ceil(
            (board.surface.get_width() * 0.25) + math.ceil((board.surface.get_width() * 0.7 / columns) * j))
        self.y = math.ceil(
            (board.surface.get_height() * 0.04) + math.ceil((board.surface.get_height() * 0.9265 / rows) * i))
        super().__init__(width, height, self.x, self.y)
        self.load_image(image_file)
        self.timer = timer
        self.player = player
        self.i = i
        self.j = j
        self.delete_marks = []

    def load_image(self, image_file):
        """
        Load the bomb image and scale it to the specified width and height.

        Args:
            image_file: path to the bomb image file
        """
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))

    def bomb_delay(self):
        """
        Decrease the timer value of the bomb by 1.
        """
        if self.timer > 0:
            self.timer -= 1

    def set_marks(self, delete_marks):
        """
        Set the delete marks for the bomb.

        Args:
            delete_marks: list of delete marks associated with the bomb
        """
        self.delete_marks = delete_marks


class Cube(Drawable):
    def __init__(self, x, y, width=50, height=50, i=0, j=0):
        """
        Initialize a cube object.

        Args:
            x: x-coordinate of the cube
            y: y-coordinate of the cube
            width: width of the cube (default: 50)
            height: height of the cube (default: 50)
            i: row index of the cube's position
            j: column index of the cube's position
        """
        super().__init__(width, height, x, y)
        self.image = None
        paths = ['images/cheese_brick.png', 'images/dirt_brick.png',
                 'images/sweet_brick.png', 'images/ice_cube.png']
        image_file = random.choice(paths)
        self.load_image(image_file)
        self.i = i
        self.j = j

    def load_image(self, image_file):
        """
        Load the cube image and scale it to the specified width and height.

        Args:
            image_file: path to the cube image file
        """
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.surface.blit(self.image, (0, 0))


class Profile(Drawable):
    def __init__(self, width, height, player):
        """
        Initialize a profile object.

        Args:
            width: width of the profile object
            height: height of the profile object
            player: player identifier
        """
        super().__init__(width, height, width * 0.0756,
                         height * 0.394 + (player - 1) * height * 0.308)
        self.image = None
        self.x_pos = width * 0.0756
        self.y_pos = height * 0.394 + (player - 1) * height * 0.308
        self.player = player
        self.update_image()

    def update_image(self):
        """
        Update the profile image based on the player identifier.
        """
        image_file = 'images/hero{}.png'.format(self.player)
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.06674), int(self.height * 0.1129)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def draw_on(self, surface):
        """
        Draw the profile image on the given surface.

        Args:
            surface: surface to draw on
        """
        surface.blit(self.image, self.rect)


class ProfilePowerUps(Drawable):
    def __init__(self, width, height, player, power_up):
        """
        Initialize a profile power-up object.

        Args:
            width: width of the profile power-up object
            height: height of the profile power-up object
            player: player identifier
            power_up: power-up type (1 for shield, 0 for blank)
        """
        super().__init__(width, height, width * 0.1546,
                         height * 0.396 + (player - 1) * height * 0.308)
        self.image = None
        self.player = player
        self.power_up = power_up
        self.x_pos = width * 0.1546
        self.y_pos = height * 0.396 + (player - 1) * height * 0.308
        self.update_image()

    def update_image(self):
        """
        Update the power-up image based on the power-up type.
        """
        image_file = 'images/shield.png' if self.power_up == 1 else 'images/blank.png'
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(
            self.image, (int(self.width * 0.0278), int(self.height * 0.0448)))
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def add_shield(self):
        """
        Set the power-up to shield and update the image.
        """
        self.power_up = 1
        self.update_image()

    def remove_shield(self):
        """
        Remove the shield power-up and update the image.
        """
        self.power_up = 0
        self.update_image()

    def draw_on(self, surface):
        """
        Draw the power-up image on the given surface.

        Args:
            surface: surface to draw on
        """
        surface.blit(self.image, self.rect)


class Score:
    def __init__(self, width, height, player):
        """
        Initialize a score object.

        Args:
            width: width of the score object
            height: height of the score object
            player: player identifier
        """
        self.score = 0
        self.font = pygame.font.SysFont('monospace', int(width * 0.02))
        self.position = (width * 0.045, height * 0.5197 +
                         (player - 1) * height * 0.307)

    def draw_on(self, surface):
        """
        Draw the score on the given surface.

        Args:
            surface: surface to draw on
        """
        text = self.font.render(str(self.score), True, (0, 0, 0))
        surface.blit(text, self.position)
