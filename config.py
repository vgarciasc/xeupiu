import json
from constants import convert_birthday_to_str

CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))

if CONFIG['fullscreen']:
    CONFIG["size_window_border_top"] = 0
    CONFIG["size_window_border_bottom"] = 0
    CONFIG["size_toolbar"] = 0

VERBOSE = CONFIG["debug"]
WINDOW_TITLE = CONFIG["window_title"]

PLAYER_BIRTHDAY_JP, PLAYER_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["player"]["birthday"]["month"], CONFIG["player"]["birthday"]["day"])
SHIORI_BIRTHDAY_JP, SHIORI_BIRTHDAY_EN = convert_birthday_to_str(CONFIG["player"]["shiori_birthday"]["month"], CONFIG["player"]["shiori_birthday"]["day"])