import math
import main
import drawable as dr
import random
import pygame


class Spawn:
    def spawn_bombs(self, x, y, player):
        """
        Spawn bombs at the specified position on the game board.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.
            player (int): The player number.
        """

        # Map the position to the corresponding indices in cord_list
        j = math.floor(
            (x - self.board.surface.get_width() * 0.25) / (
                    (self.board.surface.get_width() * 0.7) / len(main.cord_list[0])))
        i = math.floor((y - self.board.surface.get_height() * 0.04) / (
                (self.board.surface.get_height() * 0.9265) / len(main.cord_list)))

        main.lock.acquire()

        # Check if the selected position is available
        if main.cord_list[i][j] == 0:
            main.cord_list[i][j] = 1

            # Calculate the width and height of the bomb based on the board size
            width = math.floor((self.board.surface.get_width() * 0.7) / 20)
            height = math.floor(
                (self.board.surface.get_height() * 0.9265) / 16)

            # Create a new bomb and add it to the list
            bomb = dr.Bomb(self.board, image_file='images/bomb.png',
                           width=width, height=height, player=player, i=i, j=j)
            self.bombs.append(bomb)
        else:
            if player == 1:
                self.hero1.bomb = 1
            elif player == 2:
                self.hero2.bomb = 1

        main.lock.release()

    def spawn_cubes(self, iteration=1000000000000, wait=True):
        """
        Spawn cubes on the game board.

        Args:
            iteration (int, optional): The number of iterations to spawn cubes. Defaults to 1000000000000.
            wait (bool, optional): Whether to wait between spawning cubes. Defaults to True.
        """
        rows = len(main.cord_list)
        columns = len(main.cord_list[0])

        for _ in range(iteration):
            i = random.randrange(rows)
            j = random.randrange(columns)

            main.lock.acquire()

            # Check if the selected position is available
            if main.cord_list[i][j] == 0 and not self.is_corner_or_adjacent(i, j, columns):
                # Check collision with heroes
                hero_collision = False
                for hero in [self.hero1, self.hero2]:
                    hero_i = hero.get_position_i()
                    hero_j = hero.get_position_j()
                    if (abs(hero_i - i) == 1 and hero_j == j) or (hero_i == i and abs(hero_j - j) == 1):
                        hero_collision = True
                        break

                if not hero_collision:
                    main.cord_list[i][j] = 1

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
                    cube = dr.Cube(x, y, width, height, i=i, j=j)
                    self.cubes.append(cube)

            main.lock.release()
            pygame.time.wait(10) if wait else None

    def spawn_items(self):
        """
        Spawn items at random positions on the game board.
        """

        while True:
            i = random.randrange(len(main.cord_list))
            j = random.randrange(len(main.cord_list[0]))

            main.lock.acquire()

            # Check if the selected position is available
            if main.cord_list[i][j] == 0:
                main.cord_list[i][j] = 1

                # Calculate the width and height of the item based on the board size
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor(
                    (self.board.surface.get_height() * 0.9265) / 16)

                # Create a new item and add it to the list
                item = dr.Item(self.board, item_type=random.randrange(
                    2), width=width, height=height, i=i, j=j)
                self.items.append(item)

            main.lock.release()
            pygame.time.wait(5000)

    def is_corner_or_adjacent(self, i, j, columns):
        """
        Check if the given position is a corner or adjacent to the corner.

        Args:
            i (int): Row index.
            j (int): Column index.
            columns (int): Number of columns in the board.

        Returns:
            bool: True if the position is a corner or adjacent to the corner, False otherwise.
        """
        return (i == 0 and (j == 0 or j == 1)) or (i == 1 and (j == 0 or j == columns - 1)) or (
                    i == 0 and (j == columns - 1 or j == columns - 2))
