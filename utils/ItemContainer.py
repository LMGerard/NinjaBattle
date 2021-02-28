from utils.Item import *
from utils.constants import TOOLBAR_OBJECT_SIZE
import math


class ItemContainer:
    def __init__(self, window: ac.Window, projectile, countdown: float, scale: float):
        super().__init__()
        self.window = window
        self.item = projectile

        self.ready_to_launch = True
        self.countdown = countdown
        self.time = time()

        self.image = ac.load_texture(projectile.image_path)
        self.scale = scale

    def draw(self, index: int):
        size = TOOLBAR_OBJECT_SIZE
        y = self.window.y_offset + size / 2 + 10
        x = self.window.x_offset + self.window.width - size * index - 10 * (index + 1) - size / 2

        ac.draw_rectangle_filled(x, y, size, size, (255, 255, 255))
        self.image.draw_scaled(x, y, self.scale)
        ac.draw_rectangle_outline(x, y, size, size, (0, 0, 0))

        if not self.ready_to_launch:
            height = (size - (time() - self.time) * size / self.countdown) * (self.ready_to_launch == 0)
            ac.draw_rectangle_filled(x, y - (size - height) / 2, size, height, (255, 0, 0, 150))

    def launch(self, player: ac.Sprite, goal_pos):
        reach = True
        if hasattr(self, "reach"):
            dist = math.sqrt((player.center_x - goal_pos[0]) ** 2 + (player.center_y - goal_pos[1]) ** 2)
            reach = dist <= self.reach

        if self.ready_to_launch and reach:
            self.ready_to_launch = False
            self.time = time()
            return self.item(player, goal_pos=goal_pos)

    def update(self):
        if time() - self.time >= self.countdown:
            self.ready_to_launch = True

    def reset_countdown(self):
        self.ready_to_launch = True

    @classmethod
    def force_launch(cls, player: ac.Sprite, goal_pos):
        return cls.item(player, goal_pos)


class ShurikenContainer(ItemContainer):
    item = Shuriken
    countdown = 0.5

    def __init__(self, window: ac.Window):
        super().__init__(window, self.item, self.countdown, 0.1)


class FireWorkContainer(ItemContainer):
    item = FireWork
    countdown = 3
    reach = 500

    def __init__(self, window: ac.Window):
        super().__init__(window, self.item, self.countdown, 0.15)


class PlatformContainer(ItemContainer):
    item = Platform
    countdown = 10
    reach = 200

    def __init__(self, window: ac.Window):
        super().__init__(window, self.item, self.countdown, 2)


class DashContainer(ItemContainer):
    item = Dash
    countdown = 2

    def __init__(self, window: ac.Window):
        super().__init__(window, self.item, self.countdown, 2)

