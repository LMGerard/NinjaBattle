import arcade as ac


class ScoreManager:
    def __init__(self, players: ac.SpriteList, window: ac.Window):
        self.players = players

        self.window = window

    def draw(self):
        font_size = 12

        for index, player in enumerate(self.players):
            ac.draw_text(f"{player.name} : {player.score}", self.window.x_offset + 10,
                         self.window.y_offset + self.window.height - font_size * 1.5 * (index + 1), (0, 0, 0),
                         font_size=font_size)
