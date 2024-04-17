import pandas as pd
from config import CONFIG

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
        text = text.replace(CONFIG["player"][f"{lang}_name"], "<PLAYER_NAME>")
        text = text.replace(CONFIG["player"][f"{lang}_surname"], "<PLAYER_SURNAME>")
        return text

    @staticmethod
    def specify_player_variables(text, lang='en'):
        text = text.replace("<PLAYER_NAME>", CONFIG["player"][f"{lang}_name"])
        text = text.replace("<PLAYER_SURNAME>", CONFIG["player"][f"{lang}_surname"])
        return text
