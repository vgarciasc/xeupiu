import glob

import numpy as np
from PIL import Image

from scripts.char_db_script import clean_nameselect_image
from poorcr import PoorCR

# The goal of this script is to parse the kanji from the character naming screen (screenshots/kanji_*.png) and detect
# which of the kanji are not present in our database (created with MS Gothic v2.3). The kanji that are not present
# will be saved in 'data/characters/mysteries' for further analysis, alongside the closest kanji found in the database.

if __name__ == "__main__":
    pcr = PoorCR(only_perfect=True)

    processed_chars = []
    for file_id in range(1, 88):
        filename = f"kanji_{file_id}"
        print(f"Processing {filename}...")

        img_bw = clean_nameselect_image(f"data/characters/screenshots/{filename}.png", True)
        img_bw.save(f"data/characters/char_tables/{filename}_bw.png")

        _offset_x, _offset_y = 2, 2
        char_size_x, char_size_y = 11, 11
        padding_x, padding_y = 5, 5
        curr_row, curr_col = 0, 0
        while True:
            img_char = img_bw.crop((_offset_x, _offset_y,
                                       _offset_x + char_size_x,
                                       _offset_y + char_size_y))
            img_char_np = np.array(img_char.convert('1'))

            red, green, blue = np.array(img_char.convert('RGB')).T
            white_pts = (red > 200) & (green > 200) & (blue > 200)

            _offset_x += char_size_x + padding_x
            curr_col += 1

            if not np.all(white_pts):
                if any(np.array_equal(img_char_np, elem) for elem in processed_chars):
                    pass
                else:
                    processed_chars.append(img_char_np)

                    match_char, match_img = pcr.get_char_match(img_char_np)
                    print(f"[{curr_row}, {curr_col}]: {match_char}")
                    if match_char == "?":
                        img_char.save(f"data/characters/mysteries/{filename}_{curr_row}-{curr_col}.png")
                    else:
                        img_char.save(f"data/characters/kanji_ingame/kanji_{match_char}.png")

            if _offset_x + char_size_x > img_bw.size[0]:
                _offset_y += char_size_y + padding_y
                _offset_x = 2
                curr_row += 1
                curr_col = 0

                if _offset_y + char_size_y > img_bw.size[1]:
                    print()
                    break

    for filename in glob.glob("data/characters/mysteries/*.png"):
        char_img = Image.open(filename)
        match_char, match_img_np = pcr.get_char_match(np.array(char_img.convert('1')))
        print(f"{filename}: {match_char}")

        # concatenate char_img and match_img
        char_img_np = np.array(char_img.convert('1'))
        _np = np.concatenate((char_img_np, np.ones((11, 2)), match_img_np), axis=1)
        _np = np.pad(_np, ((2, 2), (2, 2)), 'constant', constant_values=1)
        _img = Image.fromarray(_np * 255)
        _img = _img.resize((_img.size[0] * 2, _img.size[1] * 2), Image.NEAREST)
        f = f"{filename.replace('mysteries', 'proposals').split('.')[0]}_{match_char if match_char != '?' else 'none'}.png"
        _img.convert("L").save(f)