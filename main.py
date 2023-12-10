import time

import numpy as np
from PIL import Image
from thefuzz import fuzz
from manga_ocr import MangaOcr

from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import translator as tr
import image_processing as imp
import database as db
from poorcr import PoorCR
from logger import save_everything
from constants import *

window_id = get_window_by_title(WINDOW_TITLE)

overlay_tb = OverlayWindow(window_id)
df_text = db.get_text_database()
df_names = db.get_names_database()
pcr_name = PoorCR(only_perfect=True)
pcr_text = PoorCR(only_perfect=True)

iterations_wout_textbox = 0
history_text_ocr_lines = []
curr_line_cache = []
while True:
    # Take screenshot, crop textbox
    tik = time.perf_counter_ns()
    img_ss = get_window_image(window_id)
    img_ss = img_ss.resize((img_ss.size[0] // overlay_tb.game_scaling,
                            img_ss.size[1] // overlay_tb.game_scaling),
                           Image.NEAREST)
    img_tb = imp.crop_textbox_image(img_ss)

    # Hide textbox overlay if textbox is not there
    if imp.check_is_textbox_there(img_tb):
        iterations_wout_textbox = 0
        if overlay_tb.is_hidden:
            overlay_tb.show()
    else:
        iterations_wout_textbox += 1
        if iterations_wout_textbox > ITERS_WOUT_TEXTBOX_BEFORE_MINIMIZING:
            overlay_tb.hide()
        continue

    # Detecting text in textbox
    img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
    img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

    text_ocr_name = None
    if not imp.check_is_text_empty(img_tb_name):
        text_ocr_name = pcr_name.detect(img_tb_name)

    text_ocr_lines = []
    for i, img_tb_line in enumerate(img_tb_lines):
        if not imp.check_is_text_empty(img_tb_line):
            text_ocr_line = pcr_text.detect(img_tb_line)
            if text_ocr_line == '':
                print("Empty line detected. This should not be happening "
                      "(empty line should not be considered by separate_into_lines). "
                      "Skipping...")
                continue
            text_ocr_lines.append(text_ocr_line)
    text_ocr = "".join(curr_line_cache)

    # Text has stopped printing when all texts in history are the same as the current text.
    has_text_stopped_printing = True
    for prev_text_ocr_lines in history_text_ocr_lines:
        if len(prev_text_ocr_lines) > 0 and len(text_ocr_lines) > 0:
            if prev_text_ocr_lines[-1] != text_ocr_lines[-1]:
                has_text_stopped_printing = False
                break
    history_text_ocr_lines.append(text_ocr_lines)
    history_text_ocr_lines = history_text_ocr_lines[-HISTORY_SIZE:]

    if not curr_line_cache:
        # Cache is empty. Fill it with the current text.
        curr_line_cache = text_ocr_lines
    elif not text_ocr_lines:
        # Textbox is empty. Cache should be empty as well.
        curr_line_cache = []
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
    display_text = text_ocr

    if "?" in text_ocr:
        save_everything(img_ss, img_tb, img_tb_bw, img_tb_lines)
        print(f"Text was '{text_ocr}'")
        print("Exiting...")
        # break

    n_matches = -1
    if tr.should_translate_text(text_ocr) and (not "?" in text_ocr) and has_text_stopped_printing:
        # Translating character name
        display_char_name = db.retrieve_translated_name(df_names, text_ocr_name)
        if display_char_name is None and text_ocr_name is not None and has_text_stopped_printing:
            display_char_name = tr.translate_text(text_ocr_name, "google_cloud")
            df_names = db.add_translated_name(df_names, text_ocr_name, display_char_name)

        # Translating character text
        n_matches, matched_jp_text, translated_text = db.retrieve_translated_text(
            df_text, text_ocr, char_name_en=display_char_name, fuzziness=90,
            is_text_jp_complete=has_text_stopped_printing)

        if n_matches == 0:
            if has_text_stopped_printing:
                # No match found, but text has stopped printing. Translate and add to database
                translated_text = tr.translate_text(text_ocr, "google_cloud")
                df_text = db.add_translated_text(df_text, text_ocr, translated_text, char_name=display_char_name)
                display_text = translated_text
        elif n_matches == 1:
            # One match found. Display it.
            display_text = translated_text
        else:
            # Multiple matches found. Display the first one.
            print(f"Multiple matches found for '{text_ocr}'. Displaying the first one.")
            display_text = translated_text

    # Display
    overlay_tb.update(display_text, display_char_name)

    # Housekeeping
    tok = time.perf_counter_ns()
    print(f"Name (detected):\t\t {text_ocr_name}")
    print(f"Name (displayed):\t\t {display_char_name}")
    print(f"Text (detected):\t\t {text_ocr}")
    print(f"Text (displayed, {n_matches}):\t {display_text}")
    print(f"[[{time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms]]")
    print("=" * 100)
