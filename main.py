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

lock = th.Lock()
cord_list = [[0 for i in range(20)] for j in range(16)]
cord_list[0][0] = 1
cord_list[0][19] = 1
semaphore = th.Semaphore(10)


class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board_elements = None
        pygame.init()
        self.background = Background(
            'images/background.png', width, height)
        self.background2 = Background(
            'images/blank.png', width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(self.board, image_file='images/hero1.png', width=30,
                          height=30, x=width * 0.25, y=height * 0.04, name="Player 1")
        self.hero2 = Hero(self.board, image_file='images/hero2.png', width=30, height=30,
                          x=width - width * 0.0734, y=height * 0.04, color=(255, 0, 0), name="Player 2")
        hearts1 = [Heart(width=width, height=height, live_type=True,
                         player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=width, height=height, live_type=True,
                         player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)
        self.timer = Timer(width, 80)
        self.items = []
        self.bombs = []
        self.cubes = []
        self.score1 = Score(width, height, 1)
        self.score2 = Score(width, height, 2)
        self.prof1 = Profile(width, height, 1)
        self.prof2 = Profile(width, height, 2)
        self.profitems1 = Profile_power_ups(width, height, 1, 0)
        self.profitems2 = Profile_power_ups(width, height, 2, 0)
        self.text_end = Text(width * 0.11, "Time's up!",
                             width * 0.1446, height * 0.168)
        self.text_end_live = Text(width * 0.11, "Player died",
                                  width * 0.1446, height * 0.168)
        self.text_points1 = Text(
            width * 0.055, " ", width * 0.1446, height * 0.507)
        self.text_points2 = Text(
            width * 0.055, " ", width * 0.1446, height * 0.6774)
        self.game_paused = False

    def reset_game(self):
        self.board_elements = None
        pygame.init()
        self.background = Background(
            'images/background.png', self.width, self.height)
        self.background2 = Background(
            'images/blank.png', self.width, self.height)
        self.board = Board(self.width, self.height, background=self.background)
        self.hero1 = Hero(self.board, image_file='images/hero1.png', width=30,
                          height=30, x=self.width * 0.25, y=self.height * 0.04, name="Player 1")
        self.hero2 = Hero(self.board, image_file='images/hero2.png', width=30, height=30,
                          x=self.width - self.width * 0.0734, y=self.height * 0.04, color=(255, 0, 0), name="Player 2")
        hearts1 = [Heart(width=self.width, height=self.height, live_type=True,
                         player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=self.width, height=self.height, live_type=True,
                         player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)
        self.timer = Timer(self.width, 80)
        self.items = []
        self.bombs = []
        self.cubes = []
        self.score1 = Score(self.width, self.height, 1)
        self.score2 = Score(self.width, self.height, 2)
        self.prof1 = Profile(self.width, self.height, 1)
        self.prof2 = Profile(self.width, self.height, 2)
        self.profitems1 = Profile_power_ups(self.width, self.height, 1, 0)
        self.profitems2 = Profile_power_ups(self.width, self.height, 2, 0)
        self.text_end = Text(self.width * 0.11, "Time's up!",
                             self.width * 0.1446, self.height * 0.168)
        self.text_end_live = Text(self.width * 0.11, "Player died",
                                  self.width * 0.1446, self.height * 0.168)
        self.text_points1 = Text(
            self.width * 0.055, " ", self.width * 0.1446, self.height * 0.507)
        self.text_points2 = Text(
            self.width * 0.055, " ", self.width * 0.1446, self.height * 0.6774)
        global cord_list
        cord_list = [[0 for i in range(20)] for j in range(16)]
        cord_list[0][0] = 1
        cord_list[0][19] = 1
        game.prepare()
        game.run()

    def prepare(self):
        random_number = random.randint(20, 60)
        self.spawn_cubes(random_number, False)

    def run(self):
        threads = [
            th.Thread(target=self.timer.count_down),
            th.Thread(target=self.spawn_items),
            th.Thread(target=self.spawn_cubes)
        ]

        # Run in separate threads
        for thread in threads:
            thread.start()

        while not self.handle_events():
            if not self.game_paused:
                self.bomb_colision()  # Sprawdzanie kolizji dla każdej bomby
                self.item_colision()
                self.board_elements = [
                    self.background,
                    self.hero1,
                    self.hero2,
                    self.timer,
                    *self.items,
                    *self.bombs,
                    *self.cubes,
                    self.score1,
                    self.score2,
                    self.prof1,
                    self.prof2,
                    self.profitems1,
                    self.profitems2,
                ]
                self.board.draw(*self.board_elements)

        # Wait until both threads have finished
        for thread in threads:
            thread.join()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.USEREVENT:
                self.board_elements.clear()
                self.board_elements.append(self.background2)
                if self.timer.time_left == 0:
                    self.board_elements.append(self.text_end)
                else:
                    self.board_elements.append(self.text_end_live)
                self.text_points1.text = str(
                    self.hero1.name) + " points: " + str(self.score1.score)
                self.text_points2.text = str(
                    self.hero2.name) + " points: " + str(self.score2.score)
                self.board_elements.append(self.text_points1)
                self.board_elements.append(self.text_points2)
                self.board.draw(*self.board_elements)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.game_paused = not self.game_paused

                while True:
                    # Oczekiwanie na wcisnięcie spacji
                    for event in pygame.event.get():
                        if event.type == pygame.locals.QUIT:
                            pygame.quit()
                            exit()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            self.reset_game()
                            break
                    else:
                        continue  # Jeśli nie wcisnięto spacji, kontynuuj pętlę
                    break  # Jeśli wcisnięto spacje, wyjście z pętli

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.hero1.move(x=0, y=-1, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero1
            if self.check_collision(self.hero1):
                self.hero1.move(x=0, y=1, board=self.board)
        if keys[pygame.K_DOWN]:
            self.hero1.move(x=0, y=1, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero1
            if self.check_collision(self.hero1):
                self.hero1.move(x=0, y=-1, board=self.board)
        if keys[pygame.K_LEFT]:
            self.hero1.move(x=-1, y=0, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero1
            if self.check_collision(self.hero1):
                self.hero1.move(x=1, y=0, board=self.board)
        if keys[pygame.K_RIGHT]:
            self.hero1.move(x=1, y=0, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero1
            if self.check_collision(self.hero1):
                self.hero1.move(x=-1, y=0, board=self.board)
        if keys[pygame.K_b]:
            if self.hero1.bomb == 1:
                self.hero1.bomb = 0
                self.spawn_bombs(self.hero1.rect.x, self.hero1.rect.y, 1)

        if keys[pygame.K_w]:
            self.hero2.move(x=0, y=-1, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero2
            if self.check_collision(self.hero2):
                self.hero2.move(x=0, y=1, board=self.board)
        if keys[pygame.K_s]:
            self.hero2.move(x=0, y=1, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero2
            if self.check_collision(self.hero2):
                self.hero2.move(x=0, y=-1, board=self.board)
        if keys[pygame.K_a]:
            self.hero2.move(x=-1, y=0, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero2
            if self.check_collision(self.hero2):
                self.hero2.move(x=1, y=0, board=self.board)
        if keys[pygame.K_d]:
            self.hero2.move(x=1, y=0, board=self.board)
            # Sprawdzanie kolizji z kostkami dla hero2
            if self.check_collision(self.hero2):
                self.hero2.move(x=-1, y=0, board=self.board)
        if keys[pygame.K_n]:
            if self.hero2.bomb == 1:
                self.hero2.bomb = 0
                self.spawn_bombs(self.hero2.rect.x, self.hero2.rect.y, 2)

    def bomb_colision(self):
        for bomb in self.bombs:
            if bomb.timer == 0:
                bomb_position_hero1 = (
                    self.hero1.get_position_i(), self.hero1.get_position_j())
                bomb_position_hero2 = (
                    self.hero2.get_position_i(), self.hero2.get_position_j())

                # Check collision with hero1
                if (bomb.i, bomb.j) == bomb_position_hero1 or \
                        abs(bomb.i - bomb_position_hero1[0]) + abs(bomb.j - bomb_position_hero1[1]) == 1:
                    self.hero1.remove_live()
                    self.profitems1.remove_shield()
                    lock.acquire()
                    cord_list[bomb.i][bomb.j] = 0
                    lock.release()
                    self.score2.increase_score(10)

                # Check collision with hero2
                elif (bomb.i, bomb.j) == bomb_position_hero2 or \
                        abs(bomb.i - bomb_position_hero2[0]) + abs(bomb.j - bomb_position_hero2[1]) == 1:
                    self.hero2.remove_live()
                    self.profitems1.remove_shield()
                    lock.acquire()
                    cord_list[bomb.i][bomb.j] = 0
                    lock.release()
                    self.score1.increase_score(10)

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
                # Remove bomb after checking collisions
                self.bombs.remove(bomb)

            # After the loop, remove the bombs that were marked for deletion
        self.bombs = [bomb for bomb in self.bombs if bomb.timer > 0]

        # Update bomb timers
        for bomb in self.bombs:
            bomb.bomb_delay()

    # check colision between hero and items
    def item_colision(self):
        for item in self.items:
            if self.hero1.rect.colliderect(item.rect):
                self.items.remove(item)
                if item.item_type == 0:  # heart
                    self.hero1.add_live()
                if item.item_type == 1:  # shield
                    self.hero1.activate_shield()
                    self.profitems1.add_shield()
                lock.acquire()
                cord_list[item.i][item.j] = 0
                lock.release()
                del item
                break

        for item in self.items:
            if self.hero2.rect.colliderect(item.rect):
                self.items.remove(item)
                if item.item_type == 0:  # heart
                    self.hero2.add_live()
                if item.item_type == 1:  # shield
                    self.hero2.activate_shield()
                    self.profitems2.add_shield()
                lock.acquire()
                cord_list[item.i][item.j] = 0
                lock.release()
                del item
                break

    def spawn_items(self):
        global cord_list
        while True:
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0]))
            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor(
                    (self.board.surface.get_height() * 0.9265) / 16)
                item = Item(self.board, item_type=random.randrange(
                    2), i=i, j=j, width=width, height=height)
                self.items.append(item)

            lock.release()
            pygame.time.wait(5000)

    def spawn_bombs(self, x, y, player):
        global cord_list
        j = math.floor(
            (x - self.board.surface.get_width() * 0.25) / (
                (self.board.surface.get_width() * 0.7) / len(cord_list[0])))
        i = math.floor((y - self.board.surface.get_height() * 0.04) / (
            (self.board.surface.get_height() * 0.9265) / len(cord_list)))

        lock.acquire()
        if cord_list[i][j] == 0:
            cord_list[i][j] = 1
            width = math.floor((self.board.surface.get_width() * 0.7) / 20)
            height = math.floor(
                (self.board.surface.get_height() * 0.9265) / 16)
            bomb = Bomb(image_file='images/bomb.png',
                        x=x, y=y, width=width, height=height, player=player, i=i, j=j)
            self.bombs.append(bomb)
        else:
            if player == 1:
                self.hero1.bomb = 1
            elif player == 2:
                self.hero2.bomb = 1

        lock.release()

    def spawn_cubes(self, iteration=1000000000000, wait=True):
        for _ in range(iteration):
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0]))

            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
                rows = len(cord_list)
                columns = len(cord_list[0])
                x = math.ceil(
                    (self.board.surface.get_width() * 0.25) + math.ceil(
                        (self.board.surface.get_width() * 0.7 / columns) * j))
                y = math.ceil((self.board.surface.get_height() * 0.04) + math.ceil(
                    (self.board.surface.get_height() * 0.9265 / rows) * i))
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor(
                    (self.board.surface.get_height() * 0.9265) / 16)
                cube = Cube(x, y, width, height, i=i, j=j)
                self.cubes.append(cube)

            lock.release()
            pygame.time.wait(5000) if wait else None

    def check_collision(self, hero):
        for cube in self.cubes:
            if hero.rect.colliderect(cube.rect):
                return True
        return False


if __name__ == "__main__":
    game = Game(1200, 600)
    game.prepare()
    game.run()
