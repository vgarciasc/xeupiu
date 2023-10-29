import pandas as pd
from thefuzz import fuzz

def get_database():
    return pd.read_csv("data/database.csv", sep=";")

def fuzzy_match(row, name, fuzziness=90):
    if fuzz.ratio(row['names'], name) > fuzziness:
        return True
    else:
        return False

def retrieve_translation(df, text_jp, fuzzy=False):
    if fuzzy:
        results = df[df["Japanese text"].apply(fuzzy_match, args=(text_jp,), axis=1)]
    else:
        results = df[df["Japanese text"] == text_jp]

    if len(results) == 0:
        return None

    return results.iloc[0]["English text"]

def add_translation(df, text_jp, text_en):
    df = pd.concat([df, pd.DataFrame({"Japanese text": [text_jp], "English text": [text_en]})])
    df.to_csv("data/database.csv", sep=";", index=False)
    return df

def is_text_continuing(prev_text, curr_text):
    if prev_text is None:
        return False

    prev_text_arr = prev_text.split("\n")
    curr_text_arr = curr_text.split("\n")

    if len(prev_text_arr) == 3:
        if prev_text_arr[1] == curr_text_arr[0]:
            # Second line became first line. Text is continuing.
            return True

    return False