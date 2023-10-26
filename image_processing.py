import numpy as np
from PIL import Image

def convert_emerald_textbox_to_black_and_white(img_tb):
    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    bg_pixels = (red < 70) & (blue < 70)
    img_tb_np[..., :-1][bg_pixels.T] = (0, 0, 0)
    img_tb_np[..., :-1] = 255 - img_tb_np[..., :-1]
    return Image.fromarray(img_tb_np)