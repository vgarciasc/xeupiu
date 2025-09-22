import tkinter as tk

import numpy as np
from PIL import Image

from xeupiu.image_processing import get_count_by_equality
from xeupiu.screenshot import get_window_by_title, get_window_image
from xeupiu.overlay import OverlayWindow

DATE_COMPONENT_POS = [(295, 61), (295, 92), (295, 125)]
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

        self.pos_x = window_pos_x + int(pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)
        self.textbox_width = int(18 * self.game_scaling)
        self.textbox_height = int(15 * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text=attr_str, font=("MS PGothic", self.font_size), fg='white',
                              image=self.bg_img, wraplength=self.textbox_width, justify='left', compound='center')
        self.label.pack()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        c = get_count_by_equality(r, g, b, 304, 30, 16, 148, 247, 214, 156)
        return c == 11

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlays = [YearMonthDayOverlayWindow(window_id, i) for i in range(3)]

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(overlays[0].letterbox_offset[0], overlays[0].letterbox_offset[1]),
                                  offset_y=(overlays[0].letterbox_offset[2], overlays[0].letterbox_offset[3]))
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)
        img_rgb = np.array(img_ss.convert('RGB')).T

        for overlay in overlays:
            overlay.hide_if_not_needed(*img_rgb, img_ss)
