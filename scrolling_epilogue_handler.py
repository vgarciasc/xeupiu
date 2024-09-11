import time
import tkinter as tk

import numpy as np
from PIL import Image

import image_processing as imp
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
from scrolling_epilogue_database import ScrollingEpilogueDatabase
from translator import Translator

SCROLLING_BOX = [
    (87, 55, 155, 13),
    (87, 71, 155, 13),
    (87, 87, 155, 13),
    (87, 103, 155, 13),
    (87, 119, 155, 13),
    (87, 135, 155, 13),
    (87, 151, 155, 13)
]

class ScrollingEpilogueHandler:
    def __init__(self, window_id):
        self.window_id = window_id
        self.db = ScrollingEpilogueDatabase()
        self.pcr = PoorCR(only_perfect=True, padding_x=3, should_calibrate=False)
        self.tt = Translator()

        self.overlay = ScrollingEpilogueOverlayWindow(window_id)

        self.scrolling_text = []

    def handle(self, img_ss_rgb: np.ndarray, img_ss: Image):
        if self.detect_scrolling_epilogue_screen(img_ss_rgb):
            if self.overlay.is_hidden:
                self.overlay.show()

            text = self.read_onscreen_text(img_ss)
            if text != "":
                self.update_text(text)
        else:
            self.overlay.update("")
            self.overlay.hide()

    def update_text(self, text: str):
        translation = self.db.retrieve_translation(text)
        if translation is None:
            translation = self.tt.translate(text)
            self.db.insert_translation(text, translation)

        self.overlay.update(translation)

    def detect_scrolling_epilogue_screen(self, img_ss_rgb: np.ndarray) -> bool:
        return imp.get_count_by_equality(*img_ss_rgb, 16, 187, 40, 40, 107, 173, 58) == 193

    def read_onscreen_text(self, img_ss: Image) -> str:
        texts = []
        for x, y, w, h in SCROLLING_BOX:
            text = self.read_onscreen_area(x, y, w, h, img_ss)
            texts.append(text)

        if '?' not in ''.join(texts):
            for i, text in enumerate(texts):
                if text not in self.scrolling_text:
                    self.scrolling_text += texts[i:]
                elif text == '':
                    if i > 0 and texts[i - 1] == self.scrolling_text[-1]:
                        self.scrolling_text += ['']

            if len(self.scrolling_text) > 0:
                scrolling_blocks = [(' ' if x == '' else x) for x in self.scrolling_text]
                scrolling_blocks = ''.join(scrolling_blocks).strip().split(" ")
                if len(scrolling_blocks) > 0 and self.scrolling_text[-1] == '':
                    block = scrolling_blocks[-1]
                    return block

                # scrolling_blocks = ''.join(self.scrolling_text).split("。")
                #
                # if len(scrolling_blocks) > 1:
                #     block = scrolling_blocks[-2] + "。"
                #     return block

        return ""

    def read_onscreen_area(self, x: int, y: int, w: int, h: int, img_ss: Image):
        img_tb = img_ss.crop((x, y, x + w, y + h))
        img_tb = imp.convert_to_black_and_white(img_tb, (164, 206, 206))

        return self.pcr.detect(img_tb, should_recalibrate=False)

class ScrollingEpilogueOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        self.is_selected = False
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        pos_x, pos_y, w, h = 60, 200, 200, 32

        self.pos_x = window_pos_x + int(pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)
        self.textbox_width = int(w * self.game_scaling)
        self.textbox_height = int(h * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text=" ", font=("MS PGothic", self.font_size), fg='white',
                              bg='black', wraplength=self.textbox_width, justify='center', compound='center',
                              width=self.textbox_width, height=self.textbox_height)
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    handler = ScrollingEpilogueHandler(window_id)

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(handler.overlay.letterbox_offset[0], handler.overlay.letterbox_offset[1]),
                                  offset_y=(handler.overlay.letterbox_offset[2], handler.overlay.letterbox_offset[3]),
                                  use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // handler.overlay.game_scaling,
                                img_ss.size[1] // handler.overlay.game_scaling),
                               Image.NEAREST)
        img_rgb = np.array(img_ss.convert('RGB')).T

        handler.handle_scrolling_epilogue(img_rgb, img_ss)
