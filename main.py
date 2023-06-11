import math
import pygame
import pygame.locals
import threading as th
from concurrent.futures import ThreadPoolExecutor
import time
import random
import sys
from board import *
from drawable import *
from collisions import Collisions
from spawn import Spawn

# Create a lock object for synchronization
lock = th.Lock()

# Create a 2-dimensional list to represent cord_list
# with dimensions 16x20, initialized with zeros
cord_list = [[0 for i in range(20)] for j in range(16)]


class Game(Collisions, Spawn):
    def __init__(self, width, height, game_time):
        """
        Initialize the game object.

        Args:
            width: width of the game window
            height: height of the game window
            game_time: total game time in seconds
        """
        self.width = width
        self.height = height
        self.game_time = game_time
        self.board_elements = None

        # Initialize Pygame
        pygame.init()

        # Create background objects
        self.background_start = Background(
            'images/Start_screen.png', width, height)
        self.background = Background(
            'images/background.png', width, height)
        self.background2 = Background(
            'images/blank.png', width, height)

        # Create game board
        self.board = Board(width, height, background=self.background)

        # Create hero objects
        self.hero1 = Hero(self.board, image_file='images/hero1.png', width=30,
                          height=30, x=width - width * 0.0734, y=height * 0.04, name="Player 1")
        self.hero2 = Hero(self.board, image_file='images/hero2.png', width=30, height=30,
                          x=width * 0.25, y=height * 0.04,  name="Player 2")

        # Create heart objects for each player
        hearts1 = [Heart(width=width, height=height, live_type=True,
                         player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=width, height=height, live_type=True,
                         player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)

        # Create timer object
        self.timer = Timer(width, game_time)

        # Create empty lists for items, bombs, and cubes
        self.items = []
        self.bombs = []
        self.cubes = []

        # Create score objects for each player
        self.score1 = Score(width, height, 1)
        self.score2 = Score(width, height, 2)

        # Create profile objects for each player
        self.prof1 = Profile(width, height, 1)
        self.prof2 = Profile(width, height, 2)

        # Create profile power-up objects for each player
        self.profitems1 = ProfilePowerUps(width, height, 1, 0)
        self.profitems2 = ProfilePowerUps(width, height, 2, 0)

        # Create text objects for game events
        self.text_end = Text(width * 0.11, "Time's up!",
                             width * 0.1446, height * 0.168)
        self.text_end_live = Text(width * 0.11, "Player died",
                                  width * 0.1446, height * 0.168)
        self.text_points1 = Text(
            width * 0.055, " ", width * 0.1446, height * 0.507)
        self.text_points2 = Text(
            width * 0.055, " ", width * 0.1446, height * 0.6774)

        # Create button objects
        self.restart_button = Button(width, height, "images/restart.png")
        self.start_button = Button(width, height, "images/start.png")

    def start_screen(self):
        """
        Display the start screen with a button to start the game.
        """
        self.board.draw(self.background_start, self.start_button)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    # Quit the game
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
                    if self.start_button.rect.collidepoint(
                            pygame.mouse.get_pos()):  # Check if click occurred on the button
                        return

            pygame.display.flip()

    def reset_game(self):
        """
        Reset the game to its initial state.
        """
        self.__init__(self.width, self.height, self.game_time)

        # Reset cord_list
        global cord_list
        cord_list = [[0 for i in range(20)] for j in range(16)]

        # Prepare and run the game again
        game.run()

    def prepare(self):
        """
        Prepare the game by spawning cubes.
        """
        random_number = random.randint(300, 350)
        self.spawn_cubes(random_number, False)

    def run(self):
        """
        Run the game loop.
        """

        # Display the start screen
        self.start_screen()

        # Prepare game
        self.prepare()

        # Create threads for timer countdown, spawning items, and spawning cubes
        threads = [
            th.Thread(target=self.timer.count_down),
            th.Thread(target=self.spawn_items),
            th.Thread(target=self.spawn_cubes)
        ]

        # Run threads
        for thread in threads:
            thread.start()

        while not self.handle_events():
            # Perform collision checks
            self.bomb_collision()
            self.item_collision()

            # Define the board elements to be drawn
            self.board_elements = [
                self.background,
                self.hero1,
                self.hero2,
                self.timer,
                *self.items,
                *self.cubes,
                *self.bombs,
                self.score1,
                self.score2,
                self.prof1,
                self.prof2,
                self.profitems1,
                self.profitems2,
            ]

            # Draw the board and board elements
            self.board.draw(*self.board_elements)

        # Wait for threads to finish
        for thread in threads:
            thread.join()

        # Quit pygame
        pygame.quit()

    def handle_events(self):
        """
        Handle game events such as quitting, time's up, player death, and button clicks.

        Returns:
            True if the game should quit, False otherwise.
        """
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                # Quit the game
                pygame.quit()
                return True
            elif event.type == pygame.USEREVENT and (self.timer.time_left == 0 or self.hero1.lives == 0 or self.hero2.lives == 0):
                # Game over condition reached
                self.board_elements.clear()
                self.board_elements.append(self.background2)
                if self.timer.time_left == 0:
                    self.board_elements.append(self.text_end)
                elif self.hero1.lives == 0 or self.hero2.lives == 0:
                    self.board_elements.append(self.text_end_live)
                self.text_points1.text = f"{self.hero1.name} points: {self.score1.score}"
                self.text_points2.text = f"{self.hero2.name} points: {self.score2.score}"
                self.board_elements.extend(
                    [self.text_points1, self.text_points2, self.restart_button])
                self.board.draw(*self.board_elements)

                while True:
                    # Wait for reset button click
                    for event in pygame.event.get():
                        if event.type == pygame.locals.QUIT:
                            # Quit the game
                            pygame.quit()
                            exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
                            if self.restart_button.rect.collidepoint(
                                    pygame.mouse.get_pos()):  # Check if click occurred on the button
                                self.reset_game()
                                break
                    else:
                        continue  # If button not clicked, continue loop
                    break  # If reset button clicked, exit the loop

        # Key mappings for movement and actions
        key_mappings = {
            pygame.K_w: (0, -1, 0, 2),
            pygame.K_s: (0, 1, 0, 2),
            pygame.K_a: (-1, 0, 0, 2),
            pygame.K_d: (1, 0, 0, 2),
            pygame.K_UP: (0, -1, 0, 1),
            pygame.K_DOWN: (0, 1, 0, 1),
            pygame.K_LEFT: (-1, 0, 0, 1),
            pygame.K_RIGHT: (1, 0, 0, 1),
            pygame.K_RETURN: (0, 0, 1, 1),
            pygame.K_KP_ENTER: (0, 0, 1, 1),
            pygame.K_SPACE: (0, 0, 1, 2)
        }

        keys = pygame.key.get_pressed()

        for key, movement in key_mappings.items():
            if keys[key]:
                x, y, action, hero = movement
                x = x * 1.4
                y = y * 1.4
                hero_obj = self.hero1 if hero == 1 else self.hero2
                if action == 0:
                    # Move the hero and check for collisions
                    hero_obj.move(x, y, self.board)
                    if self.check_collision(hero_obj):
                        hero_obj.move(-x, -y, self.board)
                elif action == 1 and hero_obj.bomb == 1:
                    # Spawn bombs
                    hero_obj.bomb = 0
                    self.spawn_bombs(hero_obj.rect.x, hero_obj.rect.y, hero)

    def check_collision(self, hero):
        """
        Check collision between the hero and cubes.

        Args:
            hero (Hero): The hero object to check collision for.

        Returns:
            bool: True if collision occurs, False otherwise.
        """
        for cube in self.cubes:
            if hero.rect.colliderect(cube.rect):
                return True
        return False


if __name__ == "__main__":
    game = Game(1200, 600, 80)
    game.run()
