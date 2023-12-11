import time
import tkinter as tk
from ctypes import windll
import win32gui

from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

ATTRIBUTE_POS = [(40, 24), (40, 38), (40, 52), (128, 24), (128, 38), (128, 52), (216, 24), (216, 38), (216, 52)]
ATTRIBUTE_NAMES = ["HEALTH", "ARTS", "STYLE", "HUMAN", "EXERC", "GUTS", "SCIENC", "TRIVIA", "STRESS"]

class AttributeOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, attribute_id: int):
        self.attribute_id = attribute_id
        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        attr_str = ATTRIBUTE_NAMES[self.attribute_id]
        pos_x, pos_y = ATTRIBUTE_POS[self.attribute_id]
        self.bg_img = tk.PhotoImage(file="data/emerald_bg_4x.png")

        self.textbox_width = int(30 * self.game_scaling)
        self.textbox_height = int(15 * self.game_scaling)
        self.pos_x = window_pos_x + (pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling) + 61  # 61 is the height of the taskbar

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

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlays = [AttributeOverlayWindow(window_id, i) for i in range(9)]

    while True:
        time.sleep(1)
