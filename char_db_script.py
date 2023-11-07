import numpy as np
from PIL import Image

hiragana = [
    "あ", "い", "う", "え", "お",
    "か", "き", "く", "け", "こ",
    "さ", "し", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "な", "に", "ぬ", "ね", "の",
    "は", "ひ", "ふ", "へ", "ほ",
    "ま", "み", "む", "め", "も",
    "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ",
    "わ", "を", "ん",
    "ぁ", "ぃ", "ぅ", "ぇ", "ぉ",
    "つ", "ゃ", "ゅ", "ょ", "ー",
    "が", "ぎ", "ぐ", "げ", "ご",
    "ざ", "じ", "ず", "ぜ", "ぞ",
    "だ", "ぢ", "づ", "で", "ど",
    "ば", "び", "ぶ", "べ", "ぼ",
    "ぱ", "ぴ", "ぷ", "ぺ", "ぽ",
]

cheatsheet = hiragana

if __name__ == "__main__":
    filename = "hiragana"

    # img = Image.open(f'data/characters/{filename}.png')
    # img_chars = img.crop((76, 137, 76 + 540, 137 + 208))
    #
    # img_chars_np = np.array(img_chars.convert('RGB'))
    # red, green, blue = img_chars_np.T
    # white_pts = (red > 200) & (green > 200) & (blue > 200)
    #
    # img_chars_np[...] = (255, 255, 255)
    # img_chars_np[...][white_pts.T] = (0, 0, 0)
    # img_chars = Image.fromarray(img_chars_np)
    #
    # width, height = img_chars.size
    # img_chars = img_chars.resize((width // 2, height // 2), Image.NEAREST)

    img_chars = Image.open(f'data/characters/hiragana/hiragana_chars.png')

    offset_x, offset_y = 2, 1
    char_size_x, char_size_y = 11, 11
    padding_x, padding_y = 5, 5

    _offset_x = offset_x
    _offset_y = offset_y
    curr_char = 0
    for row in range(0, 6):
        for col in range(0, 17):
            img_char = img_chars.crop((_offset_x, _offset_y, _offset_x + char_size_x, _offset_y + char_size_y))
            _offset_x += char_size_x + padding_x

            red, green, blue = np.array(img_char.convert('RGB')).T
            white_pts = (red > 200) & (green > 200) & (blue > 200)
            if np.all(white_pts):
                continue

            char = cheatsheet[curr_char]
            img_char.save(f"data/characters/{filename}/{filename}_{row}-{col}_{char}.png")
            curr_char += 1

        _offset_y += char_size_y + padding_y + (row + 1) % 2
        _offset_x = offset_x

    img_chars.save(f"data/characters/{filename}/{filename}_chars.png")

