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
    def generalize_player_variables(text, lang='jp'):
        text = text.replace(CONFIG["save"]["player"][f"{lang}_name"], "<PLAYER_NAME>")
        text = text.replace(CONFIG["save"]["player"][f"{lang}_surname"], "<PLAYER_SURNAME>")

        text = text.replace(PLAYER_BIRTHDAY_JP, "<PLAYER_BIRTHDAY>")
        text = text.replace(SHIORI_BIRTHDAY_JP, "<SHIORI_BIRTHDAY>")

        return text

    @staticmethod
    def specify_player_variables(text, lang='en'):
        text = text.replace("<PLAYER_NAME>", CONFIG["save"]["player"][f"{lang}_name"])
        text = text.replace("<PLAYER_SURNAME>", CONFIG["save"]["player"][f"{lang}_surname"])

        text = text.replace("<PLAYER_BIRTHDAY>", PLAYER_BIRTHDAY_EN)
        text = text.replace("<SHIORI_BIRTHDAY>", SHIORI_BIRTHDAY_EN)

        return text
