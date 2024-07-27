import time
import tkinter as tk

import numpy as np
from PIL import Image

from image_processing import get_count_by_equality
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

ATTRIBUTE_POS = [(40, 23), (40, 37), (40, 51), (128, 23), (128, 37), (128, 51), (216, 23), (216, 37), (216, 51)]
ATTRIBUTE_NAMES = ["HEALTH", "ARTS", "STYLE", "HUMAN", "EXERC", "GUTS", "SCIENC", "TRIVIA", "STRESS"]

class AttributeOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, attribute_id: int):
        self.attribute_id = attribute_id
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        attr_str = ATTRIBUTE_NAMES[self.attribute_id]
        pos_x, pos_y = ATTRIBUTE_POS[self.attribute_id]
        self.bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_4x.png")

        self.pos_x = window_pos_x + int(pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)
        self.textbox_width = int(30 * self.game_scaling)
        self.textbox_height = int(15 * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text=attr_str, font=("MS PGothic", self.font_size), fg='white',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        c = get_count_by_equality(r, g, b, 192, 10, 24, 20, 49, 0, 0)
        return c == 96

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlays = [AttributeOverlayWindow(window_id, i) for i in range(9)]

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(overlays[0].letterbox_offset[0], overlays[0].letterbox_offset[1]),
                                  offset_y=(overlays[0].letterbox_offset[2], overlays[0].letterbox_offset[3]),
                                  use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)
        img_rgb = np.array(img_ss.convert('RGB')).T

        for overlay in overlays:
            overlay.hide_if_not_needed(*img_rgb, img_ss)
