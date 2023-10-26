import time
from PIL import Image
import numpy as np

from manga_ocr import MangaOcr
from screenshot import get_window_by_title
from overlay import OverlayWindow

window = OverlayWindow(670, 480)
mocr = MangaOcr()

for i in range(10):
    img_ss = get_window_by_title("gameplay_emerald.mp4")
    img_tb = img_ss.crop((60, 370, 60 + 520, 370 + 105))

    img_tb_np = np.array(img_tb.convert('RGBA'))
    red, green, blue, alpha = img_tb_np.T
    bg_pixels = (red < 70) & (blue < 70)
    img_tb_np[..., :-1][bg_pixels.T] = (0, 0, 0)
    img_tb_np[..., :-1] = 255 - img_tb_np[..., :-1]
    img_tb = Image.fromarray(img_tb_np)

    img_tb.show()