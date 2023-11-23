import pandas as pd
from thefuzz import fuzz
import difflib

DB_NAMES_FILEPATH = "data/database_names.csv"
DB_TEXT_FILEPATH = "data/database_text.csv"


def fuzzy_match(row: pd.Series, name: str, fuzziness: int = 92) -> bool:
    if fuzz.ratio(row['Japanese text'], name) > fuzziness:
        return True
    else:
        return False


def get_text_database() -> pd.DataFrame:
    return pd.read_csv(DB_TEXT_FILEPATH, sep=";")


def get_names_database() -> pd.DataFrame:
    return pd.read_csv(DB_NAMES_FILEPATH, sep=";")


def retrieve_translated_text(df: pd.DataFrame, text_jp: str, char_name_en: str = None,
                             fuzziness: int = 100, is_text_jp_complete: bool = True):

    if not is_text_jp_complete and len(text_jp) < 5:
        # wait until more is revealed
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
            results = df[df.apply(lambda row: fuzz.ratio(row['Japanese text'][:txt_len], text_jp) > fuzziness, axis=1)]

    n_matches = len(results)

    if n_matches == 0:
        return 0, None, None

    result = results.iloc[0]
    jp_text = result["Japanese text"]
    eng_text = result["English text"]

    return n_matches, jp_text, eng_text


def retrieve_translated_name(df: pd.DataFrame, char_name_jp: str):
    if char_name_jp is None:
        return None

    df = df[df["Japanese name"] == char_name_jp]

    if len(df) == 0:
        return None

    result = df.iloc[0]
    eng_text = result["English name"]

    return eng_text


def add_translated_text(df: pd.DataFrame, text_jp: str, text_en: str, char_name: str = "none"):
    df = pd.concat([df, pd.DataFrame({"Character name": [char_name],
                                      "Japanese text": [text_jp],
                                      "English text": [text_en]})])
    df.to_csv(DB_TEXT_FILEPATH, sep=";", index=False)
    return df


def add_translated_name(df: pd.DataFrame, name_jp: str, name_en: str):
    df = pd.concat([df, pd.DataFrame({"Japanese name": [name_jp],
                                      "English name": [name_en]})])
    df.to_csv(DB_NAMES_FILEPATH, sep=";", index=False)
    return df


if __name__ == "__main__":
    txt_jp = "無理だと思っていた第一志望だったが、格すく合格することができた。"
    df_text = get_text_database()

    n_matches, matched_txt_jp, txt_en = retrieve_translated_text(df_text, txt_jp, fuzziness=90)
    print(f"n_matches: {n_matches}")
    print(f"matched_txt_jp: {matched_txt_jp}")
    print(f"txt_en: {txt_en}")
