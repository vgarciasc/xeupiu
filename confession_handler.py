import time
from datetime import datetime

import pandas as pd
import numpy as np
from PIL import Image
from config import CONFIG
from constants import convert_jp_str_to_int
from image_processing import get_count_by_equality, convert_to_black_and_white, extract_characters, \
    get_count_by_thresholds
from confession_subtitle_overlay import ConfessionSubtitleOverlay
from overlay import OverlayWindow
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from confession_database import ConfessionDatabase

CHARACTER_CUES = [
    ("Ayako", (156, 33, 20, 20), (164, 164, 206), 87),
    ("Yuko", (164, 1, 13, 15), (255, 99, 132), 20),
    ("Nozomi", (211, 144, 30, 41), (164, 255, 206), 41),
    ("Yuina", (133, 3, 55, 25), (0, 41, 230), 72),
    ("Shiori", (166, 0, 21, 8), (255, 164, 164), 19),
    ("Mira", (66, 72, 13, 9), (206, 132, 255), 10),
    ("Rei", (105, 56, 24, 18), (255, 255, 164), 25),
    ("Miharu", (84, 14, 31, 26), (230, 99, 0), 87),
    ("Yumi", (106, 7, 105, 31), (107, 255, 230), 1185),
    ("Mio", (160, 26, 37, 17), (0, 99, 99), 102),
]

def detect_confession(img_ss_rgb: np.ndarray) -> bool:
    #tatebayashi's horns make it 16
    return get_count_by_equality(*img_ss_rgb, 269, 10, 20, 20, 107, 107, 99) in [45, 34]

def detect_confession_character(img_ss_rgb: np.ndarray) -> str:
    for char, coords, color, count in CHARACTER_CUES:
        if get_count_by_equality(*img_ss_rgb, *coords, *color) == count:
            return char

    print("Detected confession screen, but didn't recognize character.")
    return None

class ConfessionHandler:
    def __init__(self, window_id: int):
        self.window_id = window_id
        # self.pcr = PoorCR(padding_x=4)
        self.db = ConfessionDatabase()
        self.confession_made = False
        self.subtitle_overlay = ConfessionSubtitleOverlay(window_id)

    def handle(self, img_ss_rgb: np.ndarray) -> None:
        if detect_confession(img_ss_rgb) and not self.confession_made:
            character = detect_confession_character(img_ss_rgb)
            if character is not None:
                self.subtitle_overlay.show()
                self.start_confession(character)
        else:
            self.subtitle_overlay.hide()

    def start_confession(self, character: str):
        script = self.db.retrieve_confession_script(character)

        for i, row in script.iterrows():
            total_time_waited = 0
            if row["Character"] == "<PLAYER_NAME>":
                total_time_waited += self.display_text_subtitle(row["Text"], row['Text speed'], color='grey')
            else:
                self.subtitle_overlay.update(row["Text"], color='white')

            time.sleep(max(0, row["Duration"] - total_time_waited))

        self.confession_made = True
        self.subtitle_overlay.hide()

    def display_text_subtitle(self, text: str, speed : float = 1, color: str = 'white'):
        total_time_waited = 0
        for i, _ in enumerate(text):
            self.subtitle_overlay.update(text[:i+1], color=color)
            duration = 0.1 * 1/speed
            time.sleep(duration)
            total_time_waited += duration
        # self.subtitle_overlay.update(text, color=color)
        return total_time_waited


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    ch = ConfessionHandler(window_id)
    overlay = ch.subtitle_overlay

    print("Starting confession handler...")

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(overlay.letterbox_offset[0], overlay.letterbox_offset[1]),
                                  offset_y=(overlay.letterbox_offset[2], overlay.letterbox_offset[3]))

        img_ss = img_ss.resize((img_ss.size[0] // overlay.game_scaling,
                                img_ss.size[1] // overlay.game_scaling),
                               Image.NEAREST)

        img_ss_rgb = np.array(img_ss.convert('RGB')).T

        ch.handle(img_ss_rgb)



