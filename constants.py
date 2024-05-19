TB_POS_X = 30
TB_POS_Y = 168
TB_WIDTH = 11 + (11 + 3) * 18 - 3
TB_HEIGHT = 11 + (11 + 5) * 2 + 6

CURSOR_WIDTH = 15
JAP_DIGITS = {"0": "０", "1": "１", "2": "２", "3": "３", "4": "４", "5": "５", "6": "６", "7": "７", "8": "８", "9": "９"}

def convert_birthday_to_str(month, day):
    birthday_jp_str = ""
    for digit in str(month):
        birthday_jp_str += JAP_DIGITS[digit]
    birthday_jp_str += "月"
    for digit in str(day):
        birthday_jp_str += JAP_DIGITS[digit]
    birthday_jp_str += "日"

    birthday_en_str = ["January", "February", "March", "April", "May", "June",
                          "July", "September", "October", "November", "December"][month - 1]
    birthday_en_str += f" {day}"

    return birthday_jp_str, birthday_en_str


def format_translated_text(jp_text, eng_text):
    if jp_text[0] == "（":
        eng_text = eng_text.replace("\"", "").replace("(", "").replace(")", "")
        eng_text = "(" + eng_text + ")"
    elif jp_text[0] == "「" or jp_text[0] == "『":
        eng_text = eng_text.replace("\"", "")
        eng_text = "\"" + eng_text + "\""
    return eng_text

def is_str_empty(str):
    return str.isspace() or not str