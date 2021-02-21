import arcade as ac
from utils.Projectile import Shuriken


class Player(ac.Sprite):
    def __init__(self, window: ac.Window, level):
        super(Player, self).__init__(filename="assets/player_0.png", scale=0.05)
        self.window = window
        self.level = level
        self.physics_engine = None

        self.textures.append(ac.load_texture("assets/player_0.png", flipped_horizontally=True))
        self.set_position(300, 300)

        self.health_bar = HealthBar((100, 50), max_health=100, width=self.width, height=5)
        self.speed = 4
        self.jump_force = 18

        self.projectiles = []

    def update(self):
        for project in self.projectiles:
            if ac.check_for_collision_with_list(project, self.level.grounds_list):
                self.projectiles.remove(project)

        self.physics_engine.update()
        for project in self.projectiles:
            project.update()

        LEFT_VIEWPORT_MARGIN = 100
        RIGHT_VIEWPORT_MARGIN = 100
        TOP_VIEWPORT_MARGIN = 100
        BOTTOM_VIEWPORT_MARGIN = 200
        changed = False

        # Scroll left
        left_boundary = self.window.x_offset + LEFT_VIEWPORT_MARGIN
        if self.left < left_boundary:
            self.window.x_offset -= left_boundary - self.left
            changed = True

        # Scroll right
        right_boundary = self.window.x_offset + self.window.width - RIGHT_VIEWPORT_MARGIN
        if self.right > right_boundary:
            self.window.x_offset += self.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.window.y_offset + self.window.height - TOP_VIEWPORT_MARGIN
        if self.top > top_boundary:
            self.window.y_offset += self.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.window.y_offset + BOTTOM_VIEWPORT_MARGIN
        if self.bottom < bottom_boundary:
            self.window.y_offset -= bottom_boundary - self.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.window.y_offset = int(self.window.y_offset)
            self.window.x_offset = int(self.window.x_offset)

            # Do the scrolling
            ac.set_viewport(self.window.x_offset,
                            self.window.width + self.window.x_offset,
                            self.window.y_offset,
                            self.window.height + self.window.y_offset)

    def update_viewport(self):
        a = self.window.x_offset + self.window.width / 3
        b = self.window.x_offset + self.window.width / 3 * 2

        if self.center_x < a:
            self.window.x_offset -= a - self.center_x
        elif b < self.center_x:
            self.window.x_offset -= b - self.center_x
        c = self.window.y_offset + self.window.height / 6
        d = self.window.y_offset + self.window.height / 3 * 2
        if self.center_y < c:
            self.window.y_offset -= c - self.center_y
        elif d < self.center_y:
            self.window.y_offset -= d - self.center_y

    def draw_all(self):
        for project in self.projectiles:
            project.draw()
        self.health_bar.draw(self.center_x, self.center_y + self.height)
        self.draw()

    def key_press(self, key):
        if key == ac.key.Z and self.physics_engine.can_jump():
            self.physics_engine.jump(self.jump_force)
        elif key == ac.key.Q:
            self.change_x -= self.speed
        elif key == ac.key.D:
            self.change_x += self.speed

        self.update_texture()

    def key_release(self, key):
        if key == ac.key.Q:
            self.change_x += self.speed
        elif key == ac.key.D:
            self.change_x -= self.speed

        self.update_texture()

    def mouse_press(self, x, y, button):
        if button == ac.MOUSE_BUTTON_LEFT:
            self.projectiles.append(Shuriken(self.position, (x, y), 10))

    def update_texture(self):
        ac.set_viewport(0, self.window.width, 0, self.window.height)

        if self.change_x < 0:
            self.texture = self.textures[1]
            self.cur_texture_index = 1
        elif self.change_x > 0:
            self.texture = self.textures[0]
            self.cur_texture_index = 0

    def objectify(self) -> dict:

        return {"msg": "game_data",
                "user_id": self.window.user_id,
                "position": self.position,
                "texture": self.cur_texture_index,
                "projectiles": [(project.id,
                                 project.start_pos,
                                 project.goal_pos,
                                 project.speed) for project in self.projectiles]}


class HealthBar:
    def __init__(self, pos, max_health, width, height):
        self.x, self.y = pos
        self.width = width
        self.height = height

        self.max_health = max_health
        self.health = max_health

    def draw(self, x, y):
        ac.draw_rectangle_filled(x, y, self.width, self.height, (255, 0, 0))
        width = self.health * self.width / self.max_health
        ac.draw_rectangle_filled(x - width / 2, y, width, self.height, (0, 255, 0))
        ac.draw_rectangle_outline(x, y, self.width, self.height, (0, 0, 0))


class EnemyPlayer(ac.Sprite):
    def __init__(self):
        super().__init__(filename="assets/player_1.png", scale=0.05)
        self.textures.append(ac.load_texture("assets/player_1.png", flipped_horizontally=True))
        self.health_bar = HealthBar((100, 50), max_health=100, width=self.width, height=5)
        self.projectiles = []
        self.cur_texture_index = 0

    def draw_all(self):
        for project in self.projectiles:
            project.draw()
        self.health_bar.draw(self.center_x, self.center_y + self.height)
        self.draw()

    def update(self):
        for project in self.projectiles:
            project.update()

    def from_dict(self, data: dict):
        self.position = data["position"]
        if self.cur_texture_index != data["texture"]:
            self.texture = self.textures[data["texture"]]
            self.cur_texture_index = data["texture"]
        for s_pos, g_pos, speed in data["projectiles"]:
            self.projectiles.append(Shuriken(s_pos, g_pos, speed, fake=True))
