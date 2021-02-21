import arcade as ac
import math


class Projectile(ac.Sprite):
    max_id = 0

    def __init__(self, filename: str, scale: float, pos: tuple, goal_pos: tuple, speed: int, fake=False):
        if not fake:
            self.id = Projectile.max_id
            Projectile.max_id += 1

        super().__init__(filename=filename, scale=scale)
        self.start_pos = self.center_x, self.center_y = pos
        self.goal_pos = self.goal_x, self.goal_y = goal_pos
        self.speed = speed

        # scale vector to the speed
        v = self.speed / math.sqrt((self.goal_x - self.center_x) ** 2 + (self.goal_y - self.center_y) ** 2)
        self.change_x, self.change_y = (self.goal_x - self.center_x) * v, (self.goal_y - self.center_y) * v
        self.change_angle = 15

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.angle += self.change_angle


class Shuriken(Projectile, ac.Sprite):
    image_path = "./assets/shuriken.png"
    scale = 0.035

    def __init__(self, pos: tuple, goal_pos: tuple, speed: int, fake=False):
        super().__init__(self.image_path, self.scale, pos, goal_pos, speed, fake=fake)
