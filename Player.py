import arcade as ac
from utils.Projectile import Shuriken
from constants import BOTTOM_VIEWPORT_MARGIN, LEFT_VIEWPORT_MARGIN, RIGHT_VIEWPORT_MARGIN, TOP_VIEWPORT_MARGIN


class Player(ac.Sprite):
    def __init__(self, window: ac.Window, level):
        super(Player, self).__init__(filename="assets/player_0.png", scale=0.05)
        self.window = window
        self.level = level
        self.physics_engine = None

        self.textures.append(ac.load_texture("assets/player_0.png", flipped_horizontally=True))
        self.set_position(300, 300)

        self.health_bar = HealthBar(self, max_health=100)
        self.speed = 4
        self.jump_force = 18

        self.projectiles = ac.SpriteList()

    def update(self):
        if self.physics_engine is not None:
            self.physics_engine.update()

        self.projectiles.update()

        if self is self.level.player:
            for project in self.projectiles:
                if ac.check_for_collision_with_list(project, self.level.enemies):
                    self.projectiles.remove(project)
                elif ac.check_for_collision_with_list(project, self.level.grounds_list):
                    self.projectiles.remove(project)
        else:
            for project in self.projectiles:
                if ac.check_for_collision(project, self.level.player):
                    self.level.player.health_bar.health -= 10
                    self.projectiles.remove(project)
                elif ac.check_for_collision_with_list(project, self.level.grounds_list):
                    self.projectiles.remove(project)
                else:
                    for enemy in self.level.enemies:
                        if enemy is not self and ac.check_for_collision(project, enemy):
                            self.projectiles.remove(project)
                            break

        # Scroll left
        left_boundary = self.window.x_offset + LEFT_VIEWPORT_MARGIN
        if self.left < left_boundary:
            self.window.x_offset -= left_boundary - self.left

        # Scroll right
        right_boundary = self.window.x_offset + self.window.width - RIGHT_VIEWPORT_MARGIN
        if self.right > right_boundary:
            self.window.x_offset += self.right - right_boundary

        # Scroll up
        top_boundary = self.window.y_offset + self.window.height - TOP_VIEWPORT_MARGIN
        if self.top > top_boundary:
            self.window.y_offset += self.top - top_boundary

        # Scroll down
        bottom_boundary = self.window.y_offset + BOTTOM_VIEWPORT_MARGIN

        if self.bottom < bottom_boundary:
            self.window.y_offset -= bottom_boundary - self.bottom

    def draw_all(self):
        for project in self.projectiles:
            project.draw()
        self.health_bar.draw()
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

    def from_dict(self, data: dict):
        """
        Update the player attributes with new ones, network function
        :param data:dict
        """
        self.health_bar.health = data["health"]
        self.position = data["position"]
        if self.cur_texture_index != data["texture"]:
            self.texture = self.textures[data["texture"]]
            self.cur_texture_index = data["texture"]
        for s_pos, g_pos, speed in data["projectiles"]:
            self.projectiles.append(Shuriken(s_pos, g_pos, speed, fake=True))

    def objectify(self) -> dict:
        """
        Concat the player data inside a dict, network function
        :return:dict
        """
        return {"msg": "game_data",
                "user_id": self.window.user_id,
                "position": self.position,
                "health": self.health_bar.health,
                "texture": self.cur_texture_index,
                "projectiles": [(project.id,
                                 project.start_pos,
                                 project.goal_pos,
                                 project.speed) for project in self.projectiles]}


class HealthBar:
    def __init__(self, player: ac.Sprite, max_health):
        self.player = player

        self.max_health = max_health
        self.health = max_health

    def draw(self):
        width, height = self.player.width, self.player.height // 5
        x, y = self.player.center_x, self.player.top + height * 2
        # red rectangle
        ac.draw_rectangle_filled(x, y, width, height, (255, 0, 0))
        new_width = self.health * width / self.max_health
        # green rectangle
        ac.draw_rectangle_filled(x - (width - new_width) / 2, y, new_width, height, (0, 255, 0))
        # outline
        ac.draw_rectangle_outline(x, y, width, height, (0, 0, 0))
