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
    text = mocr(img_tb)

    img_ss.save("data/tmp_window.png")
    img_tb.save("data/tmp_text.png")