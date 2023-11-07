import numpy as np
from PIL import Image
from image_processing import extract_characters, trim_char
import glob

def load_character_db():
    char_images = {}

    for filename in glob.glob('data/characters/hiragana/*.png'):
        if filename.endswith('chars.png'):
            continue

        char = filename.split('/')[-1].split('.')[0].split('_')[-1]
        char_img = np.array(Image.open(filename).convert('1'))
        char_img = char_img.astype(np.int32)

        if char in char_images:
            char_images[char].append(char_img)
        else:
            char_images[char] = [char_img]

    return char_images

def get_char_match(db, test_img_np):
    test_img_np = trim_char(test_img_np)

    min_dist = 100000
    min_char = None
    min_img_np = None
    for char, char_img_nps in db.items():
        for char_img_np in char_img_nps:
            for row in range(11):
                # create an image where this row is duplicated
                _char_img_np = np.zeros((char_img_np.shape[0] + 1, char_img_np.shape[1]))
                _char_img_np[:row, :] = char_img_np[:row, :]
                _char_img_np[row, :] = char_img_np[row, :]
                _char_img_np[row + 1, :] = char_img_np[row, :]
                _char_img_np[row + 1:, :] = char_img_np[row:, :]
                _char_img_np = trim_char(_char_img_np)

                # if they dont have the same shape, continue
                if _char_img_np.shape != test_img_np.shape:
                    continue

                dist = np.sum(np.abs(test_img_np - _char_img_np))
                if dist < min_dist:
                    min_dist = dist
                    min_char = char
                    min_img_np = char_img_np

    if min_dist > 10:
        min_char = "?"
        min_img_np = np.zeros((12, 11))

    return min_char, min_img_np

def run_ocr(db, img_line_bw):
    char_imgs = extract_characters(img_line_bw)
    for i, char_img in enumerate(char_imgs):
        char_img.save(f"data/tmp_char_{i}.png")

    text = ""
    for char_img in char_imgs:
        char_img_np = np.array(char_img.convert('1'))
        char_img_np = char_img_np.astype(np.int32)

        char, _ = get_char_match(db, char_img_np)
        text += char

    return text

if __name__ == "__main__":
    char_db = load_character_db()

    # for filename in glob.glob('data/characters/hiragana/*.png'):
    #     if filename.endswith('chars.png'):
    #         continue
    #
    #     test_char = filename.split('/')[-1].split('.')[0].split('_')[-1]
    #     test_char_img = Image.open(filename)
    #     test_char_img_np = np.array(test_char_img.convert('1'))
    #     test_char_img_np = test_char_img_np.astype(np.int32)
    #
    #     min_char, min_img_np = get_char_match(char_db, test_char_img_np)
    #
    #     if min_char != test_char:
    #         raise Exception(f"test_char: {test_char} | min_char: {min_char}")
    #
    # print(f"Passed all tests.")

    chars = []
    img = Image.open('data/tmp_line_2.png')
    char_imgs = extract_characters(img)
    char_imgs[-1].save("data/tmp_char.png")
    # foo = np.array(char_imgs[-1].convert('1')).astype(np.int32)
    # txt = get_char_match(char_db, foo)
    # print(txt[0])

    # text = run_ocr(char_db, img)
    # print(text)
