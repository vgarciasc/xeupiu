import time
import tkinter as tk

import numpy as np
from PIL import Image

from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

DATE_COMPONENT_POS = [(298, 62), (298, 92), (298, 124)]
DATE_COMPONENT_NAMES = ["YEAR", "MON", "DAY"]

class YearMonthDayOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, date_component_id: int):
        self.date_component_id = date_component_id
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        attr_str = DATE_COMPONENT_NAMES[self.date_component_id]
        pos_x, pos_y = DATE_COMPONENT_POS[self.date_component_id]
        self.bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_DATE-DAY.png")
        self.font_size = min(self.game_scaling * 5, 24)

        self.textbox_width = int(18 * self.game_scaling)
        self.textbox_height = int(15 * self.game_scaling)
        self.pos_x = window_pos_x + (pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text=attr_str, font=("MS PGothic", self.font_size), fg='white',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, img_ss: Image) -> bool:
        img_attr = img_ss.crop((DATE_COMPONENT_POS[self.date_component_id][0] - 2,
                                DATE_COMPONENT_POS[self.date_component_id][1] + 7,
                                (DATE_COMPONENT_POS[self.date_component_id][0] + 18 - 2),
                                (DATE_COMPONENT_POS[self.date_component_id][1] + 15 + 7)))
        red, green, blue = np.array(img_attr.convert('RGB')).T
        return np.any((red < 50) & (blue < 50) & (green > 70))

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlays = [YearMonthDayOverlayWindow(window_id, i) for i in range(3)]

    while True:
        time.sleep(1)
