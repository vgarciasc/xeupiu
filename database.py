import pandas as pd
from thefuzz import fuzz

DB_NAMES_FILEPATH = "data/database_names.csv"
DB_TEXT_FILEPATH = "data/database_text.csv"


def fuzzy_match(row: pd.Series, name: str, fuzziness: int = 90) -> bool:
    if fuzz.ratio(row['names'], name) > fuzziness:
        return True
    else:
        return False


def get_text_database() -> pd.DataFrame:
    return pd.read_csv(DB_TEXT_FILEPATH, sep=";")


def get_names_database() -> pd.DataFrame:
    return pd.read_csv(DB_NAMES_FILEPATH, sep=";")


def retrieve_translated_text(df: pd.DataFrame, text_jp: str, char_name_jp: str = None, fuzzy: bool = False):
    df = df[df["Character name"] == char_name_jp]

    if fuzzy:
        results = df[df["Japanese text"].apply(fuzzy_match, args=(text_jp,), axis=1)]
    else:
        results = df[df["Japanese text"] == text_jp]

    if len(results) == 0:
        return None

    result = results.iloc[0]
    eng_text = result["English text"]

    return eng_text


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
