import time
import tkinter as tk
from ctypes import windll

import numpy as np
import win32gui
from PIL import Image

from constants import *
from screenshot import get_window_by_title, get_window_image
from config import CONFIG

bg_img = None


class OverlayWindow:
    """ A semi-transparent window that displays text on top of the game window. """

    def __init__(self, window_id: int):
        self.letterbox_offset = self.get_letterbox_offset(window_id)

        pos_x, pos_y, width, height = self.get_window_dims(window_id)
        self.create_overlay(pos_x, pos_y, width, height)

        self.is_hidden = False
        self.iterations_wout_gameobj = 0

    def get_letterbox_offset(self, window_id: int):
        """
        Removes black letterboxes on the sides of the game window.
        :return: The x and y offsets of the game window.
        """

        img_ss = get_window_image(window_id, use_scaling=False)
        img_ss_np = np.array(img_ss.convert('RGBA'))

        left_offset = 0
        for r, g, b, a in img_ss_np[img_ss_np.shape[0]//2, :, :]:
            if not (r == 0 and g == 0 and b == 0):
                break
            left_offset += 1

        right_offset = 0
        for r, g, b, a in np.flip(img_ss_np, axis=1)[img_ss_np.shape[0]//2, :, :]:
            if not (r == 0 and g == 0 and b == 0):
                break
            right_offset += 1

        bottom_offset = 0
        for r, g, b, a in np.flip(img_ss_np, axis=0)[:, img_ss_np.shape[1]//2, :]:
            if not (r == 0 and g == 0 and b == 0):
                break
            bottom_offset += 1

        top_offset = 0
        for r, g, b, a in img_ss_np[:, img_ss_np.shape[1]//2, :]:
            if not (r == 0 and g == 0 and b == 0):
                break
            top_offset += 1

        local_game_scaling = round((img_ss.width - left_offset - right_offset) / 320)

        # There is a 1px black border on the left on DuckStation for some reason
        left_offset -= 1 * local_game_scaling

        # There is a *FLICKERING* 1px black border on the top on DuckStation
        if (img_ss.height - top_offset - bottom_offset) % 240 != 0 and top_offset != 0:
            top_offset -= 1 * local_game_scaling

        if right_offset - left_offset < 0:
            print(f"Letterbox calibration done before window was fully rendered. Retrying...")
            return self.get_letterbox_offset(window_id)

        return left_offset, right_offset, top_offset, bottom_offset

    def get_window_dims(self, window_id: int):
        windll.user32.SetProcessDPIAware()

        left, top, right, bot = win32gui.GetWindowRect(window_id)
        width, height = right - left, bot - top
        pos_x, pos_y = left, top

        l_offset, r_offset, t_offset, b_offset = self.letterbox_offset

        pos_x += l_offset
        pos_y += CONFIG["border_size"]["size_toolbar"] + CONFIG["border_size"]["size_window_border_top"] + t_offset
        width -= (l_offset + r_offset)
        height -= (CONFIG["border_size"]["size_toolbar"] + CONFIG["border_size"]["size_window_border_top"] + t_offset + b_offset)

        self.game_scaling = width // 320
        self.font_size = min(self.game_scaling * 6, 24)

        return pos_x, pos_y, width, height

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        global bg_img

        self.pos_x = window_pos_x + int(TB_POS_X * self.game_scaling)
        self.pos_y = window_pos_y + int(TB_POS_Y * self.game_scaling)
        self.textbox_width = int(TB_WIDTH * self.game_scaling)
        self.textbox_height = int(TB_HEIGHT * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)
        bg_img = tk.PhotoImage(file="data/backgrounds/emerald_bg_4x.png")

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="asdf", font=("MS PGothic", self.font_size), fg='white',
                              wraplength=self.textbox_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()

    def detect_gameobj(self, img_ss: Image) -> bool:
        """
        Detects whether the game object to be overlayed is present in the screenshot.
        """

        return True

    def hide_if_not_needed(self, img_ss: Image) -> None:
        """
        Hides the overlay if it is not needed.
        """

        if self.detect_gameobj(img_ss):
            self.iterations_wout_gameobj = 0
        else:
            self.iterations_wout_gameobj += 1

        if self.iterations_wout_gameobj > CONFIG["iters_without_gameobj_without_minimizing"]:
            self.hide()
        else:
            self.show()

    def hide(self):
        """
        Hides the overlay window.
        """

        if self.is_hidden:
            return

        self.root.attributes("-alpha", 0.0)
        self.root.update_idletasks()
        self.root.update()
        self.is_hidden = True

    def show(self):
        """
        Shows the overlay window.
        """

        if not self.is_hidden:
            return

        self.root.attributes("-alpha", 0.9)
        self.root.update_idletasks()
        self.root.update()
        self.is_hidden = False

    def update(self, new_text: str, char_name: str = None) -> None:
        """
        Updates the text displayed on the overlay.

        :param new_text: The new text to display.
        :param char_name: The name of the character speaking the text.
        """

        if char_name:
            new_text = char_name + "\n  " + new_text + ""

        new_text = new_text.replace("\" \"", "\"\n\"")

        self.label.config(text=new_text)
        self.root.update_idletasks()
        self.root.update()

    @staticmethod
    def create_master():
        root_tk = tk.Tk()
        root_tk.overrideredirect(True)
        root_tk.attributes("-alpha", 0.0)
        return root_tk


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")
    overlay = OverlayWindow(window_id)

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 1, None)
        time.sleep(0.5)
        overlay.hide()
        time.sleep(0.5)
        overlay.show()
        time.sleep(0.5)
