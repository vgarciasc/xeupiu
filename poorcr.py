import numpy as np
from PIL import Image
from image_processing import extract_characters, trim_char
import glob


def load_character_db():
    char_images = {}

    for filename in glob.glob('data/characters/hiragana/*.png') + \
                    glob.glob('data/characters/other/*.png') + \
                    glob.glob('data/characters/kanji/*.png'):

        if filename.endswith('chars.png'):
            continue

        char = filename.split('/')[-1].split('.')[0].split('_')[-1]
        char_img = np.array(Image.open(filename).convert('1'))
        char_img = char_img.astype(np.int32)

        if char in char_images:
            char_images[char].append(char_img)
        else:
            char_images[char] = [char_img]

    char_db_str = []
    char_db_np = []
    for char, char_img_nps in char_images.items():
        for char_img_np in char_img_nps:
            char_db_np.append(char_img_np)
            char_db_str.append(char)

    return np.array(char_db_np), char_db_str

def get_char_match(db, test_img_np):
    if np.all(test_img_np):
        return ' ', np.zeros((11, 11))

    char_db_np, char_db_str = db

    dist = np.sum(np.abs(test_img_np - char_db_np), axis=(1, 2))
    min_char = char_db_str[np.argmin(dist)]
    min_img_np = char_db_np[np.argmin(dist)]
    min_dist = np.min(dist)

    if min_dist > 10:
        min_char = "?"
        min_img_np = np.zeros((12, 11))

    return min_char, min_img_np


def run_ocr(db, img_line_bw):
    char_imgs = extract_characters(img_line_bw)
    text = ""
    for char_img in char_imgs:
        char_img_np = np.array(char_img.convert('1'))
        char_img_np = char_img_np.astype(np.int32)

        char, _ = get_char_match(db, char_img_np)
        text += char

    text = text.replace(" ", "")
    return text


if __name__ == "__main__":
    char_db = load_character_db()

    chars = []
    img = Image.open('data/tmp_line_0.png')
    char_imgs = extract_characters(img)
    for char_img in char_imgs:
        char_img.save(f"data/tmp_char_{len(chars)}.png")
        chars.append(np.array(char_img.convert('1')).astype(np.int32))

    text = run_ocr(char_db, img)
    print(text)
