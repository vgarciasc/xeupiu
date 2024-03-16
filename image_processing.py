import numpy as np
from PIL import Image
from constants import *


def convert_emerald_textbox_to_black_and_white(img_tb):
    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    bg_pixels = ((red < 50) & (blue < 50) & (green > 50)) | ((red < 20) & (blue < 20) & (green < 20))
    img_tb_np[..., :-1] = (0, 0, 0)
    img_tb_np[..., :-1][bg_pixels.T] = (255, 255, 255)
    return Image.fromarray(img_tb_np)


def convert_notebook_to_black_and_white(img_ss):
    img_tb_np = np.array(img_ss.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    fg_pixels = ((red == 132) & (green == 132) & (blue == 164))
    img_tb_np[..., :-1] = (255, 255, 255)
    img_tb_np[..., :-1][fg_pixels.T] = (0, 0, 0)
    return Image.fromarray(img_tb_np)


def convert_weekday_to_black_and_white(img_tb):
    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    fg_pixels = (red > 90) & (blue > 90) & (green > 90)
    img_tb_np[..., :-1] = (255, 255, 255)
    img_tb_np[..., :-1][fg_pixels.T] = (0, 0, 0)
    return Image.fromarray(img_tb_np)


def separate_into_lines(img_tb):
    # If image is entirely white, return
    if np.all(np.array(img_tb.convert('1')) == 1):
        return None, []

    # A region in the textbox. If this region is blank, the left area
    # of the textbox is being used to display the character's name
    img_name = img_tb.crop((0, 0, 42, 20))
    img_name_np = np.array(img_name.convert('1'))
    is_name_there = np.any(img_name_np == 0)

    below_name = img_tb.crop((0, 17, 42, 48))
    below_name_np = np.array(below_name.convert('1'))
    is_nothing_below_name = np.all(below_name_np == 1)

    rest_textbox = img_tb.crop((47, 0, img_tb.width - 47, img_tb.height))
    rest_textbox_np = np.array(rest_textbox.convert('1'))
    is_text_in_rest_textbox = np.any(rest_textbox_np == 0)

    should_separate_name_and_text = is_name_there and is_nothing_below_name and is_text_in_rest_textbox

    _x, _y = 0, 0
    if should_separate_name_and_text:
        _x = 43
    else:
        img_name = None

    img_text = img_tb.crop((_x, 0, img_tb.width, img_tb.height))
    red, green, blue = np.array(img_text.convert('RGB')).T
    black_pts_y = np.where(red != 255)[1]

    img_lines = []
    if len(black_pts_y) > 0:
        _y = np.min(black_pts_y) - 1
        for i in range(3):
            if _y + 16 * (i + 1) > 54:
                break
            img_line = img_tb.crop((_x, _y + 16 * i, img_tb.width, _y + 16 * (i + 1) - 2))
            if not check_is_text_empty(img_line):
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

    w = rightmost_black - leftmost_black
    w = w + (14 - (w - 11) % 14)
    w = w + offset_x * 2

    h = bottommost_black - topmost_black
    h = max(h, 11 + offset_y * 2)

    x1 = max(leftmost_black - offset_x, 0)
    y1 = max(topmost_black - offset_y, 0)

    img_tb_trim = img_tb.crop((x1, y1, x1 + w, y1 + h))

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

    black = np.array(img_tb.convert('1')).T
    return np.all(black[:, :-1])


def check_is_textbox_there(img_tb):
    red, green, blue = np.array(img_tb.convert('RGB')).T
    return np.any((red < 50) & (blue < 50) & (green > 100))


def check_are_attributes_there(img_ss):
    img_attr = img_ss.crop((30, 34, 30 + 9, 34 + 36))
    red, green, blue = np.array(img_attr.convert('RGB')).T
    return np.all((red < 50) & (blue < 50) & (green > 70))


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


def crop_textbox_image(img_ss):
    img_tb = img_ss.crop((TB_POS_X, TB_POS_Y, TB_POS_X + TB_WIDTH, TB_POS_Y + TB_HEIGHT))

    img_cs = img_tb.crop((TB_WIDTH - 11, 27, TB_WIDTH, TB_HEIGHT))
    r, g, b = np.array(img_cs.convert('RGB')).T

    cursor_is_there = np.any((b > 140) & (r < 100))
    if cursor_is_there:
        img_tb = img_tb.crop((0, 0, TB_WIDTH - CURSOR_WIDTH, 48))

    return img_tb


if __name__ == "__main__":
    img_ss = Image.open("data/tmp/ss.png")
    game_scaling = img_ss.width // 320

    img_ss = img_ss.resize((img_ss.size[0] // game_scaling,
                            img_ss.size[1] // game_scaling),
                           Image.NEAREST)

    img_tb = crop_textbox_image(img_ss)
    img_tb.save("data/tmp/text.png")

    img_tb_bw = convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_bw.save("data/tmp/text_bw.png")

    img_name, img_tb_lines = separate_into_lines(img_tb_bw)
    if img_name:
        img_name.save(f"data/tmp/name.png")
    for i, img_tb_line in enumerate(img_tb_lines):
        if not check_is_text_empty(img_tb_line):
            img_tb_line.save(f"data/tmp/line_{i}.png")


