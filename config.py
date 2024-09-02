import json
from constants import convert_birthday_to_str

CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))

PLAYER_BIRTHDAY_JP, PLAYER_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["save"]["player"]["birth_month"],
                                                                 CONFIG["save"]["player"]["birth_day"])
SHIORI_BIRTHDAY_JP, SHIORI_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["save"]["shiori"]["birth_month"],
                                                                 CONFIG["save"]["shiori"]["birth_day"])

SIZE_WINDOW_BORDER_TOP = CONFIG["border_size"]["size_window_border_top"]
SIZE_WINDOW_BORDER_BOTTOM = CONFIG["border_size"]["size_window_border_bottom"]
SIZE_TOOLBAR = CONFIG["border_size"]["size_toolbar"]
LEFT_OFFSET_CORRECTION = CONFIG["border_size"]["left_offset_correction"]

def update_config(config):
    global CONFIG
    CONFIG = config

    global SIZE_WINDOW_BORDER_TOP
    global SIZE_WINDOW_BORDER_BOTTOM
    global SIZE_TOOLBAR
    global LEFT_OFFSET_CORRECTION

    SIZE_WINDOW_BORDER_TOP = CONFIG["border_size"]["size_window_border_top"]
    SIZE_WINDOW_BORDER_BOTTOM = CONFIG["border_size"]["size_window_border_bottom"]
    SIZE_TOOLBAR = CONFIG["border_size"]["size_toolbar"]
    LEFT_OFFSET_CORRECTION = CONFIG["border_size"]["left_offset_correction"]

    if CONFIG['fullscreen']:
        SIZE_WINDOW_BORDER_TOP = 0
        SIZE_WINDOW_BORDER_BOTTOM = 0
        SIZE_TOOLBAR = 0
        LEFT_OFFSET_CORRECTION = 0

def save_config_to_json(config):
    global CONFIG
    CONFIG = config

    json.dump(config, open('config.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
