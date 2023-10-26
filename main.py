import time
import PIL.Image
import numpy as np

from manga_ocr import MangaOcr
from screenshot import get_window_by_title
from overlay import OverlayWindow
from image_processing import convert_emerald_textbox_to_black_and_white

window = OverlayWindow(670, 480)
mocr = MangaOcr()

for i in range(10000):
    tik = time.perf_counter_ns()
    img_ss = get_window_by_title("gameplay_emerald.mp4")
    img_tb = img_ss.crop((60, 370, 60 + 520, 370 + 105))

    img_tb_bw = convert_emerald_textbox_to_black_and_white(img_tb)

    # img_ss.save("data/tmp_window.png")
    # img_tb.save("data/tmp_text.png")
    # img_tb_bw.save("data/tmp_text_bw.png")

    line_1 = img_tb_bw.crop((110, 0,  520, 0 + 35))
    line_2 = img_tb_bw.crop((110, 35, 520, 35 + 35))
    line_3 = img_tb_bw.crop((110, 70, 520, 70 + 35))

    for line in [line_1, line_2, line_3]:
        line_np = np.array(line.convert('RGB'))
        red, green, blue = line_np.T
        if np.all(red == 255):
            continue
        rightmost_black = np.max(np.where(red != 255)[0])
        line = line.crop((0, 0, rightmost_black + 10, 35))

    text = []
    for i, line in enumerate([line_1, line_2, line_3]):
        _txt = mocr(line)
        _txt = _txt if _txt != "そういえば、" else ""
        text.append(_txt)

        # line.save(f"data/tmp_line_{i}.png")
    text = "\n".join(text)

    window.update(text)
    tok = time.perf_counter_ns()
    print(f"#{i} ; {time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms ; \n{text}")