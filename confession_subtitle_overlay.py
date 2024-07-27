import time
import tkinter as tk
from ctypes import windll

import numpy as np
import win32gui
from PIL import Image

from constants import TB_POS_X, TB_POS_Y, TB_WIDTH, TB_HEIGHT
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

class ConfessionSubtitleOverlay(OverlayWindow):
    def __init__(self, window_id: int):
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        pos_x, pos_y, width, height = 50, 200, 200, 20

        self.font_size = min(self.game_scaling * 5, 24)

        self.pos_x = window_pos_x + int(pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)
        self.textbox_width = int(width * self.game_scaling)
        self.textbox_height = int(height * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)
        self.bg_img = tk.PhotoImage(file="data/backgrounds/subtitle_bg_4x.png")

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="Lorem ipsum dolor", font=("MS PGothic", self.font_size), fg='white',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = ConfessionSubtitleOverlay(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        overlay.hide()
        time.sleep(0.5)
        overlay.show()
        time.sleep(0.5)
