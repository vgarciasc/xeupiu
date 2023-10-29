import time
import pandas as pd

from thefuzz import fuzz
from manga_ocr import MangaOcr
from screenshot import get_window_by_title
from overlay import OverlayWindow
import translator as tr
import image_processing as imp
import database as db


def save_everything(img_ss, img_tb, img_tb_bw, lines):
    img_ss.save("data/tmp_window.png")
    img_tb.save("data/tmp_text.png")
    img_tb_bw.save("data/tmp_text_bw.png")
    for i, line in enumerate(lines):
        line.save(f"data/tmp_line_{i}.png")


window = OverlayWindow(670, 480)
df = db.get_database()
mocr = MangaOcr()

history_size = 3
history_text_ocr_lines = []
iters_w_same_text = 0
openai_requests = 0

curr_line_cache = []
for iter in range(10000):
    print("--------------------")
    _mid_scroll = False

    tik = time.perf_counter_ns()
    img_ss = get_window_by_title("gameplay_emerald.mp4")
    img_tb = img_ss.crop((60, 370, 60 + 520, 370 + 105))

    img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

    img_tb_name = imp.trim_text(img_tb_name)
    if not imp.check_is_text_empty(img_tb_name):
        text_ocr_name = mocr(img_tb_name)

    text_ocr_lines = []
    for i, img_tb_line in enumerate(img_tb_lines):
        img_tb_line = imp.trim_text(img_tb_line)

        if not imp.check_is_text_empty(img_tb_line):
            text_ocr_line = mocr(img_tb_line)
            text_ocr_lines.append(text_ocr_line)

            if text_ocr_line == "そういえば、":
                # save_everything(img_ss, img_tb, img_tb_bw, img_tb_lines)
                # raise Exception("Text was empty.")
                _mid_scroll = True
                break

    if _mid_scroll:
        continue

    # Text has stopped printing when all texts in history are the same
    # as the current text.
    has_text_stopped_printing = True
    for prev_text_ocr_lines in history_text_ocr_lines:
        if len(prev_text_ocr_lines) > 0 and len(text_ocr_lines) > 0:
            if prev_text_ocr_lines[-1] != text_ocr_lines[-1]:
                has_text_stopped_printing = False
                break
    history_text_ocr_lines.append(text_ocr_lines)
    history_text_ocr_lines = history_text_ocr_lines[-history_size:]

    if not curr_line_cache:
        # Cache is empty. Fill it with the current text.
        curr_line_cache = text_ocr_lines
    elif not text_ocr_lines:
        # Textbox is empty. Cache should be empty as well.
        curr_line_cache = text_ocr_lines
    else:
        # Textbox is not empty, and cache is not empty.
        # Check to see if current text is a continuation of the cache.
        # If it is, then append the current text to the cache.
        is_scrolling = False
        for i, line in enumerate(curr_line_cache):
            if fuzz.ratio(text_ocr_lines[0], line) > 50 or text_ocr_lines[0].startswith(line):
                is_scrolling = True
                curr_line_cache = curr_line_cache[:i] + text_ocr_lines
                break

        if not is_scrolling:
            curr_line_cache = text_ocr_lines

    # Translation
    display_text = "".join(curr_line_cache)
    if has_text_stopped_printing and tr.should_translate_text(display_text):
        # display_text = "Translated:\n" + display_text
        print(f"Translating: {display_text}")
        translated_text = db.retrieve_translation(df, display_text)
        if translated_text is None:
            openai_requests += 1
            print(f"Sending to OpenAI... # of requests already sent: {openai_requests}")
            translated_text = tr.translate_jpn2eng(display_text)
            df = db.add_translation(df, display_text, translated_text)
        else:
            print(f"Found translation in database: {translated_text}")
        display_text = translated_text

    # Display
    window.update(display_text)

    # Housekeeping
    tok = time.perf_counter_ns()
    print(f"#{iter} ; {time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms ; \n{display_text}")
