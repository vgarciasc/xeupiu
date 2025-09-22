import pandas as pd
import re
from xeupiu.config import CONFIG
from xeupiu.constants import convert_damage_jp2en, convert_date_jp2en

class Database:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath, sep=";")

    def retrieve_translation(self, **kwargs):
        pass

    def insert_translation(self, **kwargs):
        pass

    @staticmethod
    def generalize_string(text):
        if text is None:
            return

        text = Database.generalize_player_variables(text)
        text, jp_date = Database.generalize_date(text)
        text, jp_damage = Database.generalize_damage(text)
        return text, {"date": jp_date, "damage": jp_damage}

    @staticmethod
    def specify_string(text, metadata):
        if text is None:
            return

        text = Database.specify_player_variables(text)
        text = Database.specify_date(text, convert_date_jp2en(metadata["date"]))
        text = Database.specify_damage(text, convert_damage_jp2en(metadata["damage"]))
        return text


    @staticmethod
    def generalize_player_variables(text):
        config = CONFIG["save"]["player"]

        text = text.replace(config["jp_nickname"], "<PNICKNAME>")
        text = text.replace(config["jp_name"], "<PNAME>")
        text = text.replace(config["jp_surname"], "<PSURNAME>")
        text = text.replace(config["jp_nickname_ascii"], "<PNICKNAME>")
        text = text.replace(config["jp_name_ascii"], "<PNAME>")
        text = text.replace(config["jp_surname_ascii"], "<PSURNAME>")
        text = text.replace("<PSURNAME><PNAME>", "<PNAME> <PSURNAME>")

        text = text.replace(CONFIG.plbday_jp, "<PLAYER_BIRTHDAY>")
        text = text.replace(CONFIG.shbday_jp, "<SHIORI_BIRTHDAY>")

        return text

    @staticmethod
    def specify_player_variables(text):
        config = CONFIG["save"]["player"]

        text = text.replace("<PNAME>", config["en_name"])
        text = text.replace("<PSURNAME>", config["en_surname"])
        text = text.replace("<PNICKNAME>", config["en_nickname"])

        text = text.replace("<PLAYER_BIRTHDAY>", CONFIG.plbday_en)
        text = text.replace("<SHIORI_BIRTHDAY>", CONFIG.shbday_en)

        return text

    @staticmethod
    def generalize_date(text):
        date = re.search(r"[０１２３４５６７８９]+月[０１２３４５６７８９]+日", text)

        if date:
            date = date.group()
            text = text.replace(date, "<DATE>")

        return text, date

    @staticmethod
    def specify_date(text, date_en):
        if date_en is None:
            return text

        if "<DATE>" not in text:
            return text

        return text.replace("<DATE>", date_en)

    @staticmethod
    def generalize_damage(text):
        damage = re.search(r"[０１２３４５６７８９]+のダメージ", text)

        if damage:
            damage = damage.group()
            text = text.replace(damage, "<DAMAGE>")

        return text, damage

    @staticmethod
    def specify_damage(text, damage_en):
        if damage_en is None:
            return text

        if "<DAMAGE>" not in text:
            return text

        return text.replace("<DAMAGE>", damage_en)

if __name__ == "__main__":
    text = "『７月２３日に、近所の公園へ行かない？"
    text, date = Database.generalize_date(text)
    print(text, date)

    text = "『に、近所の公園へ行かない？"
    text, date = Database.generalize_date(text)
    print(text, date)