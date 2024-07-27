import pandas as pd

from config import CONFIG
from database import Database


class ConfessionDatabase(Database):
    def __init__(self):
        super().__init__(CONFIG["databases"]["confession_filepath"])

    def retrieve_confession_script(self, char_name: str):
        if char_name is None:
            raise ValueError("Character name for confession is None.")

        df = self.df[self.df["Confession_ID"] == char_name].copy()

        if df.empty:
            raise ValueError(f"No confession script found for {char_name}.")

        df['Start time'] = pd.to_datetime(df['Start time'], format='%M:%S,%f')
        df['End time'] = pd.to_datetime(df['End time'], format='%M:%S,%f')
        df['Duration'] = (df['End time'] - df['Start time']).dt.total_seconds()

        return df


if __name__ == "__main__":
    conf_db = ConfessionDatabase()

    txt = conf_db.retrieve_confession_script("Ayako")
    print(txt)