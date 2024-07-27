TB_POS_X = 30
TB_POS_Y = 168
TB_WIDTH = 11 + (11 + 3) * 18 - 3
TB_HEIGHT = 11 + (11 + 5) * 2 + 6

CURSOR_WIDTH = 15
JAP_DIGITS_INT2STR = {"0": "０", "1": "１", "2": "２", "3": "３", "4": "４", "5": "５", "6": "６", "7": "７", "8": "８", "9": "９"}
JAP_DIGITS_STR2INT = {"０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8", "９": "9"}

def convert_jp_str_to_int(str):
    return int(''.join([JAP_DIGITS_STR2INT[c] for c in str]))

def convert_birthday_to_str(month, day):
    birthday_jp_str = ""
    for digit in str(month):
        birthday_jp_str += JAP_DIGITS_INT2STR[digit]
    birthday_jp_str += "月"
    for digit in str(day):
        birthday_jp_str += JAP_DIGITS_INT2STR[digit]
    birthday_jp_str += "日"

    if day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"

    birthday_en_str = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month - 1]
    birthday_en_str += f" {day}{suffix}"

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