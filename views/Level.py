import arcade as ac
import arcade.gui as gui
from utils.ScoreManager import ScoreManager
from Player import Player
import json


class Level(ac.View):
    def __init__(self, window: ac.Window, number: int):
        super().__init__(window)
        self.players = ac.SpriteList()
        self.score_manager = ScoreManager(self.players, self.window)
        self.ui_manager = gui.UIManager(self.window)
        self.players_by_ids = {}
        self.level_number = number
        self.gravity = 1

        self.window.set_mouse_cursor(self.window.get_system_mouse_cursor(self.window.CURSOR_CROSSHAIR))

        self.items_to_update = ac.SpriteList()
        self.grounds_list = None
        self.player = None

    def on_draw(self):
        ac.start_render()
        self.grounds_list.draw()
        for player in self.players:
            player.draw_all()
        self.score_manager.draw()

    def on_update(self, delta_time):
        self.networking()
        self.players.update()
        self.grounds_list.update()
        self.items_to_update.update()

    def networking(self):
        try:
            message, address = self.window.socket.recvfrom(1024)
            message = json.loads(message)
        except:
            message = None

        if message is not None:
            if message["msg"] == "game_data":
                self.players_by_ids[message["user_id"]].from_dict(message)
            elif message["msg"] == "spawn":
                self.player.reset()
                self.player.from_dict(message)
            elif message["msg"] == "end":
                self.end_game()

        self.network_send(self.player.objectify())

    def network_send(self, data):
        data["user_id"] = self.window.user_id
        self.window.socket.sendto(json.dumps(data).encode('utf-8'), self.window.address)

    def on_key_press(self, key, key_modifiers):
        self.player.key_press(key)

    def on_key_release(self, key, key_modifiers):
        self.player.key_release(key)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        x, y = x + self.window.x_offset, y + self.window.y_offset
        self.player.mouse_press(x, y, button)

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def on_window_deactivate(self):
        """
        Function called by main.py when the window is deactivated
        """
        self.player.change_x = 0

    def end_game(self):
        self.score_manager.end_screen = True

    def setup(self, users_ids):
        for user_id in users_ids:
            player = Player(self.window, self, user_id)
            player.setup()

            self.players.append(player)
            self.players_by_ids[user_id] = player
            if user_id == self.window.user_id:
                self.player = player

        self.load_level_file()

    def load_level_file(self):
        """
        Load the level from tmx file to the game
        :return:
        """
        tile_map = ac.tilemap.read_tmx(f"assets/level_{self.level_number}.tmx")

        self.grounds_list = ac.tilemap.process_layer(tile_map, 'ground', 1)

        if tile_map.properties is not None and "gravity" in tile_map.properties.keys():
            self.gravity = int(tile_map.properties["gravity"])

        if tile_map.background_color:
            ac.set_background_color(tile_map.background_color)

        for player in self.players:
            player.physics_engine = ac.PhysicsEnginePlatformer(player, self.grounds_list, self.gravity)