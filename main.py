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
cord_list = [[0 for j in range(20)] for i in range(16)]


class Game:
    def __init__(self, width, height):
        pygame.init()
        self.background = Background(
            'images/background.png', width, height)
        self.background2 = Background(
            'images/blank.png', width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(image_file='images/hero1.png', width=30,
                          height=30, x=width / 2, y=height / 2, name="Player 1")
        self.hero2 = Hero(image_file='images/hero2.png', width=30, height=30,
                          x=width // 3, y=height // 3, color=(255, 0, 0), name="Player 2")
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
        self.text_end = Text(width * 0.11, "Time's up!",width*0.1446,height*0.168)
        self.text_points1 = Text(width*0.055," ",width*0.1446,height*0.507)
        self.text_points2 = Text(width*0.055, " ",width*0.1446,height*0.6774)

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
                self.board_elements.append(self.text_end)
                self.text_points1.text = str(self.hero1.name)+" points: " + str(self.score1.score)
                self.text_points2.text = str(self.hero2.name)+ " points: " + str(self.score2.score)
                self.board_elements.append(self.text_points1)
                self.board_elements.append(self.text_points2)
                self.board.draw(*self.board_elements)
                return True

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

    # check colision between hero and bombs
    def bomb_colision(self):
        for bomb in self.bombs:
            if self.hero1.rect.colliderect(bomb.rect) and bomb.timer == 0:
                self.hero1.remove_live()
                self.bombs.remove(bomb)
                self.profitems1.remove_shield()
                if bomb.player == 1:
                    self.hero1.bomb = 1
                elif bomb.player == 2:
                    self.hero2.bomb = 1
                lock.acquire()
                cord_list[bomb.i][bomb.j] = 0
                lock.release()
                del bomb
                self.score2.increase_score(10)  # Zwiększenie punktacji o 10
                break  # Dodajemy break, aby przerwać pętlę po znalezieniu kolizji

            if self.hero2.rect.colliderect(bomb.rect) and bomb.timer == 0:
                self.hero2.remove_live()
                self.bombs.remove(bomb)
                self.profitems2.remove_shield()
                if bomb.player == 1:
                    self.hero1.bomb = 1
                elif bomb.player == 2:
                    self.hero2.bomb = 1
                lock.acquire()
                cord_list[bomb.i][bomb.j] = 0
                lock.release()
                del bomb

                self.score1.increase_score(10)  # Zwiększenie punktacji o 10
                break

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
                height = math.floor((self.board.surface.get_height() * 0.9265) / 16)
                item = Item(self.board, item_type=random.randrange(2), i=j, j=i, width=width, height=height)
                self.items.append(item)

            lock.release()
            pygame.time.wait(5000)

    def spawn_bombs(self, x, y, player):
        global cord_list
        i = math.ceil(
            (x - self.board.surface.get_width() * 0.25) / (
                        (self.board.surface.get_width() * 0.7) / len(cord_list[0])))
        j = math.ceil((y - self.board.surface.get_height() * 0.04) / (
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

        lock.release()

    def spawn_cubes(self):
        while True:
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
                cube = Cube(x, y, width, height)
                self.cubes.append(cube)

            lock.release()
            pygame.time.wait(5000)

    def check_collision(self, hero):
        for cube in self.cubes:
            if hero.rect.colliderect(cube.rect):
                return True
        return False


if __name__ == "__main__":
    game = Game(1200, 600)
    game.run()
