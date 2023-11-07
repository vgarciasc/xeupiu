import numpy as np
from PIL import Image

def convert_emerald_textbox_to_black_and_white(img_tb):
    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    bg_pixels = (red > 100) & (blue > 100) & (green > 100)
    img_tb_np[..., :-1] = (255, 255, 255)
    img_tb_np[..., :-1][bg_pixels.T] = (0, 0, 0)
    return Image.fromarray(img_tb_np)

def separate_into_lines(img_tb):
    # A region in the textbox. If this region is blank, the left area
    # of the textbox is being used to display the character's name
    divider_line = img_tb.crop((44, 0, 49, 52))
    divider_line_np = np.array(divider_line.convert('RGBA'))
    red, green, blue, alpha = divider_line_np.T
    is_divider_line_there = np.all(red == 255) and np.all(green == 255) and np.all(blue == 255)

    _x, _y = 0, 0

    img_name = None
    if is_divider_line_there:
        img_name = img_tb.crop((0, 0, 44, 17))
        _x = 55

    img_text = img_tb.crop((_x, 0, 196, 52))
    red, green, blue = np.array(img_text.convert('RGB')).T
    black_pts_y = np.where(red != 255)[1]

    img_lines = []
    if len(black_pts_y) > 0:
        _y = np.min(black_pts_y) - 5
        for i in range(3):
            if _y + 35*(i+1) > 105:
                break
            img_line = img_tb.crop((_x, _y + 35*i, 196, _y + 35*(i+1)))
            img_lines.append(img_line)

    return img_name, img_lines

def trim_text(img_tb):
    if img_tb is None:
        return None

    red, green, blue = np.array(img_tb.convert('RGB')).T

    if np.all(red == 255):
        return img_tb

    leftmost_black = np.min(np.where(red != 255)[0])
    rightmost_black = np.max(np.where(red != 255)[0])
    img_tb_trim = img_tb.crop((leftmost_black - 5, 0, rightmost_black + 10, 35))

    return img_tb_trim

def trim_char(img_char_bw_np):
    img_char_bw_np = img_char_bw_np[:, np.min(np.where(np.mean(img_char_bw_np, axis=0) < 1)):]
    img_char_bw_np = img_char_bw_np[:, :np.max(np.where(np.mean(img_char_bw_np, axis=0) < 1)) + 1]
    img_char_bw_np = img_char_bw_np[np.min(np.where(np.mean(img_char_bw_np, axis=1) < 1)):, :]
    img_char_bw_np = img_char_bw_np[:np.max(np.where(np.mean(img_char_bw_np, axis=1) < 1)) + 1, :]
    img_char_bw_np = img_char_bw_np.astype(np.int32)
    return img_char_bw_np

def check_is_text_empty(img_tb):
    if img_tb is None:
        return True

    red, green, blue = np.array(img_tb.convert('RGB')).T
    return np.all(red > 200) | np.all(green > 200) | np.all(blue > 200)

def extract_characters(img_line):
    width, height = img_line.size
    img_line = img_line.resize((width // 2, height // 2), Image.NEAREST)
    img_line_np = np.array(img_line.convert('1'))

    char_w, char_h = 11, 12
    char_start_y = 2
    char_start_x = 2
    char_padding_x = 3

    char_imgs = []
    for i in range(0, 100):
        if char_start_x + char_w + char_padding_x > img_line_np.shape[1]:
            break

        char = img_line_np[char_start_y:(char_start_y + char_h), char_start_x:(char_start_x + char_w)]
        char_img = Image.fromarray(char)
        char_start_x += char_w + char_padding_x

        char_imgs.append(char_img)

    return char_imgs


if __name__ == "__main__":
    img_tb = Image.open("data/tmp_text.png")
    img_tb_bw = convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_bw.save("data/tmp_text_bw.png")
    img_tb_bw.resize((img_tb_bw.size[0] // 2, img_tb_bw.size[1] // 2), Image.NEAREST).save("data/tmp_text_bw_half.png")

    name, img_tb_lines = separate_into_lines(img_tb_bw)
    for i, img_tb_line in enumerate(img_tb_lines):
        img_tb_line = trim_text(img_tb_line)

        if not check_is_text_empty(img_tb_line):
            img_tb_line.save(f"data/tmp_line_{i}.png")


