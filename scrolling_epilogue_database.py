import pandas as pd

from config import CONFIG
from database import Database
from notebook_database import NotebookDatabase


class ScrollingEpilogueDatabase(NotebookDatabase):
    def __init__(self):
        super().__init__(CONFIG["databases"]["epilogue_filepath"])


if __name__ == "__main__":
    conf_db = ScrollingEpilogueDatabase()

    txt = conf_db.retrieve_translation("部活―覧")
    print(txt)