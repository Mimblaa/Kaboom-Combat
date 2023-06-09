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

# Create a lock object for synchronization
lock = th.Lock()

# Create a 2-dimensional list to represent cord_list
# with dimensions 16x20, initialized with zeros
cord_list = [[0 for i in range(20)] for j in range(16)]

# Set the values of specific elements in cord_list
cord_list[0][0] = 1  # Set the value at index (0, 0) to 1
cord_list[0][19] = 1  # Set the value at index (0, 19) to 1

# Create a semaphore object with an initial value of 10
semaphore = th.Semaphore(10)


class Game:
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
        self.text_points1 = Text(width * 0.055, " ", width * 0.1446, height * 0.507)
        self.text_points2 = Text(width * 0.055, " ", width * 0.1446, height * 0.6774)

        # Create restart button object
        self.restart_button = Reset(width, height)

    def reset_game(self):
        """
        Reset the game to its initial state.
        """
        self.__init__(self.width,self.height,self.game_time)

        # Reset cord_list
        global cord_list
        cord_list = [[0 for i in range(20)] for j in range(16)]
        cord_list[0][0] = 1
        cord_list[0][19] = 1

        # Prepare and run the game again
        game.prepare()
        game.run()

    def prepare(self):
        """
        Prepare the game by spawning cubes.
        """
        random_number = random.randint(200, 250)
        self.spawn_cubes(random_number, False)

    def run(self):
        """
        Run the game loop.
        """

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
                self.board_elements.extend([self.text_points1, self.text_points2, self.restart_button])
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

    def bomb_collision(self):
        """
        Handle bomb collisions with heroes, cubes, and countdown timers.
        """
        for bomb in self.bombs:
            if bomb.timer == 50:
                delete_marks = []
                for x, y in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if (bomb.i + x) >= 0 and (bomb.j + y) >= 0:
                        delete_marks.append(Delete(self.width, self.height, i=bomb.i + x, j=bomb.j + y))
                        bomb.set_marks(delete_marks)
            if bomb.timer == 0:
                bomb_position_hero1 = (self.hero1.get_position_i(), self.hero1.get_position_j())
                bomb_position_hero2 = (self.hero2.get_position_i(), self.hero2.get_position_j())

                # Check collision with hero1
                if (bomb.i, bomb.j) == bomb_position_hero1 or \
                        abs(bomb.i - bomb_position_hero1[0]) + abs(bomb.j - bomb_position_hero1[1]) == 1:
                    if self.hero1.shield == 0:
                        self.hero1.remove_live()
                        lock.acquire()
                        cord_list[bomb.i][bomb.j] = 0
                        lock.release()
                        self.score2.score += 10
                    else:
                        self.hero1.shield = 0
                        self.profitems1.remove_shield()

                # Check collision with hero2
                elif (bomb.i, bomb.j) == bomb_position_hero2 or \
                        abs(bomb.i - bomb_position_hero2[0]) + abs(bomb.j - bomb_position_hero2[1]) == 1:
                    if self.hero2.shield == 0:
                        self.hero2.remove_live()
                        lock.acquire()
                        cord_list[bomb.i][bomb.j] = 0
                        lock.release()
                        self.score1.score += 10
                    else:
                        self.hero2.shield = 0
                        self.profitems2.remove_shield()

                # Check collision with cubes
                adjacent_positions = [(bomb.i + 1, bomb.j), (bomb.i - 1, bomb.j), (bomb.i, bomb.j + 1),
                                      (bomb.i, bomb.j - 1)]
                for cube in self.cubes:
                    for position in adjacent_positions:
                        if (cube.i, cube.j) == position:
                            self.cubes.remove(cube)
                            lock.acquire()
                            cord_list[cube.i][cube.j] = 0
                            lock.release()
                            break

                self.hero1.bomb = 1 if bomb.player == 1 else 2
                self.hero2.bomb = 1 if bomb.player == 2 else 1
                self.bombs.remove(bomb)  # Remove bomb after checking collisions

        # Remove bombs with timers greater than 0
        self.bombs = [bomb for bomb in self.bombs if bomb.timer > 0]

        # Update bomb timers
        for bomb in self.bombs:
            bomb.bomb_delay()

    def item_collision(self):
        """
        Handle collisions between heroes and items.
        """
        for item in self.items:
            if self.hero1.rect.colliderect(item.rect):
                self.process_item_collision(item, self.hero1, self.profitems1)
                break

        for item in self.items:
            if self.hero2.rect.colliderect(item.rect):
                self.process_item_collision(item, self.hero2, self.profitems2)
                break

    def process_item_collision(self, item, hero, profitems):
        """
        Process the collision between a hero and an item.

        Args:
            item (Item): The item that was collided with.
            hero (Hero): The hero that collided with the item.
            profitems (ProfilePowerUps): The power-up profile associated with the hero.
        """
        self.items.remove(item)
        if item.item_type == 0:  # heart item
            hero.add_live()
        if item.item_type == 1:  # shield item
            hero.shield = 1
            profitems.add_shield()
        cord_list[item.i][item.j] = 0
        del item

    def spawn_items(self):
        """
        Spawn items at random positions on the game board.
        """
        global cord_list

        while True:
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0]))

            lock.acquire()

            # Check if the selected position is available
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1

                # Calculate the width and height of the item based on the board size
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor(
                    (self.board.surface.get_height() * 0.9265) / 16)

                # Create a new item and add it to the list
                item = Item(self.board, item_type=random.randrange(
                    2), width=width, height=height, i=i, j=j)
                self.items.append(item)

            lock.release()
            pygame.time.wait(5000)

    def spawn_bombs(self, x, y, player):
        """
        Spawn bombs at the specified position on the game board.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.
            player (int): The player number.
        """
        global cord_list

        # Map the position to the corresponding indices in cord_list
        j = math.floor(
            (x - self.board.surface.get_width() * 0.25) / (
                    (self.board.surface.get_width() * 0.7) / len(cord_list[0])))
        i = math.floor((y - self.board.surface.get_height() * 0.04) / (
                (self.board.surface.get_height() * 0.9265) / len(cord_list)))

        lock.acquire()

        # Check if the selected position is available
        if cord_list[i][j] == 0:
            cord_list[i][j] = 1

            # Calculate the width and height of the bomb based on the board size
            width = math.floor((self.board.surface.get_width() * 0.7) / 20)
            height = math.floor(
                (self.board.surface.get_height() * 0.9265) / 16)

            # Create a new bomb and add it to the list
            bomb = Bomb(self.board,image_file='images/bomb.png',
                       width=width, height=height, player=player, i=i, j=j)
            self.bombs.append(bomb)
        else:
            if player == 1:
                self.hero1.bomb = 1
            elif player == 2:
                self.hero2.bomb = 1

        lock.release()

    def spawn_cubes(self, iteration=1000000000000, wait=True):
        """
        Spawn cubes on the game board.

        Args:
            iteration (int, optional): The number of iterations to spawn cubes. Defaults to 1000000000000.
            wait (bool, optional): Whether to wait between spawning cubes. Defaults to True.
        """
        rows = len(cord_list)
        columns = len(cord_list[0])

        for _ in range(iteration):
            i = random.randrange(rows)
            j = random.randrange(columns)

            lock.acquire()

            # Check if the selected position is available
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1

                # Calculate the position, width, and height of the cube based on the board size
                x = math.ceil(
                    (self.board.surface.get_width() * 0.25) + math.ceil(
                        (self.board.surface.get_width() * 0.7 / columns) * j))
                y = math.ceil((self.board.surface.get_height() * 0.04) + math.ceil(
                    (self.board.surface.get_height() * 0.9265 / rows) * i))
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor(
                    (self.board.surface.get_height() * 0.9265) / 16)

                # Create a new cube and add it to the list
                cube = Cube(x, y, width, height, i=i, j=j)
                self.cubes.append(cube)

            lock.release()
            pygame.time.wait(5000) if wait else None

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
    game.prepare()
    game.run()
