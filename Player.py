from utils.constants import BOTTOM_VIEWPORT_MARGIN, LEFT_VIEWPORT_MARGIN, RIGHT_VIEWPORT_MARGIN, TOP_VIEWPORT_MARGIN
from utils.ItemContainer import *


class Player(ac.Sprite):
    def __init__(self, window: ac.Window, level, user_id):
        super(Player, self).__init__(filename="assets/player_0.png", scale=0.05)
        self.window = window
        self.level = level
        self.user_id = user_id
        self.physics_engine = None
        self.ui_manager = None

        self.score = 0
        self.name = self.user_id  # to change later

        self.health_bar = HealthBar(self, max_health=100, health=0)
        self.items = ac.SpriteList()
        self.speed = 4
        self.jump_force = 18
        self.can_move = True
        self.can_attack = True

        self.items = ac.SpriteList()
        self.items_containers = []
        self.platforms = []

        self.last_attacker = None
        self.last_attackers = {}

    def reset(self):
        self.health_bar = HealthBar(self, max_health=100, health=100)
        self.speed = 4
        self.jump_force = 18
        self.can_move = True
        self.can_attack = True
        self.last_attacker = None
        self.last_attackers = {}
        self.items = ac.SpriteList()

    def setup(self):
        # load textures
        self.textures.append(ac.load_texture("assets/player_0.png", flipped_horizontally=True))
        self.set_position(400, 300)
        if self.user_id == self.window.user_id:
            self.items_containers.append(ShurikenContainer(self.window))
            self.items_containers.append(FireWorkContainer(self.window))
            self.items_containers.append(PlatformContainer(self.window))

    def update(self):
        self.items.update()
        if self.can_move:
            self.physics_engine.update()

        if self is self.level.player:
            for container in self.items_containers:
                container.update()

            if len(self.last_attackers) > 0:
                self.last_attacker = max(self.last_attackers.keys(), key=lambda x: self.last_attackers[x])
                self.last_attackers = {}

            # viewport scroll
            changed = False

            left_boundary = self.window.x_offset + LEFT_VIEWPORT_MARGIN
            if self.left < left_boundary:
                self.window.x_offset -= left_boundary - self.left
                changed = True

            right_boundary = self.window.x_offset + self.window.width - RIGHT_VIEWPORT_MARGIN
            if self.right > right_boundary:
                self.window.x_offset += self.right - right_boundary
                changed = True

            top_boundary = self.window.y_offset + self.window.height - TOP_VIEWPORT_MARGIN
            if self.top > top_boundary:
                self.window.y_offset += self.top - top_boundary
                changed = True

            bottom_boundary = self.window.y_offset + BOTTOM_VIEWPORT_MARGIN
            if self.bottom < bottom_boundary:
                self.window.y_offset -= bottom_boundary - self.bottom
                changed = True

            if changed:
                self.window.y_offset = int(self.window.y_offset)
                self.window.x_offset = int(self.window.x_offset)

                self.window.set_viewport(self.window.x_offset,
                                         self.window.width + self.window.x_offset,
                                         self.window.y_offset,
                                         self.window.height + self.window.y_offset)

    def draw_all(self):
        self.items.draw()
        for index, item in enumerate(self.items_containers):
            item.draw(index)
        self.health_bar.draw()
        self.draw()

    def key_press(self, key):
        if key == ac.key.Z and self.physics_engine.can_jump():
            self.physics_engine.jump(self.jump_force)
        elif key == ac.key.Q:
            self.change_x -= max(self.speed, self.change_x - self.speed)
        elif key == ac.key.D:
            self.change_x = min(self.speed, self.change_x + self.speed)

        self.update_texture()

    def key_release(self, key):
        if key == ac.key.Q:
            self.change_x += self.speed
        elif key == ac.key.D:
            self.change_x -= self.speed

        self.update_texture()

    def mouse_press(self, x, y, button):
        if button == ac.MOUSE_BUTTON_LEFT and self.can_attack:
            item = self.items_containers[1].launch(self, (x, y))
            if item is not None:
                self.items.append(item)
        elif button == ac.MOUSE_BUTTON_RIGHT and self.can_attack:
            item = self.items_containers[0].launch(self, (x, y))
            if item is not None:
                self.items.append(item)
        elif button == ac.MOUSE_BUTTON_MIDDLE and self.can_attack:
            item = self.items_containers[2].launch(self, (x, y))
            if item is not None:
                if not item.collides_with_list(self.level.grounds_list):
                    self.level.grounds_list.append(item)
                    self.items.append(item)
                else:
                    self.items_containers[2].reset_countdown()

    def update_texture(self):
        if self.change_x < 0:
            self.set_texture(1)
            self.cur_texture_index = 1
        elif self.change_x > 0:
            self.set_texture(0)
            self.cur_texture_index = 0

    def from_dict(self, data: dict):
        """
        Update the player attributes with new ones, network function
        :param data:dict
        """
        keys = data.keys()
        if "health" in keys:
            self.health_bar.health = data["health"]
        if "position" in keys and False:
            self.position = data["position"]
        if "texture" in keys and self.cur_texture_index != data["texture"]:
            self.cur_texture_index = data["texture"]
            self.set_texture(self.cur_texture_index)
        if "score" in keys:
            self.score = data["score"]
        if "items" in keys:
            for p_type, p_pos in data["items"]:
                if p_type == "shuriken":
                    item = ShurikenContainer.force_launch(self, p_pos)
                elif p_type == "firework":
                    item = FireWorkContainer.force_launch(self, p_pos)
                elif p_type == "platform":
                    item = PlatformContainer.force_launch(self, p_pos)
                    self.level.grounds_list.append(item)
                self.items.append(item)
        if "change" in keys:
            pass
            #self.change_x, self.change_y = data["change"]

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
                "last_attacker": self.last_attacker,
                "change": (self.change_x, self.change_y),
                "items": [(item.id, item.type, item.goal_pos) for item in self.items]}


class HealthBar:
    def __init__(self, player: Player, max_health: int, health: int):
        self.player = player

        self.max_health = max_health
        self.health = health
        self.health = 100
        self.last_health = None

        self.health_bar_complete = ac.load_texture("assets/health_bar_complete.png")
        self.health_bar_black = ac.load_texture("assets/health_bar_black.png")
        self.health_bar_red = None

    def draw(self):
        if self.player is self.player.level.player:
            x, y = self.player.window.x_offset, self.player.window.y_offset
            self.health_bar_complete.draw_scaled(center_x=x + self.health_bar_complete.width / 2,
                                                 center_y=y + self.health_bar_complete.height / 2, scale=1)

            if self.last_health != self.health:
                new_width = self.health * 291 / self.max_health
                self.health_bar_red = ac.load_texture("assets/health_bar_red.png", x=0, y=0, height=27, width=new_width)
                self.last_health = self.health

            self.health_bar_red.draw_transformed(left=x + 75, bottom=y + 59,
                                                 width=self.health_bar_red.width, height=self.health_bar_red.height)
        else:
            width, height = self.player.width, self.player.height // 5
            x, y = self.player.center_x, self.player.top + height * 2

            ac.draw_rectangle_filled(center_x=x, center_y=y, width=width, height=height, color=(22, 0, 0))

            n_width = self.health * width / 100
            ac.draw_rectangle_filled(center_x=x - width / 2 + n_width / 2, center_y=y,
                                     width=n_width, height=height, color=(203, 0, 2))
