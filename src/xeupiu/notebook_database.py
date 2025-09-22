import pandas as pd
from xeupiu.database import Database
from xeupiu.config import CONFIG

class NotebookDatabase(Database):
    def __init__(self, filepath=CONFIG["databases"]["notebook_filepath"]):
        super().__init__(filepath)

    def retrieve_translation(self, notebook_item_jp: str):
        notebook_item_jp, str_metadata = self.generalize_string(notebook_item_jp.strip())

        if notebook_item_jp is None:
            return None

        df = self.df[self.df["Japanese text"] == notebook_item_jp]

        if len(df) == 0:
            return None

        result = df.iloc[0]
        eng_text = result["English text"]
        eng_text = self.specify_string(eng_text, str_metadata)

        return eng_text

    def insert_translation(self, text_jp: str, text_en: str):
        text_jp, _ = self.generalize_string(text_jp.strip())
        text_en = text_en.replace("\"", "")

        new_df = pd.DataFrame({"Japanese text": [text_jp.strip()], "English text": [text_en.strip()]})
        self.df = pd.concat([self.df, new_df])
        self.df.to_csv(self.filepath, sep=";", index=False)

        print(f"Adding new notebook item: [{text_jp} ; {text_en}]")

if __name__ == "__main__":
    name_db = NotebookDatabase()

    txt_jp = "foo"

    txt = name_db.retrieve_translation(txt_jp)
    print(txt)