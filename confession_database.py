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

        df['Text'] = df['Text'].str.replace("\\n", "\n")
        df['Start time'] = pd.to_datetime(df['Start time'], format='%M:%S,%f')
        df['Duration'] = (df['Start time'] - df['Start time'].shift(1)).shift(-1).dt.total_seconds()
        df.loc[df.index[-1], 'Duration'] = 7.0

        return df


if __name__ == "__main__":
    conf_db = ConfessionDatabase()

    txt = conf_db.retrieve_confession_script("Nozomi")
    print(txt)