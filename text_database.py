import pandas as pd
from thefuzz import fuzz

from database import Database
from constants import DB_TEXT_FILEPATH

class TextDatabase(Database):
    def __init__(self):
        super().__init__(DB_TEXT_FILEPATH)

    def retrieve_translation(self, text_jp: str, char_name_en: str = None,
                             fuzziness: int = 100, is_text_jp_complete: bool = True):

        text_jp = text_jp.strip()
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

        return n_matches, jp_text, eng_text

    def insert_translation(self, text_jp: str, text_en: str, char_name: str = "none"):
        self.df = pd.concat([self.df, pd.DataFrame({"Character name": [char_name.strip()],
                                                    "Japanese text": [text_jp.strip()],
                                                    "English text": [text_en.strip()]})])
        self.df.to_csv(self.filepath, sep=";", index=False)

if __name__ == "__main__":
    name_db = TextDatabase()

    txt_jp = "「あなた、ＰＬＡＹＥＲね。"
    char_en = "Yuina"

    txt = name_db.retrieve_translation(txt_jp, char_en)
    print(txt)