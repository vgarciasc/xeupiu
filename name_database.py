import pandas as pd
from thefuzz import fuzz

from database import Database
from constants import DB_NAMES_FILEPATH


class NameDatabase(Database):
    def __init__(self):
        super().__init__(DB_NAMES_FILEPATH)

    def retrieve_translation(self, char_name_jp: str):
        char_name_jp = char_name_jp.strip()

        if char_name_jp is None:
            return None

        df = self.df[self.df["Japanese name"] == char_name_jp]

        if len(df) == 0:
            return None

        result = df.iloc[0]
        eng_text = result["English name"]

        return eng_text

    def insert_translation(self, name_jp: str, name_en: str):
        self.df = pd.concat([self.df, pd.DataFrame({"Japanese name": [name_jp.strip()],
                                                    "English name": [name_en.strip()]})])
        self.df.to_csv(self.filepath, sep=";", index=False)

if __name__ == "__main__":
    name_db = NameDatabase()

    txt_jp = "謎の女"
    txt = name_db.retrieve_translation(txt_jp)
    print(txt)