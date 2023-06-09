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
    def __init__(self, width, height, game_time):
        self.width = width
        self.height = height
        self.game_time = game_time
        self.board_elements = None
        pygame.init()
        self.background = Background(
            'images/background.png', width, height)
        self.background2 = Background(
            'images/blank.png', width, height)
        self.board = Board(width, height, background=self.background)
        self.hero1 = Hero(self.board, image_file='images/hero1.png', width=30,
                          height=30, x=width - width * 0.0734, y=height * 0.04, name="Player 1")
        self.hero2 = Hero(self.board, image_file='images/hero2.png', width=30, height=30,
                          x=width * 0.25, y=height * 0.04,  name="Player 2")
        hearts1 = [Heart(width=width, height=height, live_type=True,
                         player=1, number=i) for i in range(1, 4)]
        hearts2 = [Heart(width=width, height=height, live_type=True,
                         player=2, number=i) for i in range(1, 4)]
        self.hero1.set_hearts(hearts1)
        self.hero2.set_hearts(hearts2)
        self.timer = Timer(width, game_time)
        self.items = []
        self.bombs = []
        self.cubes = []
        self.score1 = Score(width, height, 1)
        self.score2 = Score(width, height, 2)
        self.prof1 = Profile(width, height, 1)
        self.prof2 = Profile(width, height, 2)
        self.profitems1 = ProfilePowerUps(width, height, 1, 0)
        self.profitems2 = ProfilePowerUps(width, height, 2, 0)
        self.text_end = Text(width * 0.11, "Time's up!",
                             width * 0.1446, height * 0.168)
        self.text_end_live = Text(width * 0.11, "Player died",
                                  width * 0.1446, height * 0.168)
        self.text_points1 = Text(width * 0.055, " ", width * 0.1446, height * 0.507)
        self.text_points2 = Text(width * 0.055, " ", width * 0.1446, height * 0.6774)
        self.restart_button = Reset(width, height)

    def reset_game(self):
        self.__init__(self.width,self.height,self.game_time)
        global cord_list
        cord_list = [[0 for i in range(20)] for j in range(16)]
        cord_list[0][0] = 1
        cord_list[0][19] = 1
        game.prepare()
        game.run()

    def prepare(self):
        random_number = random.randint(200, 250)
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
            self.bomb_collision()
            self.item_collision()
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
            elif event.type == pygame.USEREVENT and (self.timer.time_left == 0 or self.hero1.lives == 0 or self.hero2.lives == 0):
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
                    # Oczekiwanie na wcisnięcie resetu
                    for event in pygame.event.get():
                        if event.type == pygame.locals.QUIT:
                            pygame.quit()
                            exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Lewy przycisk myszy wciśnięty
                            if self.restart_button.rect.collidepoint(
                                    pygame.mouse.get_pos()):  # Sprawdzenie czy kliknięcie nastąpiło na przycisku
                                self.reset_game()
                                break
                    else:
                        continue  # Jeśli nie wcisnięto przycisku, kontynuuj pętlę
                    break  # Jeśli wcisnięto reset, wyjście z pętli

        # Mapowanie klawiszy do ruchu i akcji
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
                    hero_obj.move(x, y, self.board)
                    if self.check_collision(hero_obj):
                        hero_obj.move(-x, -y, self.board)
                elif action == 1 and hero_obj.bomb == 1:
                    hero_obj.bomb = 0
                    self.spawn_bombs(hero_obj.rect.x, hero_obj.rect.y, hero)

    def bomb_collision(self):
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

            # After the loop, remove the bombs that were marked for deletion
        self.bombs = [bomb for bomb in self.bombs if bomb.timer > 0]

        # Update bomb timers
        for bomb in self.bombs:
            bomb.bomb_delay()

    def item_collision(self):
        for item in self.items:
            if self.hero1.rect.colliderect(item.rect):
                self.process_item_collision(item, self.hero1, self.profitems1)
                break

        for item in self.items:
            if self.hero2.rect.colliderect(item.rect):
                self.process_item_collision(item, self.hero2, self.profitems2)
                break

    def process_item_collision(self, item, hero, profitems):
        self.items.remove(item)
        if item.item_type == 0:  # heart
            hero.add_live()
        if item.item_type == 1:  # shield
            hero.shield = 1
            profitems.add_shield()
        cord_list[item.i][item.j] = 0
        del item

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
                    2), width=width, height=height, i=i, j=j)
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
        rows = len(cord_list)
        columns = len(cord_list[0])

        for _ in range(iteration):
            i = random.randrange(rows)
            j = random.randrange(columns)

            lock.acquire()
            if cord_list[i][j] == 0:
                cord_list[i][j] = 1
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
    game = Game(1200, 600, 80)
    game.prepare()
    game.run()
