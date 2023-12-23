import glob
import time
import tkinter as tk

import numpy as np
from PIL import Image

from constants import is_str_empty
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import image_processing as imp

NOTEBOOK_ITEMS = [
    ((20, 35), (256, 16), "#e0e0e0"),
    ((32, 64), (64, 16), "#e0e0e0"),
    ((32, 80), (64, 16), "#e0e0e0"),
    ((32, 96), (64, 16), "#e0e0e0"),
    ((32, 112), (64, 16), "#e0e0e0"),
    ((32, 128), (64, 16), "#dddddd"),
    ((116, 64), (64, 16), "#e0e0e0"),
    ((116, 80), (64, 16), "#dedede"),
    ((116, 96), (64, 16), "#d8d8d8"),
    ((116, 112), (64, 16), "#d3d3d3"),
    ((116, 128), (64, 16), "#cecece"),
    ((200, 64), (64, 16), "#d8d8d8"),
    ((200, 80), (64, 16), "#d5d5d5"),
    ((200, 96), (64, 16), "#d2d2d2"),
    ((200, 112), (64, 16), "#cacaca"),
    ((200, 128), (64, 16), "#c8c8c8"),
]


class NotebookOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, item_id: int, pcr: PoorCR = None):
        self.pcr = pcr if pcr is not None else PoorCR(only_perfect=True)

        self.item_id = item_id
        self.is_selected = False
        notebook_item = NOTEBOOK_ITEMS[item_id]

        self.pos_x_gamescreen, self.pos_y_gamescreen = notebook_item[0]
        self.width, self.height = notebook_item[1]
        self.bg_color = notebook_item[2]

        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        self.font_size = min(self.game_scaling * 6, 32)

        self.textbox_width = int(self.width * self.game_scaling)
        self.textbox_height = int(self.height * self.game_scaling)
        self.pos_x = window_pos_x + (self.pos_x_gamescreen * self.game_scaling)
        self.pos_y = window_pos_y + (self.pos_y_gamescreen * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="XXX", font=("MS PGothic", self.font_size), fg='#70779e',
                              width=self.textbox_width, height=self.textbox_height,
                              wraplength=self.textbox_width, bg=self.bg_color,
                              justify='left', compound='left', anchor='w')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, img_ss: Image) -> bool:
        img_date = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                (self.pos_x_gamescreen + self.width),
                                (self.pos_y_gamescreen + self.height)))
        red, green, blue = np.array(img_date.convert('RGB')).T

        beige = (np.mean((red == green) & (blue == green)) > 0.2) and np.mean((red > 150) & (blue > 150) & (green > 150))
        lightgreen = np.mean((red > 120) & (blue > 120) & (green > 200)) > 0.4

        self.is_selected = lightgreen and not beige
        self.toggle_selected(self.is_selected)

        return beige or lightgreen

    def update_text(self, img_ss: Image):
        img_item = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                self.pos_x_gamescreen + self.width,
                                self.pos_y_gamescreen + self.height))
        img_item_bw = imp.convert_notebook_to_black_and_white(img_item)
        img_item_bw = imp.trim_text(img_item_bw)

        text = self.pcr.detect(img_item_bw)

        if is_str_empty(text):
            self.hide()

        self.update(text)

    def toggle_selected(self, val: bool):
        if val:
            self.label.config(bg='#bbebbb')
        else:
            self.label.config(bg=self.bg_color)


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()

    # overlays = [NotebookOverlayWindow(window_id, i) for i in range(16)]
    overlays = [NotebookOverlayWindow(window_id, 0)]

    while True:
        img_ss = get_window_image(window_id, use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)

        for overlay in overlays:
            overlay.hide_if_not_needed(img_ss)
            overlay.update_text(img_ss)
