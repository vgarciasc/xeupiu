import json
from constants import convert_birthday_to_str

CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))

if CONFIG['fullscreen']:
    CONFIG["border_size"]["size_window_border_top"] = 0
    CONFIG["border_size"]["size_window_border_bottom"] = 0
    CONFIG["border_size"]["size_toolbar"] = 0
    CONFIG["border_size"]["left_offset_correction"] = 0

VERBOSE = CONFIG["debug"]
WINDOW_TITLE = CONFIG["window_title"]

PLAYER_BIRTHDAY_JP, PLAYER_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["save"]["player"]["birth_month"],
                                                                 CONFIG["save"]["player"]["birth_day"])
SHIORI_BIRTHDAY_JP, SHIORI_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["save"]["shiori"]["birth_month"],
                                                                 CONFIG["save"]["shiori"]["birth_day"])

def save_config_to_json(config):
    global CONFIG
    CONFIG = config

    json.dump(config, open('config.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
