import arcade as ac
import math


class Projectile(ac.Sprite):
    max_id = 0

    def __init__(self, filename: str, scale: float, pos: tuple, goal_pos: tuple, speed: int):
        self.id = Projectile.max_id
        Projectile.max_id += 1

        super().__init__(filename=filename, scale=scale)
        self.variable = self.change_variable = self.change_speed = 0

        self.start_pos = self.center_x, self.center_y = pos
        self.goal_pos = self.goal_x, self.goal_y = goal_pos
        self.speed = speed

        v = self.speed / math.sqrt((self.goal_x - self.center_x) ** 2 + (self.goal_y - self.center_y) ** 2)
        self.change_x, self.change_y = (self.goal_x - self.center_x) * v, (self.goal_y - self.center_y) * v

    def update(self):
        self.center_x = self.change_x_function()
        self.center_y = self.change_y_function()
        self.angle = self.change_angle_function()
        self.speed = self.change_speed_function()
        self.variable = self.change_variable_function()

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


class Shuriken(Projectile, ac.Sprite):
    image_path = "./assets/shuriken.png"
    scale = 0.035
    speed = 10
    type = "shuriken"
    damage = 10

    def __init__(self, player: ac.Sprite, goal_pos: tuple):
        super().__init__(self.image_path, self.scale, player.position, goal_pos, self.speed)
        self.change_angle = 15


class FireWork(Projectile, ac.Sprite):
    image_path = "./assets/firework.png"
    scale = 0.11
    speed = 3
    type = "firework"
    damage = 50

    def __init__(self, player: ac.Sprite, goal_pos: tuple):
        super().__init__(self.image_path, self.scale, player.position, goal_pos, self.speed)

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
