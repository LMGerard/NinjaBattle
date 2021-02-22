import arcade as ac
import arcade.gui as gui
from utils.ScoreManager import ScoreManager
from Player import Player
import json


class Level(ac.View):
    def __init__(self, window: ac.Window, number: int):
        super().__init__(window)
        self.ui_manager = gui.UIManager(self.window)
        self.players = ac.SpriteList()
        self.level_number = number
        self.gravity = 1

        self.score_manager = None
        self.grounds_list = None
        self.player = None
        self.enemy_player = None

    def on_draw(self):
        ac.start_render()
        self.grounds_list.draw()
        self.player.draw_all()
        self.score_manager.draw()
        self.enemy_player.draw_all()

    def on_update(self, delta_time):
        #self.networking()
        self.players.update()

    def networking(self):
        try:
            message, address = self.window.socket.recvfrom(1024)
            message = json.loads(message)
            if message["msg"] == "game_data":
                self.enemy_player.from_dict(message)
        except:
            pass
        data = self.player.objectify()
        self.window.socket.sendto(json.dumps(data).encode('utf-8'), ("127.0.0.1", 4444))

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

    def setup(self):
        self.player = Player(self.window, self)
        self.enemy_player = Player(self.window, self)
        self.player.setup()
        self.enemy_player.setup()

        self.players.append(self.player)
        self.players.append(self.enemy_player)

        self.score_manager = ScoreManager(self.players)
        self.load_level_file()

    def load_level_file(self):
        """
        Load the level from tmx file to the game
        :return:
        """
        tile_map = ac.tilemap.read_tmx(f"assets/level_{self.level_number}.tmx")

        self.grounds_list = ac.tilemap.process_layer(tile_map, 'ground', 1)

        if tile_map.layers[0].properties is not None and "gravity" in tile_map.layers[0].properties.keys():
            self.gravity = int(tile_map.layers[0].properties["gravity"])

        if tile_map.background_color:
            ac.set_background_color(tile_map.background_color)

        self.player.physics_engine = ac.PhysicsEnginePlatformer(self.player, self.grounds_list, self.gravity)
