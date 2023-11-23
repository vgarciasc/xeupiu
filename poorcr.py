import numpy as np
from PIL import Image
from image_processing import extract_characters, trim_char, pad_char
import glob


class PoorCR:
    def __init__(self, only_perfect=False):
        self.only_perfect = only_perfect

        self.calibration = None
        self.load_character_db()

    def detect(self, img_line_bw, is_calibrating=False):
        img_line_bw_np = np.array(img_line_bw.convert('1'))

        if self.calibration is None and not is_calibrating:
            self.calibrate(img_line_bw_np)
            print(f"Calibrated. Offset: {self.calibration}")

        if self.calibration != (0, 0) and self.calibration is not None:
            img_line_bw_np = np.pad(img_line_bw_np, ((self.calibration[0], 0),
                                                     (self.calibration[1], 0)),
                                    'constant', constant_values=1)

        char_imgs = extract_characters(img_line_bw_np)
        text = ""
        for char_img in char_imgs:
            char_img_np = np.array(char_img.convert('1'))
            char_img_np = char_img_np.astype(np.int32)

            char, _ = self.get_char_match(char_img_np)
            text += char

        text = text.replace(" ", "")
        return text

    def get_char_match(self, test_img_np):
        if np.all(test_img_np):
            return ' ', np.zeros((11, 11))

        test_img_np = trim_char(test_img_np)
        test_img_np = pad_char(test_img_np)

        dist = np.sum(np.abs(test_img_np - self.db_np), axis=(1, 2))
        min_char = self.db_str[np.argmin(dist)]
        min_img_np = self.db_np[np.argmin(dist)]
        min_dist = np.min(dist)

        if min_dist > 1 and self.only_perfect:
            min_char = "?"
            min_img_np = np.zeros((11, 11))

        return min_char, min_img_np

    #TODO: should try to calibrate every time a '?' is found
    def calibrate(self, img_line_bw_np):
        for pad_x in range(0, 10):
            for pad_y in range(0, 10):
                _img = Image.fromarray(np.pad(img_line_bw_np, ((pad_x, 0), (pad_y, 0)),
                                              mode='constant', constant_values=1))
                text = self.detect(_img, is_calibrating=True)

                if not "?" in text:
                    self.calibration = (pad_x, pad_y)
                    return

        self.calibration = (0, 0)

    def load_character_db(self):
        char_images = {}

        for filename in glob.glob('data/characters/hiragana/*.png') + \
                        glob.glob('data/characters/katakana/*.png') + \
                        glob.glob('data/characters/others_1/*.png') + \
                        glob.glob('data/characters/others_2/*.png') + \
                        glob.glob('data/characters/kanji_ingame/*.png') + \
                        glob.glob('data/characters/kanji_corrected/*.png'):

            if filename.endswith('chars.png'):
                continue

            char = filename.split('/')[-1].split('.')[0].split('_')[-1]
            char_img = Image.open(filename)
            char_img_np = np.array(char_img.convert('1')).astype(np.int32)
            char_img_np = trim_char(char_img_np)
            char_img_np = pad_char(char_img_np)

            if char in char_images:
                char_images[char].append(char_img_np)
            else:
                char_images[char] = [char_img_np]

        # turn dictionary into numpy array and string array
        char_db_str = []
        char_db_np = []
        for char, char_img_nps in char_images.items():
            for char_img_np in char_img_nps:
                char_db_np.append(char_img_np)
                char_db_str.append(char)

        self.db_np = np.array(char_db_np)
        self.db_str = char_db_str

        return self.db_np, self.db_str


if __name__ == "__main__":
    pcr = PoorCR(only_perfect=True)

    img = Image.open('data/tmp_line_0.png')
    img_np = np.array(img.convert('1'))
    char_imgs = extract_characters(img_np)

    chars = []
    for char_img in char_imgs:
        char_img.save(f"data/tmp_char_{len(chars)}.png")
        chars.append(np.array(char_img.convert('1')).astype(np.int32))

    text = pcr.detect(img)
    print(text)
