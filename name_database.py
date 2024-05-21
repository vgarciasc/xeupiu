import pandas as pd
from thefuzz import fuzz

from config import CONFIG
from database import Database


class NameDatabase(Database):
    def __init__(self):
        super().__init__(CONFIG["databases"]["names_filepath"])

    def retrieve_translation(self, char_name_jp: str):
        if char_name_jp is None:
            return None

        if char_name_jp == CONFIG["save"]["player"]["jp_name"]:
            return CONFIG["save"]["player"]["en_name"]

        char_name_jp = Database.generalize_player_variables(char_name_jp.strip())

        df = self.df[self.df["Japanese name"] == char_name_jp]

        if len(df) == 0:
            return None

        result = df.iloc[0]
        eng_text = result["English name"]

        return eng_text

    def insert_translation(self, name_jp: str, name_en: str):
        name_jp = name_jp.strip()
        name_en = name_en.strip()

        self.df = pd.concat([self.df, pd.DataFrame({"Japanese name": [name_jp], "English name": [name_en]})])
        self.df.to_csv(self.filepath, sep=";", index=False)

if __name__ == "__main__":
    name_db = NameDatabase()

    txt_jp = "謎の女"
    txt = name_db.retrieve_translation(txt_jp)
    print(txt)