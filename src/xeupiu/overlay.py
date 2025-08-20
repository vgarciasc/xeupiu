import time
import tkinter as tk

import numpy as np
from PIL import Image

from xeupiu.constants import *
from xeupiu.screenshot import get_window_by_title, get_window_image, get_window_base_dims
from xeupiu.config import CONFIG, RES_SCALE_FACTOR

bg_img = None


class OverlayWindow:
    """ A semi-transparent window that displays text on top of the game window. """

    def __init__(self, window_id: int):
        self.letterbox_offset = self.get_letterbox_offset(window_id)

        pos_x, pos_y, width, height = self.get_window_dims(window_id)
        self.create_overlay(pos_x, pos_y, width, height)

        self.is_hidden = False
        self.iterations_wout_gameobj = 99

    def get_letterbox_offset(self, window_id: int, n_tries=0):
        """
        Removes black letterboxes on the sides of the game window.
        :return: The x and y offsets of the game window.
        """

        img_ss = get_window_image(window_id)
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

        if RES_SCALE_FACTOR > 1 and left_offset - right_offset <= local_game_scaling:
            # EXPERIMENTING! This is a hack to fix rounding differences between how windows does resolution scaling
            # and how the game does it. This is a hack and should be removed if it causes problems.
            print(f"Fixing off-by-one error in resolution scaling...")
            pass
        elif right_offset < left_offset:
            if n_tries < 50:
                print(f"Letterbox calibration done before window was fully rendered. Retrying...")
                print(f"Offsets: {left_offset}, {right_offset}, {top_offset}, {bottom_offset}")
                return self.get_letterbox_offset(window_id, n_tries+1)
            else:
                print(f"Letterbox calibration failed. Offsets: {left_offset}, {right_offset}, {top_offset}, {bottom_offset}")
                raise Exception("Letterbox calibration failed.")

        # EXPERIMENTING! This is a hack added because in the title screen, there is no left flicker.
        # This is solving my problems right now, but perhaps won't in the future. Keep this in mind.
        left_offset += (img_ss.width - left_offset - right_offset) % 320

        return left_offset, right_offset, top_offset, bottom_offset

    def get_window_dims(self, window_id: int) -> tuple[int, int, int, int]:
        l_offset, r_offset, t_offset, b_offset = self.letterbox_offset

        x, y, w, h = get_window_base_dims(window_id)

        border_config = CONFIG.get_borders_var()
        x += l_offset + border_config["left_offset_correction"]
        y += border_config["size_toolbar"] + border_config["size_window_border_top"] + t_offset
        w -= (l_offset + r_offset)
        h -= (border_config["size_window_border_bottom"] + border_config["size_toolbar"] + t_offset + b_offset)

        self.game_scaling = w // 320
        self.font_size = min(self.game_scaling * 6, 32)

        return x, y, w, h

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
        self.label = tk.Label(self.root, text="Loading...", font=("MS PGothic", self.font_size), fg='white',
                              wraplength=self.textbox_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        """
        Detects whether the game object to be overlayed is present in the screenshot.
        """

        return True

    def hide_if_not_needed(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> None:
        """
        Hides the overlay if it is not needed.
        """

        if self.detect_gameobj(r, g, b, img_ss):
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
        self.is_hidden = True

    def show(self):
        """
        Shows the overlay window.
        """

        if not self.is_hidden:
            return

        self.root.attributes("-alpha", 0.9)
        self.is_hidden = False

    def update(self, new_text: str, char_name: str = None, color: str = None) -> None:
        """
        Updates the text displayed on the overlay.

        :param new_text: The new text to display.
        :param char_name: The name of the character speaking the text.
        """

        if char_name:
            new_text = char_name + "\n  " + new_text + ""

        new_text = new_text.replace("\" \"", "\"\n\"")

        if color:
            self.update_color(color)

        self.label.config(text=new_text)

    def update_color(self, color: str) -> None:
        """
        Updates the color of the text displayed on the overlay.

        :param color: The new color of the text.
        """

        self.label.config(fg=color)


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
