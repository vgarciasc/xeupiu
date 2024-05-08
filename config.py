import json

CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))
VERBOSE = CONFIG["debug"]
WINDOW_TITLE = CONFIG["window_title"]