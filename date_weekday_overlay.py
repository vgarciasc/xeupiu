import glob
import time
import tkinter as tk

import numpy as np
from PIL import Image

from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import image_processing as imp

WEEKDAYS = {
    "日": ("SUN", "magenta"),
    "月": ("MON", "white"),
    "火": ("TUE", "white"),
    "水": ("WED", "white"),
    "木": ("THU", "white"),
    "金": ("FRI", "white"),
    "土": ("SAT", "cyan"),
}


class WeekdayOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        self.pcr = PoorCR(only_perfect=True)
        self.pos_x_gamescreen = 295
        self.pos_y_gamescreen = 142
        self.w = 18
        self.h = 18
        self.x_between_parenthesis = 298
        self.y_between_parenthesis = 143

        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        self.bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_DATE-DAY.png")
        self.font_size = min(self.game_scaling * 5, 24)

        self.pos_x = window_pos_x + (self.pos_x_gamescreen * self.game_scaling)
        self.pos_y = window_pos_y + ((self.pos_y_gamescreen - 1) * self.game_scaling)
        self.textbox_width = int(self.w * self.game_scaling)
        self.textbox_height = int(self.h * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="XXX", font=("MS PGothic", self.font_size), fg='cyan',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        c = imp.get_count_by_equality(r, g, b, 288, 30, 32, 148, 247, 214, 156)
        return c == 23

    def update_weekday(self, img_ss: Image) -> None:
        img_date = img_ss.crop((self.x_between_parenthesis,
                                self.y_between_parenthesis,
                                self.x_between_parenthesis + 11,
                                self.y_between_parenthesis + 11))
        img_date_bw = imp.convert_weekday_to_black_and_white(img_date)

        img_date_np = np.array(img_date_bw.convert('1'))
        weekday, _ = self.pcr.get_char_match(img_date_np)

        wd_label, wd_color = WEEKDAYS.get(weekday, ("--", "white"))
        self.label.config(fg=wd_color)
        self.update(wd_label)


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlay = WeekdayOverlayWindow(window_id)

    img_ss = get_window_image(window_id)
    img_ss = img_ss.resize((img_ss.size[0] // overlay.game_scaling,
                            img_ss.size[1] // overlay.game_scaling),
                           Image.NEAREST)
    img_ss_bw = imp.convert_weekday_to_black_and_white(img_ss)
    overlay.detect_gameobj(img_ss_bw)
    overlay.update_weekday(img_ss_bw)

    while True:
        time.sleep(1)

