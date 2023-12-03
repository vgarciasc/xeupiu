import numpy as np
from PIL import Image


def convert_emerald_textbox_to_black_and_white(img_tb):
    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    bg_pixels = (red > 150) & (blue > 150) & (green > 150)
    img_tb_np[..., :-1] = (255, 255, 255)
    img_tb_np[..., :-1][bg_pixels.T] = (0, 0, 0)
    return Image.fromarray(img_tb_np)


def separate_into_lines(img_tb):
    # If image is entirely white, return
    if np.all(np.array(img_tb.convert('1')) == 1):
        return None, []

    # A region in the textbox. If this region is blank, the left area
    # of the textbox is being used to display the character's name
    divider_line = img_tb.crop((44, 0, 49, img_tb.height))
    divider_line_np = np.array(divider_line.convert('RGBA'))
    red, green, blue, alpha = divider_line_np.T
    is_divider_line_there = np.all(red == 255) and np.all(green == 255) and np.all(blue == 255)

    _x, _y = 0, 0

    img_name = None
    if is_divider_line_there:
        img_name = img_tb.crop((0, 0, 42, 16))
        _x = 43

    img_text = img_tb.crop((_x, 0, img_tb.width, img_tb.height))
    red, green, blue = np.array(img_text.convert('RGB')).T
    black_pts_y = np.where(red != 255)[1]

    img_lines = []
    if len(black_pts_y) > 0:
        _y = np.min(black_pts_y) - 1
        for i in range(3):
            if _y + 16 * (i + 1) > 52:
                break
            img_line = img_tb.crop((_x, _y + 16 * i, img_tb.width, _y + 16 * (i + 1) - 2))
            img_lines.append(img_line)

    return img_name, img_lines


def trim_text(img_tb, offset_x=1, offset_y=1):
    if img_tb is None:
        return None

    red, green, blue = np.array(img_tb.convert('RGB')).T

    if np.all(red == 255):
        return img_tb

    leftmost_black = np.min(np.where(red != 255)[0])
    rightmost_black = np.max(np.where(red != 255)[0])
    topmost_black = np.min(np.where((red != 255).T)[0])
    bottommost_black = np.max(np.where((red != 255).T)[0])

    img_tb_trim = img_tb.crop((max(leftmost_black - offset_x, 0),
                               max(topmost_black - offset_y, 0),
                               rightmost_black + offset_x,
                               bottommost_black + offset_y))

    return img_tb_trim


def trim_char(img_char_bw_np):
    img_char_bw_np = img_char_bw_np[:, np.min(np.where(np.mean(img_char_bw_np, axis=0) < 1)):]
    img_char_bw_np = img_char_bw_np[:, :np.max(np.where(np.mean(img_char_bw_np, axis=0) < 1)) + 1]
    img_char_bw_np = img_char_bw_np[np.min(np.where(np.mean(img_char_bw_np, axis=1) < 1)):, :]
    img_char_bw_np = img_char_bw_np[:np.max(np.where(np.mean(img_char_bw_np, axis=1) < 1)) + 1, :]
    img_char_bw_np = img_char_bw_np.astype(np.int32)
    return img_char_bw_np


def pad_char(img_char_bw_np):
    return np.pad(img_char_bw_np, ((0, 11 - img_char_bw_np.shape[0]),
                                   (0, 11 - img_char_bw_np.shape[1])),
                  'constant', constant_values=1)


def check_is_text_empty(img_tb):
    if img_tb is None:
        return True

    red, green, blue = np.array(img_tb.convert('RGB')).T
    return np.all(red > 200) | np.all(green > 200) | np.all(blue > 200)


def extract_characters(img_line_np):
    # img_line_np = np.array(img_line.convert('1'))

    char_w, char_h = 11, 11
    offset_y = 1
    offset_x = 1
    padding_x = 3

    char_imgs = []
    for i in range(0, 100):
        if offset_x + char_w > img_line_np.shape[1] or offset_y + char_h > img_line_np.shape[0]:
            break

        char = img_line_np[offset_y:(offset_y + char_h), offset_x:(offset_x + char_w)]
        char_img = Image.fromarray(char)
        offset_x += char_w + padding_x

        char_imgs.append(char_img)

    return char_imgs


if __name__ == "__main__":
    img_ss = Image.open("data/tmp.png")
    img_ss = img_ss.resize((img_ss.size[0] // 2, img_ss.size[1] // 2), Image.NEAREST)

    img_tb = img_ss.crop((30, 176, 30 + 254, 176 + 48))

    img_cs = img_tb.crop((245, 27, 254, 48))
    red, green, blue = np.array(img_cs.convert('RGB')).T
    cursor_is_there = np.any((blue > 140) & (red < 100))

    if cursor_is_there:
        img_tb = img_tb.crop((0, 0, 245, 48))

    img_tb.save("data/tmp_text.png")

    img_tb_bw = convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_bw.save("data/tmp_text_bw.png")

    img_name, img_tb_lines = separate_into_lines(img_tb_bw)
    img_name.save(f"data/tmp_name.png")
    for i, img_tb_line in enumerate(img_tb_lines):
        # img_tb_line = trim_text(img_tb_line)

        if not check_is_text_empty(img_tb_line):
            img_tb_line.save(f"data/tmp_line_{i}.png")
