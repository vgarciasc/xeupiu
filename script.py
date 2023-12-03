import numpy as np
from PIL import Image

import image_processing as ip
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image

import os

if __name__ == "__main__":
    # Delete everything inside data/tmp
    for filename in os.listdir("data/tmp"):
        os.remove(f"data/tmp/{filename}")

    # Taking screenshot
    window_id = get_window_by_title("Tokimeki Memorial")
    img_ss = get_window_image(window_id)
    scaling = img_ss.size[0] // 320
    img_ss.save("data/tmp/ss.png")

    # Cropping textbox
    img_ss = img_ss.resize((img_ss.size[0] // scaling, img_ss.size[1] // scaling), Image.NEAREST)
    img_tb = img_ss.crop((30, 172, 30 + 254, 172 + 54))

    img_cs = img_tb.crop((245, 27, 254, 48))
    red, green, blue = np.array(img_cs.convert('RGB')).T
    cursor_is_there = np.any((blue > 140) & (red < 100))
    if cursor_is_there:
        img_tb = img_tb.crop((0, 0, 245, 48))

    img_tb.save("data/tmp/text.png")

    # Converting textbox to black and white
    img_tb_bw = ip.convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_bw.save("data/tmp/text_bw.png")

    # Separating into lines
    img_name, img_tb_lines = ip.separate_into_lines(img_tb_bw)
    for i, img_tb_line in enumerate(img_tb_lines):
        if not ip.check_is_text_empty(img_tb_line):
            img_tb_line.save(f"data/tmp/line_{i}.png")

    if img_name:
        img_name.save(f"data/tmp/name.png")

    # Extracting characters

    if img_name:
        pcr_name = PoorCR(only_perfect=True)
        text = pcr_name.detect(img_name)
        print('name', text)

    pcr_text = PoorCR(only_perfect=True)
    for i, img_tb_line in enumerate(img_tb_lines):
        img_tb_line_np = np.array(img_tb_line.convert('1'))
        char_imgs = ip.extract_characters(img_tb_line_np)

        chars = []
        for char_img in char_imgs:
            char_img.save(f"data/tmp/char_{i}_{len(chars)}.png")
            chars.append(np.array(char_img.convert('1')).astype(np.int32))

        text = pcr_text.detect(img_tb_line)
        print(i, text)
