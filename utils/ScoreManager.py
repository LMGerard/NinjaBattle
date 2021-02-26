import arcade as ac
import arcade.gui as gui
from PIL import ImageDraw


class ScoreManager(gui.UIManager):
    def __init__(self, players: ac.SpriteList, window: ac.Window):
        super().__init__(window)
        self.players = players
        self.end_screen = False

        self.score_panel = ac.load_texture("./assets/score_paneL.png")

    def draw(self):

        font_size = 12

        if not self.end_screen:
            for index, player in enumerate(self.players):
                ac.draw_text(f"{player.name} : {player.score}", self.window.x_offset + 10,
                             self.window.y_offset + self.window.height - font_size * 1.5 * (index + 1), (0, 0, 0),
                             font_size=font_size)
        else:
            x, y = self.window.x_offset + self.window.width / 2, self.window.y_offset + self.window.height / 2
            size = self.window.height * 4 / 5

            self.score_panel.draw_sized(center_x=x, center_y=y, width=size, height=size)
            x, y = x - size / 2, y + size / 2
            font_size = 12

            for index, player in enumerate(self.players):
                ac.draw_text(f"Name : {player.name}           Kill : {player.score}",
                             x + 10, y - font_size * 2 * (index + 1), (255, 255, 255))