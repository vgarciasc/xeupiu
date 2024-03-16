import glob
import time
import tkinter as tk

import numpy as np
from PIL import Image

import translator
from constants import is_str_empty, ITERS_WOUT_GAMEOBJ_BEFORE_MINIMIZING
from notebook_database import NotebookDatabase
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import image_processing as imp

DIVIDER_MARK_3COL_1 = ((100, 54), (9, 9), (41, 132, 164))
DIVIDER_MARK_2COL_1 = ((145, 35), (7, 8), (99, 132, 164))
DIVIDER_MARK_2COL_2 = ((145, 35), (9, 15), (41, 132, 164))

NOTEBOOK_ITEMS = [
    ((20, 35), (256, 16), "#e0e0e0", "3col_1"),
    ((24, 64), (72, 16), "#e0e0e0", "3col_1"),
    ((24, 80), (72, 16), "#e0e0e0", "3col_1"),
    ((24, 96), (72, 16), "#e0e0e0", "3col_1"),
    ((24, 112), (72, 16), "#e0e0e0", "3col_1"),
    ((24, 128), (72, 16), "#dddddd", "3col_1"),
    ((108, 64), (72, 16), "#e0e0e0", "3col_1"),
    ((108, 80), (72, 16), "#dedede", "3col_1"),
    ((108, 96), (72, 16), "#d8d8d8", "3col_1"),
    ((108, 112), (72, 16), "#d3d3d3", "3col_1"),
    ((108, 128), (72, 16), "#cecece", "3col_1"),
    ((200, 64), (72, 16), "#d8d8d8", "3col_1"),
    ((200, 80), (72, 16), "#d5d5d5", "3col_1"),
    ((200, 96), (72, 16), "#d2d2d2", "3col_1"),
    ((200, 112), (72, 16), "#cacaca", "3col_1"),
    ((200, 128), (72, 16), "#c8c8c8", "3col_1"),
    ((36, 56), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 68), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 80), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 92), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 104), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 116), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 128), (98, 12), "#e0e0e0", "2col_1"),
    ((36, 140), (98, 12), "#e0e0e0", "2col_1"),
    ((24, 64), (109, 12), "#e0e0e0", "2col_2"),
    ((24, 80), (109, 12), "#e0e0e0", "2col_2"),
    ((24, 96), (109, 12), "#e0e0e0", "2col_2"),
    ((24, 112), (109, 12), "#e0e0e0", "2col_2"),
    ((24, 128), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 38), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 64), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 80), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 96), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 112), (109, 12), "#e0e0e0", "2col_2"),
    ((160, 128), (109, 12), "#e0e0e0", "2col_2"),
    ((32, 38), (98, 12), "#e0e0e0", "2col_2"),
    ((160, 38), (98, 12), "#e0e0e0", "2col_2"),
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
        self.group_code = notebook_item[3]

        if self.group_code == "3col_1":
            self.divider_mark = DIVIDER_MARK_3COL_1
        elif self.group_code == "2col_1":
            self.divider_mark = DIVIDER_MARK_2COL_1
        elif self.group_code == "2col_2":
            self.divider_mark = DIVIDER_MARK_2COL_2
        else:
            raise ValueError(f"Invalid group code: {self.group_code}")

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
        self.label = tk.Label(self.root, text="", font=("MS PGothic", self.font_size), fg='#70779e',
                              width=self.textbox_width, height=self.textbox_height,
                              wraplength=self.textbox_width, bg=self.bg_color,
                              justify='left', compound='left', anchor='w')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, img_ss: Image) -> bool:
        red, green, blue = np.array(img_ss.convert('RGB')).T

        is_divider_there = self.detect_divider(red, green, blue)
        if not is_divider_there:
            return False

        img_item = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                (self.pos_x_gamescreen + self.width),
                                (self.pos_y_gamescreen + self.height)))

        red, green, blue = np.array(img_item.convert('RGB')).T

        beige = (np.mean((red == green) & (blue == green)) > 0.2) and np.mean(
            (red > 150) & (blue > 150) & (green > 150))
        lightgreen = np.mean((red > 120) & (blue > 120) & (green > 200)) > 0.4

        self.is_selected = lightgreen and not beige
        self.toggle_selected(self.is_selected)

        is_detected = beige or lightgreen

        if is_detected and self.is_hidden:
            img_item_bw = imp.convert_notebook_to_black_and_white(img_item)

            if imp.check_is_text_empty(img_item_bw):
                return False

            img_item_bw = imp.convert_notebook_to_black_and_white(img_item)
            img_item_bw = imp.trim_text(img_item_bw)
            img_item_bw_np = np.array(img_item_bw.convert('1'))
            self.pcr.calibrate(img_item_bw_np)

        return is_detected

    def detect_divider(self, red, green, blue):
        x, y = self.divider_mark[0]
        w, h = self.divider_mark[1]
        r, g, b = self.divider_mark[2]

        red = red[x:x + w, y:y + h]
        green = green[x:x + w, y:y + h]
        blue = blue[x:x + w, y:y + h]

        is_divider_there = np.sum((red == r) & (green == g) & (blue == b)) > 5
        return is_divider_there

    def update_text(self, img_ss: Image):
        img_item = img_ss.crop((self.pos_x_gamescreen,
                                self.pos_y_gamescreen,
                                self.pos_x_gamescreen + self.width,
                                self.pos_y_gamescreen + self.height))

        img_item_bw = imp.convert_notebook_to_black_and_white(img_item)
        img_item_bw = imp.trim_text(img_item_bw)

        if imp.check_is_text_empty(img_item_bw):
            self.hide()
            return

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

    def toggle_selected(self, val: bool):
        if val:
            self.label.config(bg='#bbebbb')
        else:
            self.label.config(bg=self.bg_color)


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    db = NotebookDatabase()

    overlays = [NotebookOverlayWindow(window_id, i, db) for i in range(len(NOTEBOOK_ITEMS))]
    # overlays = [NotebookOverlayWindow(window_id, 15, db)]

    while True:
        img_ss = get_window_image(window_id, use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)

        for overlay in overlays:
            overlay.hide_if_not_needed(img_ss)
            overlay.update_text(img_ss)
