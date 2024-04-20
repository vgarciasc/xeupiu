import json

CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))

WINDOW_TITLE = CONFIG["window_title"]