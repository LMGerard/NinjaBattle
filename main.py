import arcade as ac
import socket
from random import randrange
from views.Menu import Menu
from views.Level import Level
from utils.constants import SCREEN_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT
import sys
import os


class NinjaBattle(ac.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        self.user_id = randrange(100000000)

        # connect to server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

        self.socket.connect(("127.0.0.1", 4444))
        self.socket.setblocking(False)

        self.x_offset = 0
        self.y_offset = 0

        #self.show_game([self.user_id])
        self.show_menu()

    def show_menu(self):
        self.show_view(Menu(self))

    def show_game(self, players_ids):
        level = Level(self, 1)
        level.setup(players_ids)
        self.show_view(level)

    def on_deactivate(self):
        if isinstance(self.current_view, Level):
            self.current_view.on_window_deactivate()


def main():
    NinjaBattle(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ac.run()


# pyinstaller requirement
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

if __name__ == "__main__":
    main()
