import time
import tkinter as tk
from ctypes import windll

import numpy as np
import win32gui
from PIL import Image

from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow

class TextboxOverlayWindow(OverlayWindow):
    def __init__(self, window_id: int):
        super().__init__(window_id)

    def detect_gameobj(self, img_tb: Image) -> bool:
        r, g, b = np.array(img_tb.convert('RGB')).T

        emerald_bg = np.mean((r < 30) & (g > 86) & (g < 137) & (b == 0)) > 0.4
        has_highlight = np.any((r > 100) & (r < 150) & (g > 180) & (g < 200) & (b > 30))

        return emerald_bg and not has_highlight

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = TextboxOverlayWindow(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        overlay.hide()
        time.sleep(0.5)
        overlay.show()
        time.sleep(0.5)
