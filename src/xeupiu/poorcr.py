import time
import glob
import os

import numpy as np
from PIL import Image
from datetime import datetime

import xeupiu.image_processing as image_processing
from xeupiu.config import CONFIG
from xeupiu.image_processing import extract_characters, trim_char, pad_char


def load_character_db():
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
                    glob.glob('data/characters/weekdays/*.png') + \
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

    db_np = np.array(char_db_np)
    db_str = char_db_str

    return db_np, db_str


db_np, db_str = load_character_db()


class PoorCR:
    """
    PoorCR stands for "Poor Man's Character Recognition". It is a simple OCR that uses a database of characters
    to detect text in images. We can do this for the textboxes because the font is always the same (MS Gothic 11x11).
    """

    def __init__(self, only_perfect=False, padding_x=3, should_calibrate=True):
        self.only_perfect = only_perfect
        self.padding_x = padding_x

        os.makedirs("data/log", exist_ok=True)

        self.calibration_history = []
        self.should_calibrate = should_calibrate

    def detect(self, img_line_bw, should_recalibrate=False):
        """
        Detects text in a line of text.
        :param img_line_bw: Image of a line of text in black and white.
        :param is_calibrating: Whether this detection is part of an OCR calibration or not. Leave as 'False' if unsure.
        :return: The text detected in the line.
        """

        img_line_bw_np_original = np.array(img_line_bw.convert('1'))

        # Calibrate if no calibration exists
        if not self.calibration_history:
            if self.should_calibrate:
                self.calibrate(img_line_bw_np_original)
            else:
                self.calibration_history = [(0, 0)]

        for calibration in self.calibration_history:
            img_line_bw_np = self.apply_calibration(img_line_bw_np_original, calibration)
            char_imgs = extract_characters(img_line_bw_np, self.padding_x)
            text = self.char_imgs_to_text(char_imgs)
            perfect_detection = text.count("?") == 0

            if perfect_detection:
                return text.strip()

        if should_recalibrate:
            self.calibrate(img_line_bw_np_original)
            img_line_bw_np = self.apply_calibration(img_line_bw_np_original, self.calibration_history[-1])

            char_imgs = extract_characters(img_line_bw_np, self.padding_x)
            text = self.char_imgs_to_text(char_imgs)

            perfect_detection = text.count("?") == 0
            if not perfect_detection:
                self.log_error(text, img_line_bw)

        return text.strip()

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

        partitions = [200, 400, len(db_str)]
        curr_idx = 0
        for i in partitions:
            db_np_p = db_np[curr_idx:i]
            db_str_p = db_str[curr_idx:i]

            dist = np.sum(np.abs(test_img_np - db_np_p), axis=(1, 2))
            min_char = db_str_p[np.argmin(dist)]
            min_img_np = db_np_p[np.argmin(dist)]
            min_dist = np.min(dist)

            if min_dist == 0:
                return min_char, min_img_np

            curr_idx = i

        if min_dist > 1 and self.only_perfect:
            min_char = "?"
            min_img_np = np.zeros((11, 11))

        return min_char, min_img_np

    def char_imgs_to_text(self, char_imgs: list[Image.Image]):
        text = ""
        for char_img in char_imgs:
            char_img_np = np.array(char_img.convert('1'))
            char_img_np = char_img_np.astype(np.int32)

            char, _ = self.get_char_match(char_img_np)
            text += char
        return text

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

        calibration = None
        n_min_unrecognized = 99
        n_txt_length = 0

        for pad_x in range(0, 5):
            for pad_y in range(0, 5):
                _img = np.pad(img_line_bw_np, ((pad_x, pad_x), (pad_y, pad_y)), mode='constant', constant_values=1)

                char_imgs = extract_characters(_img, self.padding_x)
                text = self.char_imgs_to_text(char_imgs).strip()
                n_unrecognized = text.count("?")

                if text != '':
                    if (n_unrecognized < n_min_unrecognized) or \
                            (n_unrecognized == n_min_unrecognized and len(text) > n_txt_length):
                        n_min_unrecognized = n_unrecognized
                        n_txt_length = len(text)
                        calibration = (pad_x, pad_y)

        for off_y in range(0, 11):
            for off_x in range(0, 11):
                _img = img_line_bw_np[
                       off_x:img_line_bw_np.shape[0],
                       off_y:img_line_bw_np.shape[1]]

                char_imgs = extract_characters(_img, self.padding_x)
                text = self.char_imgs_to_text(char_imgs)
                n_unrecognized = text.count("?")

                if text != '':
                    if (n_unrecognized < n_min_unrecognized) or \
                            (n_unrecognized == n_min_unrecognized and len(text) > n_txt_length):
                        n_min_unrecognized = n_unrecognized
                        n_txt_length = len(text)
                        calibration = (-off_y, -off_x)

        self.calibration_history.append(calibration)
        self.calibration_history = self.calibration_history[-CONFIG['calibration_history_size']:]

    def apply_calibration(self, img_line_bw_np, calibration):
        """
        Applies the calibration to an image. This is done by padding the image with white pixels and cropping it
        according to the class's current calibration.

        :param img_line_bw_np: Image of a line of text in black and white, in a 'np.array' format.
        :return: The calibrated image.
        """

        if calibration == (0, 0) or calibration is None:
            return img_line_bw_np

        img_line_bw_np = np.pad(img_line_bw_np, ((max(calibration[0], 0), 0),
                                                 (max(calibration[1], 0), 0)),
                                'constant', constant_values=1)

        img_line_bw_np = img_line_bw_np[max(-calibration[1], 0):, max(-calibration[0], 0):]

        return img_line_bw_np

    def log_error(self, text, image):
        """
        Logs an error to the error log file.
        :param text: The text that was detected.
        :param image: The image that was detected.
        :return: None.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d")

        # get ID of the last .png that starts with 'timestamp'
        last_id = -1
        for filename in glob.glob(f"data/log/{timestamp}_*.png"):
            last_id = max(last_id, int(filename.split('_')[-1].split('.')[0]))
        img_id = last_id + 1

        img_filename = f"data/log/{timestamp}_{img_id}.png"
        image.save(img_filename)

        log_filename = f"data/log/{timestamp}.txt"

        # check if the last line of the log file is the same as the current text
        last_line = ""
        if os.path.exists(log_filename):
            with open(log_filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 2:
                    last_line = lines[-3].strip()
                    if last_line == f"Text: {text}":
                        return

        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"Text: {text}\n")
            f.write(f"Image: {img_filename}\n")
            f.write("-" * 50 + "\n")

        print(f"Logged missing character to {log_filename}.")


if __name__ == "__main__":
    pcr = PoorCR(only_perfect=True)

    tik = time.perf_counter_ns()
    for _ in range(100):
        for i, filename in enumerate(["data/tmp/img_tb_line_0.png"]):
            img = Image.open(filename)
            img = image_processing.trim_text(img)

            img_np = np.array(img.convert('1'))
            char_imgs = extract_characters(img_np)
            text = pcr.char_imgs_to_text(char_imgs)
            print(f"{_}: Text: {text}")
    tok = time.perf_counter_ns()

    print(f"Time: {(tok - tik) / 1000000:.2f} ms")
