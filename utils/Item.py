import arcade as ac
import math
from time import time


class Item(ac.Sprite):
    max_id = 0

    def __init__(self, image_path: str, scale: float, player, goal_pos: tuple):
        self.id = Item.max_id
        Item.max_id += 1
        super().__init__(filename=image_path, scale=scale)
        self.player = player
        self.goal_x, self.goal_y = self.goal_pos = goal_pos


class Weapon(Item):
    def __init__(self, image_path: str, scale: float, player, goal_pos: tuple, damages: float):
        super().__init__(image_path=image_path, scale=scale, player=player, goal_pos=goal_pos)
        self.level = self.player.level
        self.damages = damages

        self.is_main_player = self.player is self.level.player

    def collision_detection(self):
        remove = False
        # ground detection
        if self.collides_with_list(self.level.grounds_list):
            remove = True

        # player detection
        for player in self.level.players:
            if player is not self.player:
                if ac.check_for_collision(self, player):
                    remove = True

        if not self.is_main_player and ac.check_for_collision(self, self.level.player):
            self.level.player.health_bar.health -= self.damages
            self.level.player.last_attackers[self.player.user_id] = self.damages

        if remove:
            self.player.items.remove(self)

    def update(self):
        self.collision_detection()


class Projectile(Weapon):
    def __init__(self, filename: str, scale: float, player, goal_pos: tuple, speed: int, damages):
        super().__init__(image_path=filename, scale=scale, player=player, goal_pos=goal_pos, damages=damages)
        self.variable = self.change_variable = self.change_speed = 0

        self.start_pos = self.center_x, self.center_y = player.position
        self.speed = speed

        v = self.speed / math.sqrt((self.goal_x - self.center_x) ** 2 + (self.goal_y - self.center_y) ** 2)
        self.change_x, self.change_y = (self.goal_x - self.center_x) * v, (self.goal_y - self.center_y) * v

    def update(self):
        self.center_x = self.change_x_function()
        self.center_y = self.change_y_function()
        self.angle = self.change_angle_function()
        self.speed = self.change_speed_function()
        self.variable = self.change_variable_function()

        self.collision_detection()

    def change_x_function(self):
        return self.center_x + self.change_x

    def change_y_function(self):
        return self.center_y + self.change_y

    def change_angle_function(self):
        return self.angle + self.change_angle

    def change_variable_function(self):
        return self.variable + self.change_variable

    def change_speed_function(self):
        return self.speed


class Shuriken(Projectile):
    image_path = "./assets/shuriken.png"
    scale = 0.035
    speed = 10
    type = "shuriken"
    damages = 10

    def __init__(self, player: ac.Sprite, goal_pos: tuple):
        super().__init__(self.image_path, self.scale, player, goal_pos, self.speed, Shuriken.damages)
        self.change_angle = 15


class FireWork(Projectile):
    image_path = "./assets/firework.png"
    scale = 0.11
    speed = 3
    type = "firework"
    damages = 50

    def __init__(self, player: ac.Sprite, goal_pos: tuple):
        super().__init__(self.image_path, self.scale, player, goal_pos, FireWork.speed, FireWork.damages)

        self.distance = self.goal_x - self.center_x
        if self.distance < 0:
            self.speed = -self.speed
        self.y_max = abs(self.distance) / 2

        self.variable = -self.distance / 2
        self.change_variable = self.speed

        self.coefficient = 1 / self.y_max
        self.change_x = self.change_variable

    def change_y_function(self):
        return self.start_pos[1] - self.coefficient * (self.variable ** 2) + self.y_max

    def change_speed_function(self):
        return self.speed + self.speed * 0.02

    def change_x_function(self):
        return self.center_x + self.speed

    def change_variable_function(self):
        return self.variable + self.speed

    def change_angle_function(self):
        angle = (self.variable + self.distance / 2) * 180 / self.distance
        if angle > 180:
            angle = 180
        if self.distance > 0:
            angle *= -1
        return angle


class Platform(Item, ac.Sprite):
    image_path = "./assets/platform.png"
    scale = 0.9
    alive_time = 2
    speed = 0
    type = "platform"

    def __init__(self, player, goal_pos: tuple):
        super().__init__(image_path=self.image_path, player=player, goal_pos=goal_pos, scale=self.scale)
        self.center_x, self.center_y = self.goal_x, self.goal_y
        self.time = time()

    def update(self):
        if time() - self.time >= self.alive_time:
            self.player.level.grounds_list.remove(self)
            self.player.items.remove(self)


class Katana():
    pass


class Dash(Item, ac.Sprite):
    image_path = "./assets/platform.png"
    speed = 10
    distance = 100

    def __init__(self, player, goal_pos: tuple):
        super().__init__(image_path=self.image_path, player=player, goal_pos=goal_pos, scale=1)

        v = self.speed / math.sqrt((self.goal_x - player.center_x) ** 2 + (self.goal_y - player.center_y) ** 2)
        self.change_x, self.change_y = (self.goal_x - player.center_x) * v, (self.goal_y - player.center_y) * v

    def update(self):
        self.player.center_x += self.change_x
        self.player.center_y += self.change_y
