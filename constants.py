TB_POS_X = 32
TB_POS_Y = 166
TB_WIDTH = 11 + (11 + 3) * 18 - 2
TB_HEIGHT = 11 + (11 + 5) * 2 + 8

SIZE_WINDOW_BORDER_TOP = 37
SIZE_WINDOW_BORDER_BOTTOM = 27
SIZE_TOOLBAR = 26
CURSOR_WIDTH = 15

HISTORY_SIZE = 15
ITERS_WOUT_GAMEOBJ_BEFORE_MINIMIZING = 1

WINDOW_TITLE = "Tokimeki Memorial"

DB_NAMES_FILEPATH = "data/database_names.csv"
DB_TEXT_FILEPATH = "data/database_text.csv"
DB_NOTEBOOK_FILEPATH = "data/database_notebook.csv"


def is_str_empty(str):
    return str.isspace() or not str