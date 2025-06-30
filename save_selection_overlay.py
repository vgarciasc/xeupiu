import time
import tkinter as tk

import numpy as np
from PIL import Image

from image_processing import get_count_by_equality
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

OVERLAY_POS = [
    (18, 25, 40, 16),
    (18, 44, 40, 16),
    (61, 25, 40, 16),
    (61, 44, 40, 16)
]
OVERLAY_TEXTS = ["COPY", "CLEAR", "NEW", "LOAD"]

class SaveSelectionOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int, overlay_id: int):
        self.overlay_id = overlay_id
        self.is_selected = False

        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        text = OVERLAY_TEXTS[self.overlay_id]
        pos_x, pos_y, w, h = OVERLAY_POS[self.overlay_id]

        self.pos_x = window_pos_x + int(pos_x * self.game_scaling)
        self.pos_y = window_pos_y + int(pos_y * self.game_scaling)
        self.textbox_width = int(w * self.game_scaling)
        self.textbox_height = int(h * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text=text, font=("MS PGothic", self.font_size), fg='white',
                              bg='#9473d6', wraplength=self.textbox_width, justify='left', compound='center',
                              width=self.textbox_width, height=self.textbox_height)
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        is_save_creation_screen = self.detect_save_creation_screen(r, g, b)

        if is_save_creation_screen:
            pos_x, pos_y, w, h = OVERLAY_POS[self.overlay_id]

            r = r[pos_x:(pos_x + w), pos_y:(pos_y + h)].T
            g = g[pos_x:(pos_x + w), pos_y:(pos_y + h)].T
            b = b[pos_x:(pos_x + w), pos_y:(pos_y + h)].T

            is_selected = np.sum((r == 255) & (g == 255) & (b == 0)) > 0
            self.toggle_selected(is_selected)

        return is_save_creation_screen

    def detect_save_creation_screen(self, r: np.ndarray, g: np.ndarray, b: np.ndarray) -> bool:
        return get_count_by_equality(r, g, b, 9, 209, 78, 18, 197, 189, 189) == 64

    def toggle_selected(self, value: bool):
        if self.is_selected != value:
            self.is_selected = value
            self.label.config(bg='#5231a4' if value else '#9473d6')
            self.root.update_idletasks()
            self.root.update()


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlays = [SaveSelectionOverlayWindow(window_id, i) for i in range(len(OVERLAY_POS))]

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
