import time
import tkinter as tk
from ctypes import windll
import win32gui
from PIL.Image import Image

from constants import *
from screenshot import get_window_by_title, get_window_image

bg_img = None


class OverlayWindow:
    """ A semi-transparent window that displays text on top of the game window. """

    def __init__(self, window_id: int):
        pos_x, pos_y, width, height = self.get_window_dims(window_id)
        self.create_overlay(pos_x, pos_y, width, height)

        self.is_hidden = False
        self.iterations_wout_gameobj = 0

    def get_window_dims(self, window_id: int):
        windll.user32.SetProcessDPIAware()
        left, top, right, bot = win32gui.GetWindowRect(window_id)
        width, height = right - left, bot - top
        pos_x, pos_y = left, top

        pos_y += SIZE_TOOLBAR + SIZE_WINDOW_BORDER_TOP

        self.game_scaling = width // 320
        self.font_size = min(self.game_scaling * 6, 24)

        return pos_x, pos_y, width, height

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        global bg_img

        self.pos_x = window_pos_x + (TB_POS_X * self.game_scaling)
        self.pos_y = window_pos_y + int(TB_POS_Y * self.game_scaling)
        self.textbox_width = int(TB_WIDTH * self.game_scaling)
        self.textbox_height = int(TB_HEIGHT * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)
        bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_4x.png")

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="asdf", font=("MS PGothic", self.font_size), fg='white',
                              wraplength=self.textbox_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()

    def detect_gameobj(self, img_ss: Image) -> bool:
        """
        Detects whether the game object to be overlayed is present in the screenshot.
        """

        return True

    def hide_if_not_needed(self, img_ss: Image) -> None:
        """
        Hides the overlay if it is not needed.
        """

        if self.detect_gameobj(img_ss):
            self.iterations_wout_gameobj = 0
        else:
            self.iterations_wout_gameobj += 1

        if self.iterations_wout_gameobj > ITERS_WOUT_GAMEOBJ_BEFORE_MINIMIZING:
            self.hide()
        else:
            self.show()

    def hide(self):
        """
        Hides the overlay window.
        """

        if self.is_hidden:
            return

        self.root.attributes("-alpha", 0.0)
        self.root.update_idletasks()
        self.root.update()
        self.is_hidden = True

    def show(self):
        """
        Shows the overlay window.
        """

        if not self.is_hidden:
            return

        self.root.attributes("-alpha", 0.9)
        self.root.update_idletasks()
        self.root.update()
        self.is_hidden = False

    def update(self, new_text: str, char_name: str = None) -> None:
        """
        Updates the text displayed on the overlay.

        :param new_text: The new text to display.
        :param char_name: The name of the character speaking the text.
        """

        if char_name:
            new_text = char_name + "\n  " + new_text + ""

        new_text = new_text.replace("\" \"", "\"\n\"")

        self.label.config(text=new_text)
        self.root.update_idletasks()
        self.root.update()

    @staticmethod
    def create_master():
        root_tk = tk.Tk()
        root_tk.overrideredirect(True)
        root_tk.attributes("-alpha", 0.0)
        return root_tk


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = OverlayWindow(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        overlay.hide()
        time.sleep(0.5)
        overlay.show()
        time.sleep(0.5)
