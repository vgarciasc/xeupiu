import pandas as pd
from config import CONFIG, PLAYER_BIRTHDAY_JP, SHIORI_BIRTHDAY_JP, PLAYER_BIRTHDAY_EN, SHIORI_BIRTHDAY_EN

class Database:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath, sep=";")

    def retrieve_translation(self, **kwargs):
        pass

    def insert_translation(self, **kwargs):
        pass

    @staticmethod
    def generalize_dates(text):

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
        text = text.replace("><", "> <")

        text = text.replace(PLAYER_BIRTHDAY_JP, "<PLAYER_BIRTHDAY>")
        text = text.replace(SHIORI_BIRTHDAY_JP, "<SHIORI_BIRTHDAY>")

        return text

    @staticmethod
    def specify_player_variables(text):
        config = CONFIG["save"]["player"]

        text = text.replace("<PNAME>", config["en_name"])
        text = text.replace("<PSURNAME>", config["en_surname"])
        text = text.replace("<PNICKNAME>", config["en_nickname"])

        text = text.replace("<PLAYER_BIRTHDAY>", PLAYER_BIRTHDAY_EN)
        text = text.replace("<SHIORI_BIRTHDAY>", SHIORI_BIRTHDAY_EN)

        return text
