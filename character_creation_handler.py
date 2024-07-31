import json

import numpy as np
from PIL import Image

from config import CONFIG, save_config_to_json
from constants import convert_jp_str_to_int
from image_processing import get_count_by_equality, convert_to_black_and_white, extract_characters
from overlay import OverlayWindow
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image


def detect_character_creation_player(img_ss_rgb: np.ndarray) -> bool:
    return get_count_by_equality(*img_ss_rgb, 33, 56, 60, 123, 255, 197, 247) == 483

def detect_character_creation_shiori(img_ss_rgb: np.ndarray) -> bool:
    return get_count_by_equality(*img_ss_rgb, 33, 56, 60, 123, 255, 197, 247) == 371

class CharacterCreationHandler:
    def __init__(self, window_id: int):
        self.window_id = window_id
        self.pcr = PoorCR(padding_x=4)

    def detect(self, img_ss_rgb: np.ndarray, img_ss: Image):
        if detect_character_creation_player(img_ss_rgb):
            self.handle_character_creation_player(img_ss)

        if detect_character_creation_shiori(img_ss_rgb):
            self.handle_character_creation_shiori(img_ss)

    def handle_character_creation_player(self, img_ss: Image):
        configs = {}

        for field, (x, y, w, h) in [
            ("jp_surname", (103, 64, 103 + 45, 64 + 13)),
            ("jp_name", (159, 64, 159 + 45, 64 + 13)),
            ("jp_nickname", (103, 96, 103 + 77, 96 + 13)),
            ("birth_month", (103, 127, 103 + 29, 127 + 13)),
            ("birth_day", (151, 127, 151 + 29, 127 + 13)),
            ("blood_type", (103, 159, 103 + 29, 159 + 13))
        ]:
            img_field = img_ss.crop((x, y, w, h))
            img_field = convert_to_black_and_white(img_field, (222, 239, 239))
            configs[field] = self.pcr.detect(img_field)

        configs["birth_month"] = convert_jp_str_to_int(configs["birth_month"])
        configs["birth_day"] = convert_jp_str_to_int(configs["birth_day"])

        for entry in CONFIG["save"]["player"].keys():
            if entry in configs.keys():
                CONFIG["save"]["player"][entry] = configs[entry]

        save_config_to_json(CONFIG)
        print(f"Saved player config (Player character info).")

    def handle_character_creation_shiori(self, img_ss: Image):
        configs = {}

        for field, (x, y, w, h) in [
            ("birth_month", (103, 95, 103 + 29, 95 + 13)),
            ("birth_day", (151, 95, 151 + 29, 95 + 13)),
            ("blood_type", (103, 127, 103 + 29, 127 + 13))
        ]:
            img_field = img_ss.crop((x, y, w, h))
            img_field = convert_to_black_and_white(img_field, (222, 239, 239))
            configs[field] = self.pcr.detect(img_field)

        configs["birth_month"] = convert_jp_str_to_int(configs["birth_month"])
        configs["birth_day"] = convert_jp_str_to_int(configs["birth_day"])

        for entry in CONFIG["save"]["shiori"].keys():
            if entry in configs.keys():
                CONFIG["save"]["shiori"][entry] = configs[entry]

        save_config_to_json(CONFIG)
        print(f"Saved player config (Shiori info).")

if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    overlay = OverlayWindow(window_id)
    cch = CharacterCreationHandler(window_id)

    img_ss = get_window_image(window_id,
                              offset_x=(overlay.letterbox_offset[0], overlay.letterbox_offset[1]),
                              offset_y=(overlay.letterbox_offset[2], overlay.letterbox_offset[3]),
                              use_scaling=False)

    img_ss = img_ss.resize((img_ss.size[0] // overlay.game_scaling,
                            img_ss.size[1] // overlay.game_scaling),
                           Image.NEAREST)

    img_ss_rgb = np.array(img_ss.convert('RGB')).T

    cch.detect(img_ss_rgb, img_ss)



