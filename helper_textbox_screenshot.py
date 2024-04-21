import numpy as np
from PIL import Image

from config import WINDOW_TITLE
from overlay import OverlayWindow
from screenshot import get_window_by_title, get_window_image
from textbox_overlay import TextboxOverlayWindow
import image_processing as imp

if __name__ == "__main__":
    window_id = get_window_by_title(WINDOW_TITLE)

    OverlayWindow.create_master()
    overlay_tb = TextboxOverlayWindow(window_id)

    img_ss = get_window_image(window_id,
                              offset_x=(overlay_tb.letterbox_offset[0], overlay_tb.letterbox_offset[1]),
                              offset_y=(overlay_tb.letterbox_offset[2], overlay_tb.letterbox_offset[3]),
                              use_scaling=True)
    img_ss = img_ss.resize((img_ss.size[0] // overlay_tb.game_scaling,
                            img_ss.size[1] // overlay_tb.game_scaling),
                           Image.NEAREST)
    img_ss_rgb = np.array(img_ss.convert('RGB')).T

    img_tb = imp.crop_textbox_image(img_ss)

    # Detecting text in textbox
    img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

    # save everything
    img_ss.save("data/tmp/img_ss.png")
    img_tb.save("data/tmp/img_tb.png")
    img_tb_bw.save("data/tmp/img_tb_bw.png")

    if img_tb_name:
        img_tb_name.save("data/tmp/img_tb_name.png")

    for i, img_tb_line in enumerate(img_tb_lines):
        img_tb_line.save(f"data/tmp/img_tb_line_{i}.png")