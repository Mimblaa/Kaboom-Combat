import pygame
import pygame.locals
import threading as th
from concurrent.futures import ThreadPoolExecutor
import time
import random
import sys
from drawable import *
from board import *


lock = th.Lock()
cord_list = [[0 for j in range(20)] for i in range(16)]


class Game:

    def __init__(self, width, height):
        pygame.init()
        self.background = Background(
            'images/background.png',  width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(image_file='images/hero1.png',width=30, height=30, x=width/2, y=height/2, name="Player 1")
        self.hero2 = Hero(image_file='images/hero2.png',width=30, height=30, x=width//3, y=height//3, color=(255, 0, 0), name="Player 2")
        hearts1 = [Heart(width=width, height=height, live_type=True, player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=width, height=height, live_type=True, player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)
        self.timer = Timer(width, 80)
        self.tab = []
        self.bombs = []
        self.cubes = []
        self.score1 = Score(width, height,1)
        self.score2 = Score(width, height,2)
        self.prof1 = Profile(width, height, 1)
        self.prof2 = Profile(width, height, 2)


    def run(self):



        threads = [
            th.Thread(target=self.timer.count_down),
            th.Thread(target=self.spawn_items),
            th.Thread(target=self.spawn_bombs),
            th.Thread(target=self.spawn_cubes),
        ]

        # Run in separate threads
        for thread in threads:
            thread.start()

        while not self.handle_events():
           self.bomb_colision()  # Sprawdzanie kolizji dla każdej bomby
           self.board.draw(
                self.background,
                self.hero1,
                self.hero2,
                self.timer,
                *self.tab,
                *self.bombs,
                *self.cubes,
                self.score1,
                self.score2,
                self.prof1,
                self.prof2,
            )

        # Wait until both threads have finished
        for thread in threads:
            thread.join()
        pygame.quit()

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.hero1.move(x=0, y=-1, board=self.board)
            if self.check_collision(self.hero1):  # Sprawdzanie kolizji z kostkami dla hero1
                self.hero1.move(x=0, y=1, board=self.board)
        if keys[pygame.K_DOWN]:
            self.hero1.move(x=0, y=1, board=self.board)
            if self.check_collision(self.hero1):  # Sprawdzanie kolizji z kostkami dla hero1
                self.hero1.move(x=0, y=-1, board=self.board)
        if keys[pygame.K_LEFT]:
            self.hero1.move(x=-1, y=0, board=self.board)
            if self.check_collision(self.hero1):  # Sprawdzanie kolizji z kostkami dla hero1
                self.hero1.move(x=1, y=0, board=self.board)
        if keys[pygame.K_RIGHT]:
            self.hero1.move(x=1, y=0, board=self.board)
            if self.check_collision(self.hero1):  # Sprawdzanie kolizji z kostkami dla hero1
                self.hero1.move(x=-1, y=0, board=self.board)


        if keys[pygame.K_w]:
            self.hero2.move(x=0, y=-1, board=self.board)
            if self.check_collision(self.hero2):  # Sprawdzanie kolizji z kostkami dla hero2
                self.hero2.move(x=0, y=1, board=self.board)
        if keys[pygame.K_s]:
            self.hero2.move(x=0, y=1, board=self.board)
            if self.check_collision(self.hero2):  # Sprawdzanie kolizji z kostkami dla hero2
                self.hero2.move(x=0, y=-1, board=self.board)
        if keys[pygame.K_a]:
            self.hero2.move(x=-1, y=0, board=self.board)
            if self.check_collision(self.hero2):  # Sprawdzanie kolizji z kostkami dla hero2
                self.hero2.move(x=1, y=0, board=self.board)
        if keys[pygame.K_d]:
            self.hero2.move(x=1, y=0, board=self.board)
            if self.check_collision(self.hero2):  # Sprawdzanie kolizji z kostkami dla hero2
                self.hero2.move(x=-1, y=0, board=self.board)

    #check colision between hero and bombs
    def bomb_colision(self):
        for bomb in self.bombs:
            if self.hero1.rect.colliderect(bomb.rect):
                self.hero1.remove_live()
                self.bombs.remove(bomb)
                del bomb
                self.score2.increase_score(10)  # Zwiększenie punktacji o 10
                break  # Dodajemy break, aby przerwać pętlę po znalezieniu kolizji

        for bomb in self.bombs:
            if self.hero2.rect.colliderect(bomb.rect):
                self.hero2.remove_live()
                self.bombs.remove(bomb)
                del bomb

                self.score1.increase_score(10)  # Zwiększenie punktacji o 10
                break

    def spawn_items(self):
        global cord_list
        while True:
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0])-1)
            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor((self.board.surface.get_height() * 0.9265) / 16)
                item = Item(self.board, i=i, j=j,width=width, height=height)
                self.tab.append(item)

            lock.release()
            pygame.time.wait(5000)


    def spawn_bombs(self):
        global cord_list
        while True:
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0])-1)
            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
                width = math.floor((self.board.surface.get_width() * 0.7) / 20)
                height = math.floor((self.board.surface.get_height() * 0.9265) / 16)
                bomb = Bomb(self.board, image_file='images/bomb.png', i=i, j=j,width=width, height=height)
                self.bombs.append(bomb)

            lock.release()
            pygame.time.wait(5000)

    def spawn_cubes(self):
        global cord_list
        while True:
            i = random.randrange(len(cord_list))
            j = random.randrange(len(cord_list[0])-1)
            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
                rows = len(cord_list)
                columns = len(cord_list[0])
                x = math.ceil(
                    (self.board.surface.get_width() * 0.25) + math.ceil((self.board.surface.get_width() * 0.7 / columns) * i))
                y = math.ceil((self.board.surface.get_height() * 0.04) + math.ceil(
                    (self.board.surface.get_height() * 0.9265 / rows) * j))
                width=math.floor((self.board.surface.get_width() * 0.7)/20)
                height=math.floor((self.board.surface.get_height()*0.9265)/16)
                cube = Cube(self.board, x, y, width, height)
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
