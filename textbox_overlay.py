import time
import tkinter as tk
from ctypes import windll

import numpy as np
import win32gui
from PIL import Image

from config import CONFIG
from constants import TB_POS_X, TB_POS_Y, TB_WIDTH, TB_HEIGHT
from screenshot import get_window_by_title, RESOLUTION_SCALE_OFFSET_Y
from overlay import OverlayWindow

class TextboxOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        global bg_img

        self.pos_x = window_pos_x + int(TB_POS_X * self.game_scaling)
        self.pos_y = window_pos_y + int(TB_POS_Y * self.game_scaling)
        self.textbox_width = int(TB_WIDTH * self.game_scaling)
        self.textbox_height = int(TB_HEIGHT * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)
        bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_4x.png")

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="Loading...", font=("MS PGothic", self.font_size), fg='white',
                              wraplength=self.textbox_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        emerald_bg = np.mean((r < 30) & (g > 86) & (g < 137) & (b == 0)) > 0.4
        has_highlight = np.any((r > 100) & (r < 150) & (g > 170) & (g < 200) & (b > 30))
        has_selection = np.sum((r > 90) & (g > 170) & (b < 100)) > 20

        return emerald_bg and not has_highlight and not has_selection

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = TextboxOverlayWindow(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        # overlay.hide()
        # time.sleep(0.5)
        # overlay.show()
        # time.sleep(0.5)
