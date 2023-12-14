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
    "日": "SUN",
    "月": "MON",
    "火": "TUE",
    "水": "WED",
    "木": "THU",
    "金": "FRI",
    "土": "SAT",
}

class WeekdayOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        self.pcr = PoorCR(only_perfect=True)
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        self.bg_img = tk.PhotoImage(file="data/emerald_bg_DATE-DAY.png")
        self.font_size = min(self.game_scaling * 5, 24)

        self.pos_x_game, self.pos_y_game = (298, 141)
        self.textbox_width = int(18 * self.game_scaling)
        self.textbox_height = int(18 * self.game_scaling)
        self.pos_x = window_pos_x + (self.pos_x_game * self.game_scaling)
        self.pos_y = window_pos_y + int(self.pos_y_game * self.game_scaling) + 61  # 61 is the height of the taskbar

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="TUE", font=("MS PGothic", self.font_size), fg='cyan',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, img_ss: Image) -> bool:
        img_date = img_ss.crop((self.pos_x_game - 3, self.pos_y_game + 7,
                                (self.pos_x_game + 18 - 3), (self.pos_y_game + 18 + 7)))
        red, green, blue = np.array(img_date.convert('RGB')).T
        return np.any((red < 50) & (blue < 50) & (green > 70))

    def update_weekday(self, img: Image) -> None:
        img_date = img.crop((self.pos_x_game, self.pos_y_game + 11,
                            (self.pos_x_game + 11), (self.pos_y_game + 11 + 11)))

        img_date_np = np.array(img_date.convert('1'))
        weekday, _ = self.pcr.get_char_match(img_date_np)

        self.update(WEEKDAYS[weekday])


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlay = WeekdayOverlayWindow(window_id)

    img_ss = get_window_image(window_id, use_scaling=False)
    img_ss = img_ss.resize((img_ss.size[0] // overlay.game_scaling,
                            img_ss.size[1] // overlay.game_scaling),
                           Image.NEAREST)
    img_ss_bw = imp.convert_weekday_to_black_and_white(img_ss)
    overlay.update_weekday(img_ss_bw)

    while True:
        time.sleep(1)
