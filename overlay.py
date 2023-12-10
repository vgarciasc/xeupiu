import time
import tkinter as tk
from ctypes import windll
import win32gui

from screenshot import get_window_by_title, get_window_image

bg_img = None

class OverlayWindow:
    """ A semi-transparent window that displays text on top of the game window. """

    def __init__(self, window_id: int):
        global bg_img

        self.is_hidden = False

        windll.user32.SetProcessDPIAware()
        left, top, right, bot = win32gui.GetWindowRect(window_id)
        width, height = right - left, bot - top
        pos_x, pos_y = left, top

        self.window_id = window_id
        self.game_scaling = width // 320
        self.font_size = max(self.game_scaling * 6, 24)

        # Set the window size and position it at the bottom center
        self.textbox_width = int(260 * self.game_scaling)
        self.textbox_height = int(50 * self.game_scaling)
        self.pos_x = pos_x + (33 * self.game_scaling)
        self.pos_y = pos_y + int(168 * self.game_scaling) + 61  # 61 is the height of the taskbar

        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)
        bg_img = tk.PhotoImage(file="data/emerald_bg_4x.png")
        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="asdf", font=("MS PGothic", self.font_size), fg='white',
                              wraplength=self.textbox_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()

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
