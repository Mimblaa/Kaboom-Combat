import main
import drawable as dr


class Collisions:
    def bomb_collision(self):
        """
        Handle bomb collisions with heroes, cubes, and countdown timers.
        """
        for bomb in self.bombs:
            if bomb.timer == 50:
                delete_marks = []
                for x, y in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if (bomb.i + x) >= 0 and (bomb.j + y) >= 0 and (bomb.j + y) <= len(main.cord_list[0]) - 1:
                        delete_marks.append(
                            dr.Delete(self.width, self.height, i=bomb.i + x, j=bomb.j + y))
                        bomb.set_marks(delete_marks)
            if bomb.timer == 0:
                bomb_position_hero1 = (
                    self.hero1.get_position_i(), self.hero1.get_position_j())
                bomb_position_hero2 = (
                    self.hero2.get_position_i(), self.hero2.get_position_j())

                # Check collision with hero1
                if (bomb.i, bomb.j) == bomb_position_hero1 or \
                        abs(bomb.i - bomb_position_hero1[0]) + abs(bomb.j - bomb_position_hero1[1]) == 1:
                    if self.hero1.shield == 0:
                        self.hero1.remove_live()
                        main.lock.acquire()
                        main.cord_list[bomb.i][bomb.j] = 0
                        main.lock.release()
                        self.score2.score += 10
                    else:
                        self.hero1.shield = 0
                        self.profitems1.remove_shield()

                # Check collision with hero2
                elif (bomb.i, bomb.j) == bomb_position_hero2 or \
                        abs(bomb.i - bomb_position_hero2[0]) + abs(bomb.j - bomb_position_hero2[1]) == 1:
                    if self.hero2.shield == 0:
                        self.hero2.remove_live()
                        main.lock.acquire()
                        main.cord_list[bomb.i][bomb.j] = 0
                        main.lock.release()
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
                            main.lock.acquire()
                            main.cord_list[cube.i][cube.j] = 0
                            main.lock.release()
                            break

                if bomb.player == 1:
                    self.hero1.bomb = 1
                else:
                    self.hero2.bomb = 1

                # Remove bomb after checking collisions
                self.bombs.remove(bomb)

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
        main.cord_list[item.i][item.j] = 0
        del item


def check_collision(hero, cubes):
    """
    Check collision between the hero and cubes.

    Args:
        hero (Hero): The hero object to check collision for.

    Returns:
        bool: True if collision occurs, False otherwise.
    """
    for cube in cubes:
        if hero.rect.colliderect(cube.rect):
            return True
    return False
