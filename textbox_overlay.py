import time
import tkinter as tk
from ctypes import windll

import numpy as np
import win32gui
from PIL import Image

from constants import TB_POS_X, TB_POS_Y, TB_WIDTH, TB_HEIGHT
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

class TextboxOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        global bg_img

        self.pos_x = window_pos_x + int(TB_POS_X * self.game_scaling) + 4
        self.pos_y = window_pos_y + int(TB_POS_Y * self.game_scaling) - 1
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

    def detect_gameobj(self, img_tb: Image) -> bool:
        r, g, b = np.array(img_tb.convert('RGB')).T

        emerald_bg = np.mean((r < 30) & (g > 86) & (g < 137) & (b == 0)) > 0.4
        has_highlight = np.any((r > 100) & (r < 150) & (g > 170) & (g < 200) & (b > 30))

        return emerald_bg and not has_highlight

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = TextboxOverlayWindow(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        overlay.hide()
        time.sleep(0.5)
        overlay.show()
        time.sleep(0.5)
