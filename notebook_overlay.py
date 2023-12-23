import glob
import time
import tkinter as tk

import numpy as np
from PIL import Image

import translator
from constants import is_str_empty
from notebook_database import NotebookDatabase
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import image_processing as imp

NOTEBOOK_ITEMS = [
    ((20, 35),   (256, 16), "#e0e0e0"),
    ((24, 64),   (72, 16),  "#e0e0e0"),
    ((24, 80),   (72, 16),  "#e0e0e0"),
    ((24, 96),   (72, 16),  "#e0e0e0"),
    ((24, 112),  (72, 16),  "#e0e0e0"),
    ((24, 128),  (72, 16),  "#dddddd"),
    ((108, 64),  (72, 16),  "#e0e0e0"),
    ((108, 80),  (72, 16),  "#dedede"),
    ((108, 96),  (72, 16),  "#d8d8d8"),
    ((108, 112), (72, 16),  "#d3d3d3"),
    ((108, 128), (72, 16),  "#cecece"),
    ((200, 64),  (72, 16),  "#d8d8d8"),
    ((200, 80),  (72, 16),  "#d5d5d5"),
    ((200, 96),  (72, 16),  "#d2d2d2"),
    ((200, 112), (72, 16),  "#cacaca"),
    ((200, 128), (72, 16),  "#c8c8c8"),
]


class NotebookOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, item_id: int, db: NotebookDatabase, pcr: PoorCR = None):
        self.db = db if db is not None else NotebookDatabase()
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
        img_item = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                (self.pos_x_gamescreen + self.width),
                                (self.pos_y_gamescreen + self.height)))
        red, green, blue = np.array(img_item.convert('RGB')).T

        beige = (np.mean((red == green) & (blue == green)) > 0.2) and np.mean((red > 150) & (blue > 150) & (green > 150))
        lightgreen = np.mean((red > 120) & (blue > 120) & (green > 200)) > 0.4

        self.is_selected = lightgreen and not beige
        self.toggle_selected(self.is_selected)

        is_detected = beige or lightgreen

        if is_detected and self.is_hidden:
            img_item_bw = imp.convert_notebook_to_black_and_white(img_item)
            img_item_bw = imp.trim_text(img_item_bw)
            img_item_bw_np = np.array(img_item_bw.convert('1'))
            self.pcr.calibrate(img_item_bw_np)

        return is_detected

    def update_text(self, img_ss: Image):
        img_item = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                self.pos_x_gamescreen + self.width,
                                self.pos_y_gamescreen + self.height))
        img_item_bw = imp.convert_notebook_to_black_and_white(img_item)
        img_item_bw = imp.trim_text(img_item_bw)

        text_jp = self.pcr.detect(img_item_bw)
        if is_str_empty(text_jp):
            self.hide()
            text = text_jp
        else:
            text_en = self.db.retrieve_translation(text_jp)
            if text_en is None:
                text_en = translator.translate_text(text_jp, "google_cloud")
                self.db.insert_translation(text_jp, text_en)
                print(f"Adding new notebook item: {text_jp} - {text_en}")
            text = text_en

        self.update("   " + text)

    def toggle_selected(self, val: bool):
        if val:
            self.label.config(bg='#bbebbb')
        else:
            self.label.config(bg=self.bg_color)


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    db = NotebookDatabase()

    overlays = [NotebookOverlayWindow(window_id, i, db) for i in range(16)]
    # overlays = [NotebookOverlayWindow(window_id, 1, db)]

    while True:
        img_ss = get_window_image(window_id, use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)

        for overlay in overlays:
            overlay.hide_if_not_needed(img_ss)
            overlay.update_text(img_ss)
