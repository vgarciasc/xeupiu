import time
import pandas as pd
import numpy as np
from PIL import Image
from config import CONFIG, save_config_to_json
from constants import convert_jp_str_to_int
from image_processing import get_count_by_equality, convert_to_black_and_white, extract_characters
from confession_subtitle_overlay import ConfessionSubtitleOverlay
from overlay import OverlayWindow
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from confession_database import ConfessionDatabase

CHARACTER_CUES = [
    ("Ayako", (156, 33, 20, 20), (164, 164, 206), 87)
]

def detect_confession(img_ss_rgb: np.ndarray) -> bool:
    return get_count_by_equality(*img_ss_rgb, 269, 10, 20, 20, 107, 107, 99) == 45

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
        self.subtitle_overlay = ConfessionSubtitleOverlay(window_id)

    def detect(self, img_ss_rgb: np.ndarray) -> None:
        if detect_confession(img_ss_rgb):
            character = detect_confession_character(img_ss_rgb)
            if character is not None:
                self.subtitle_overlay.show()
                self.start_confession(character)
        else:
            self.subtitle_overlay.hide()

    def start_confession(self, character: str):
        script = self.db.retrieve_confession_script(character)
        for i, row in script.iterrows():
            if row["Character"] == "<PLAYER_NAME>":
                tik = time.perf_counter()
                self.display_text_subtitle(row["Text"], color='grey')
                tok = time.perf_counter()
                time_elapsed = tok - tik
                time.sleep(max(0, row["Duration"] - time_elapsed))
            else:
                tik = time.perf_counter()
                self.subtitle_overlay.update(row["Text"], color='white')
                tok = time.perf_counter()
                time_elapsed = tok - tik
                time.sleep(max(0, row["Duration"] - time_elapsed))

        self.subtitle_overlay.hide()

    def display_text_subtitle(self, text: str, speed : float = 1, color: str = 'white'):
        for i, _ in enumerate(text):
            self.subtitle_overlay.update(text[:i+1], color=color)
            time.sleep(0.05 * 1/speed)
        self.subtitle_overlay.update(text)



if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    ch = ConfessionHandler(window_id)
    overlay = ch.subtitle_overlay

    print("Starting confession handler...")

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(overlay.letterbox_offset[0], overlay.letterbox_offset[1]),
                                  offset_y=(overlay.letterbox_offset[2], overlay.letterbox_offset[3]),
                                  use_scaling=False)

        img_ss = img_ss.resize((img_ss.size[0] // overlay.game_scaling,
                                img_ss.size[1] // overlay.game_scaling),
                               Image.NEAREST)

        img_ss_rgb = np.array(img_ss.convert('RGB')).T

        ch.detect(img_ss_rgb)



