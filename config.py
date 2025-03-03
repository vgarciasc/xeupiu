import json
from constants import convert_birthday_to_str
from ctypes import windll

RES_SCALE_FACTOR = windll.shcore.GetScaleFactorForDevice(0) / 100

class Configuration():
    def __init__(self):
        self.reload()

    def reload(self):
        self.config = json.load(open('config.json', 'r', encoding='utf-8'))
        self.reload_birthdays()

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()

    def save(self):
        json.dump(self.config, open('config.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

    def get_borders_var(self):
        if self.config["fullscreen"]:
            return {
                "size_window_border_top": 0,
                "size_window_border_bottom": 0,
                "size_toolbar": 0,
                "left_offset_correction": 0
            }
        else:
            borders = self.config["border_size"]
            return {
                "size_window_border_top": round(borders["size_window_border_top"] * RES_SCALE_FACTOR),
                "size_window_border_bottom": round(borders["size_window_border_bottom"] * RES_SCALE_FACTOR),
                "size_toolbar": round(borders["size_toolbar"] * RES_SCALE_FACTOR),
                "left_offset_correction": round(borders["left_offset_correction"] * RES_SCALE_FACTOR)
            }

    def reload_birthdays(self):
        self.plbday_jp, self.plbday_en = convert_birthday_to_str(self.config["save"]["player"]["birth_month"],
                                                                 self.config["save"]["player"]["birth_day"])
        self.shbday_jp, self.shbday_en = convert_birthday_to_str(self.config["save"]["shiori"]["birth_month"],
                                                                 self.config["save"]["shiori"]["birth_day"])


CONFIG = Configuration()

if __name__ == "__main__":
    print(CONFIG['translation']['deepl']['api_key'])
