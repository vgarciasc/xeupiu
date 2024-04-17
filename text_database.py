import pandas as pd
from thefuzz import fuzz

import database
from config import CONFIG
from database import Database
from constants import DB_TEXT_FILEPATH

class TextDatabase(Database):
    def __init__(self):
        super().__init__(DB_TEXT_FILEPATH)

    def retrieve_translation(self, text_jp: str, char_name_en: str = None,
                             fuzziness: int = 100, is_text_jp_complete: bool = True):

        char_name_en = char_name_en.strip() if char_name_en is not None else None
        if char_name_en == CONFIG["player"]["en_name"]:
            char_name_en = "<PLAYER_NAME>"

        text_jp = Database.generalize_player_variables(text_jp.strip())
        df = self.df.copy()

        if not is_text_jp_complete and len(text_jp) < 5:
            return 0, None, None

        if char_name_en is not None:
            df = df[df["Character name"] == char_name_en]

        if is_text_jp_complete:
            if fuzziness == 100:
                results = df[df["Japanese text"] == text_jp]
            else:
                results = df[df.apply(lambda row: fuzz.ratio(row['Japanese text'], text_jp) > fuzziness, axis=1)]
        else:
            txt_len = len(text_jp)
            if fuzziness == 100:
                results = df[df["Japanese text"].str[:txt_len] == text_jp]
            else:
                results = df[
                    df.apply(lambda row: fuzz.ratio(row['Japanese text'][:txt_len], text_jp) > fuzziness, axis=1)]

        n_matches = len(results)

        if n_matches == 0:
            return 0, None, None

        result = results.iloc[0]
        jp_text = result["Japanese text"]
        eng_text = result["English text"]
        eng_text = Database.specify_player_variables(eng_text)

        return n_matches, jp_text, eng_text

    def insert_translation(self, text_jp: str, text_en: str, char_name: str = "none"):
        char_name = char_name.strip() if char_name is not None else "none"
        if char_name == CONFIG["player"]["en_name"]:
            char_name = "<PLAYER_NAME>"

        text_jp = Database.generalize_player_variables(text_jp.strip())
        text_en = Database.generalize_player_variables(text_en.strip())

        self.df = pd.concat([self.df, pd.DataFrame({"Character name": [char_name],
                                                    "Japanese text": [text_jp],
                                                    "English text": [text_en]})])
        self.df.to_csv(self.filepath, sep=";", index=False)

if __name__ == "__main__":
    name_db = TextDatabase()

    txt_jp = "「あなた、ＰＬＡＹＥＲね。"
    char_en = "Yuina"

    txt = name_db.retrieve_translation(txt_jp, char_en)
    print(txt)