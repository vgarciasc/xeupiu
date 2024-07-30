TB_POS_X = 30
TB_POS_Y = 168
TB_WIDTH = 11 + (11 + 3) * 18 - 3
TB_HEIGHT = 11 + (11 + 5) * 2 + 6

CURSOR_WIDTH = 15
JAP_DIGITS_INT2STR = {"0": "０", "1": "１", "2": "２", "3": "３", "4": "４", "5": "５", "6": "６", "7": "７", "8": "８",
                      "9": "９"}
JAP_DIGITS_STR2INT = {"０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8",
                      "９": "9"}
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"]


def convert_jp_str_to_int(str):
    return int(''.join([JAP_DIGITS_STR2INT[c] for c in str]))


def convert_jp_date_to_int(date_jp: str):
    """ Expects strings in format '７月２３日'."""
    if "月" not in date_jp or "日" not in date_jp:
        return None, None

    date_jp = date_jp[:-1].split("月")
    return convert_jp_str_to_int(date_jp[0]), convert_jp_str_to_int(date_jp[1])

def convert_date_to_jp_str(month, day):
    birthday_jp_str = ""
    for digit in str(month):
        birthday_jp_str += JAP_DIGITS_INT2STR[digit]
    birthday_jp_str += "月"
    for digit in str(day):
        birthday_jp_str += JAP_DIGITS_INT2STR[digit]
    birthday_jp_str += "日"

    return birthday_jp_str


def convert_date_to_en_str(month, day):
    if day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"

    return f"{MONTHS_EN[month - 1]} {day}{suffix}"


def convert_date_jp2en(date_jp: str):
    if date_jp is None:
        return None

    return convert_date_to_en_str(*convert_jp_date_to_int(date_jp))


def convert_birthday_to_str(month, day):
    return (convert_date_to_jp_str(month, day),
            convert_date_to_en_str(month, day))


def convert_damage_jp2en(damage_jp: str):
    """
    :param damage_jp: Damage string in the format ８８のダメージ
    :return: damage string in english
    """

    if damage_jp is None or not "のダメージ" in damage_jp:
        return None

    damage_en = damage_jp[:-len("のダメージ")]
    return f"{convert_jp_str_to_int(damage_en)} damage"


def format_translated_text(jp_text, eng_text):
    eng_text = eng_text.replace("``", "\"")
    eng_text = eng_text.replace("''", "\"")

    if jp_text[0] == "（":
        eng_text = eng_text.replace("\"", "").replace("(", "").replace(")", "").replace("（", "").replace("）", "")
        eng_text = "(" + eng_text + ")"
    elif jp_text[0] == "「" or jp_text[0] == "『":
        eng_text = eng_text.replace("\"", "")
        eng_text = "\"" + eng_text + "\""
    return eng_text


def is_str_empty(str):
    return str.isspace() or not str
