import arcade as ac
import arcade.gui as gui
from PIL import Image, ImageOps
import json


class Menu(ac.View):
    def __init__(self, window: ac.Window):
        super().__init__(window)

        self.ui_manager = gui.UIManager(self.window)

    def on_draw(self):
        ac.start_render()

    def on_update(self, delta_time: float):
        try:
            message, address = self.window.socket.recvfrom(1024)
            message = json.loads(message)
            if message["msg"] == "start":
                self.window.show_game()
        except:
            pass

    def join_game(self):
        data = {"user_id": self.window.user_id, "msg": "play"}
        self.window.socket.sendto(json.dumps(data).encode('utf-8'), ("127.0.0.1", 4444))

    def on_show_view(self):
        self.ui_manager.add_ui_element(PlayButton(self))
        # self.ui_manager.add_ui_element(PlayerSelector(self))
        self.ui_manager.add_ui_element(LeftArrow(self))
        # self.ui_manager.add_ui_element(RightArrow(self))

    def on_hide_view(self):
        self.ui_manager.purge_ui_elements()

    @staticmethod
    def open_image(path, width, colorize=None, rotate=None):
        img = Image.open(path).convert("L")
        ratio = (width / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)

        # colorization
        if colorize is not None:
            img = ImageOps.colorize(img, black=colorize[0], white=colorize[1])
        # rotation
        if rotate == 90:
            img = img.transpose(Image.ROTATE_90)
        elif rotate == 180:
            img = img.transpose(Image.ROTATE_180)
        elif rotate == 270:
            img = img.transpose(Image.ROTATE_270)

        return img.convert("RGBA")


class PlayButton(gui.UIFlatButton):
    def __init__(self, view: Menu):
        super().__init__("Play", view.window.width // 2, view.window.height // 3 * 2, id="play_button")
        self.view = view

    def on_click(self):
        self.view.join_game()


class PlayerSelector(gui.UIImageButton):
    def __init__(self, view: Menu):
        img = view.open_image("assets/menu/arrow.png", 50, rotate=90)
        img_02 = view.open_image("assets/menu/arrow_pressed.png", 50, rotate=90)
        super().__init__(normal_texture=ac.Texture("normal", img),
                         press_texture=ac.Texture("pressed", img_02),
                         center_x=view.window.width // 2,
                         center_y=view.window.height // 3)


class LeftArrow(gui.UIImageButton):
    def __init__(self, view: Menu):
        normal = ac.texture.load_texture("assets/menu/arrow.png",
                                         flipped_diagonally=True,
                                         flipped_horizontally=True)
        press = ac.texture.load_texture("assets/menu/arrow_pressed.png",
                                        flipped_diagonally=True,
                                        flipped_horizontally=True)
        super().__init__(normal_texture=normal,
                         press_texture=press,
                         center_x=view.window.width // 3,
                         center_y=view.window.height // 3)
        self.scale = 0.1


class RightArrow(gui.UIImageButton):
    def __init__(self, view: Menu):
        normal = ac.texture.load_texture("assets/menu/arrow.png")
        press = ac.texture.load_texture("assets/menu/arrow_pressed.png",
                                        flipped_diagonally=True,
                                        flipped_horizontally=True,
                                        width=428, height=428)

        super().__init__(normal_texture=normal,
                         press_texture=press,
                         center_x=100,
                         center_y=100,
                         text="salut")
