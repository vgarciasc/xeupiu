import numpy as np
from PIL import Image
from image_processing import extract_characters, trim_char, pad_char
import glob


class PoorCR:
    """
    PoorCR stands for "Poor Man's Character Recognition". It is a simple OCR that uses a database of characters
    to detect text in images. We can do this for the textboxes because the font is always the same (MS Gothic 11x11).
    """
    def __init__(self, only_perfect=False):
        self.only_perfect = only_perfect

        self.calibration = None
        self.load_character_db()

    def detect(self, img_line_bw, is_calibrating=False):
        """
        Detects text in a line of text.
        :param img_line_bw: Image of a line of text in black and white.
        :param is_calibrating: Whether this detection is part of an OCR calibration or not. Leave as 'False' if unsure.
        :return: The text detected in the line.
        """

        img_line_bw_np = np.array(img_line_bw.convert('1'))
        if not is_calibrating:
            img_line_bw_np = self.apply_calibration(img_line_bw_np)

        char_imgs = extract_characters(img_line_bw_np)
        text = ""
        for char_img in char_imgs:
            char_img_np = np.array(char_img.convert('1'))
            char_img_np = char_img_np.astype(np.int32)

            char, _ = self.get_char_match(char_img_np)
            text += char
        text = text.replace(" ", "")

        if "?" in text:
            if is_calibrating:
                return text
            else:
                img_line_bw_np = np.array(img_line_bw.convert('1'))
                self.calibrate(img_line_bw_np)
                return self.detect(img_line_bw, is_calibrating=True)

        return text

    def get_char_match(self, test_img_np):
        """
        Gets the closest character match for a given image. This is done by comparing the image with the database
        images and returning the closest one.

        :param test_img_np: Image to compare with the database, in a 'np.array' format.
        :return: The closest character match, and its image.
        """

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

    # TODO: should try to calibrate every time a '?' is found
    def calibrate(self, img_line_bw_np):
        """
        Calibrates the OCR by finding the offset of the text in the image. This is done by padding the image with
        white pixels and checking if the OCR detects text in the padded image. If it does, then the offset is the
        padding size. If it doesn't, then the calibration tries to find the offset by cropping the image and checking
        if the OCR detects text in the cropped image. If it does, then the offset is the negative of the crop size.
        If no calibration works, then the offset is set to (0, 0).

        :param img_line_bw_np: Image of a line of text in black and white, in a 'np.array' format.
        :return: None.
        """

        for pad_x in range(0, 5):
            for pad_y in range(0, 5):
                _img = Image.fromarray(np.pad(img_line_bw_np, ((pad_x, 0), (pad_y, 0)),
                                              mode='constant', constant_values=1))
                text = self.detect(_img, is_calibrating=True)

                if not "?" in text and text != '':
                    self.calibration = (pad_x, pad_y)
                    return

        for off_x in range(0, img_line_bw_np.shape[1] - 11):
            for off_y in range(0, img_line_bw_np.shape[0] - 11):
                _img = Image.fromarray(img_line_bw_np).crop((off_x, off_y,
                                                             img_line_bw_np.shape[1],
                                                             img_line_bw_np.shape[0]))
                text = self.detect(_img, is_calibrating=True)

                if not "?" in text and text != '':
                    self.calibration = (-off_x, -off_y)
                    return

        self.calibration = (0, 0)

    def load_character_db(self):
        """
        Loads the character database from the 'data/characters' folder. This is done by loading all the images
        in the folder and turning them into a giant tensor.

        :return: A tensor of all the characters in the database, and a string array of the characters' strings.
        """
        char_images = {}

        for filename in glob.glob('data/characters/hiragana/*.png') + \
                        glob.glob('data/characters/katakana/*.png') + \
                        glob.glob('data/characters/others_1/*.png') + \
                        glob.glob('data/characters/others_2/*.png') + \
                        glob.glob('data/characters/kanji_ingame/*.png') + \
                        glob.glob('data/characters/kanji_gameplay/*.png') + \
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

    def apply_calibration(self, img_line_bw_np):
        """
        Applies the calibration to an image. This is done by padding the image with white pixels and cropping it
        according to the class's current calibration.

        :param img_line_bw_np: Image of a line of text in black and white, in a 'np.array' format.
        :return: The calibrated image.
        """

        if self.calibration == (0, 0) or self.calibration is None:
            return img_line_bw_np

        img_line_bw_np = np.pad(img_line_bw_np, ((max(self.calibration[0], 0), 0),
                                                 (max(self.calibration[1], 0), 0)),
                                'constant', constant_values=1)

        img_line_bw_np = img_line_bw_np[max(- self.calibration[1], 0):, max(- self.calibration[0], 0):]

        return img_line_bw_np


if __name__ == "__main__":
    pcr = PoorCR(only_perfect=True)

    img = Image.open('data/tmp_line_2.png')
    img_np = np.array(img.convert('1'))
    char_imgs = extract_characters(img_np)

    chars = []
    for char_img in char_imgs:
        char_img.save(f"data/tmp_char_{len(chars)}.png")
        chars.append(np.array(char_img.convert('1')).astype(np.int32))

    text = pcr.detect(img)
    print(text)
