import time

import numpy as np
import pandas as pd
from PIL import Image

from thefuzz import fuzz
from manga_ocr import MangaOcr
from screenshot import get_window_by_title
from overlay import OverlayWindow
import translator as tr
import image_processing as imp
import database as db
from poorcr import PoorCR

def save_everything(img_ss, img_tb, img_tb_bw, lines):
    img_ss.save("data/tmp_window.png")
    img_tb.save("data/tmp_text.png")
    img_tb_bw.save("data/tmp_text_bw.png")
    for i, line in enumerate(lines):
        line.save(f"data/tmp_line_{i}.png")


window = OverlayWindow(670, 480)
df_text = db.get_text_database()
df_names = db.get_names_database()

textbox_offset = None
history_size = 10
history_text_ocr_lines = []
iters_w_same_text = 0
translation_requests = 0

pcr = PoorCR(only_perfect=True)

curr_line_cache = []
for iter in range(10000):
    print("--------------------")

    tik = time.perf_counter_ns()
    img_ss = get_window_by_title("gameplay_emerald")
    img_ss = img_ss.resize((img_ss.size[0] // 2, img_ss.size[1] // 2), Image.NEAREST)
    img_tb = img_ss.crop((30, 178, 30 + 254, 178 + 48))

    img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

    text_ocr_lines = []
    for i, img_tb_line in enumerate(img_tb_lines):
        if not imp.check_is_text_empty(img_tb_line):
            text_ocr_line = pcr.detect(img_tb_line)
            text_ocr_lines.append(text_ocr_line)

    text_ocr_name = None
    if not imp.check_is_text_empty(img_tb_name):
        text_ocr_name = pcr.detect(img_tb_name)

    if not text_ocr_lines:
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
    display_char_name = None
    display_text = "".join(curr_line_cache)

    if "?" in display_text:
        save_everything(img_ss, img_tb, img_tb_bw, img_tb_lines)
        print(f"Text was '{display_text}'")
        print("Exiting...")
        break

    should_translate = False
    if tr.should_translate_text(display_text) and should_translate:
        display_char_name = db.retrieve_translated_name(df_names, text_ocr_name)
        if display_char_name is None and has_text_stopped_printing:
            display_char_name = tr.translate_text(text_ocr_name, "google_cloud")
            df_names = db.add_translated_name(df_names, text_ocr_name, display_char_name)

        n_matches, matched_jp_text, translated_text = db.retrieve_translated_text(
            df_text, display_text, char_name_en=display_char_name, fuzziness=90,
            is_text_jp_complete=has_text_stopped_printing)

        print(f"name OCR: {text_ocr_name}")
        print(f"char_name: {display_char_name}")
        print(f"text OCR: {display_text}")
        print(f"matched_jp_text: {matched_jp_text}")
        print(f"translated text: {translated_text}")
        print(f"n_matches for this text: {n_matches}")

        if n_matches == 0:
            if has_text_stopped_printing:
                translated_text = tr.translate_text(display_text, "google_cloud")
                df_text = db.add_translated_text(df_text, display_text, translated_text, char_name=display_char_name)
                display_text = translated_text
            else:
                # Show 'display_text' (current japanese text)
                pass
        elif n_matches == 1:
            if has_text_stopped_printing:
                display_text = translated_text
            else:
                len_display_text = len(display_text)
                len_matched_text = len(matched_jp_text)
                n_characters_remain = len_matched_text - len_display_text

                if n_characters_remain > 0:
                    display_text = translated_text[:-n_characters_remain] + " " * n_characters_remain

    # Display
    window.update(display_text, display_char_name)

    # Housekeeping
    tok = time.perf_counter_ns()
    print(f"#{iter} ; {time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms ; \n{display_text}")
