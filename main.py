import arcade as ac
import socket
from random import randrange
from Menu import Menu
from Level import Level

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
SCREEN_TITLE = "Ninja Battle"


class NinjaBattle(ac.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.user_id = randrange(100000000)

        # connect to server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("127.0.0.1", 4444))
        self.socket.setblocking(False)

        self.x_offset = 0
        self.y_offset = 0

        self.show_game()
        #self.show_menu()

    def show_menu(self):
        self.show_view(Menu(self))

    def show_game(self):
        self.show_view(Level(self, 1))


def main():
    NinjaBattle(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ac.run()


if __name__ == "__main__":
    main()
