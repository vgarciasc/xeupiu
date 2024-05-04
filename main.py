import os
import time
import traceback

import keyboard
import numpy as np
from PIL import Image
from thefuzz import fuzz

from date_ymd_overlay import YearMonthDayOverlayWindow
from date_weekday_overlay import WeekdayOverlayWindow
from notebook_database import NotebookDatabase
from selectable_rect_overlay import SELECTABLE_RECTS, SelectableRectOverlay
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
from textbox_overlay import TextboxOverlayWindow
from attribute_overlay import AttributeOverlayWindow
import translator as tr
import image_processing as imp
from text_database import TextDatabase
from name_database import NameDatabase
from poorcr import PoorCR
from config import WINDOW_TITLE, CONFIG

try:
    pcr_name = PoorCR(only_perfect=True)
    pcr_text = PoorCR(only_perfect=True)

    db_texts = TextDatabase()
    db_names = NameDatabase()
    db_notebook = NotebookDatabase()

    window_id = get_window_by_title(WINDOW_TITLE)

    OverlayWindow.create_master()
    overlay_tb = TextboxOverlayWindow(window_id)
    overlay_attrs = [AttributeOverlayWindow(window_id, i) for i in range(9)]
    overlay_dateymds = [YearMonthDayOverlayWindow(window_id, i) for i in range(3)]
    overlay_rects = [SelectableRectOverlay(window_id, i, db_notebook) for i in range(len(SELECTABLE_RECTS))]
    overlay_weekday = WeekdayOverlayWindow(window_id)

    last_translated_text_ocr = None
    last_name_ocr = None
    last_img_tb_rgb = None
    iterations_wout_textbox = 0
    history_text_ocr_lines = []
    curr_line_cache = []

    print_str_history = []

    while True:
        print_str = ""
        tik = time.perf_counter_ns()

        # Take screenshot, crop textbox
        img_ss = get_window_image(window_id,
                                  offset_x=(overlay_tb.letterbox_offset[0], overlay_tb.letterbox_offset[1]),
                                  offset_y=(overlay_tb.letterbox_offset[2], overlay_tb.letterbox_offset[3]),
                                  use_scaling=True)
        img_ss = img_ss.resize((img_ss.size[0] // overlay_tb.game_scaling,
                                img_ss.size[1] // overlay_tb.game_scaling),
                               Image.NEAREST)
        img_ss_rgb = np.array(img_ss.convert('RGB')).T

        for overlay_attr in overlay_attrs:
            overlay_attr.hide_if_not_needed(*img_ss_rgb, img_ss)
        for overlay_dateymd in overlay_dateymds:
            overlay_dateymd.hide_if_not_needed(*img_ss_rgb, img_ss)
        for overlay_rect in overlay_rects:
            overlay_rect.step(*img_ss_rgb, img_ss)
        overlay_weekday.hide_if_not_needed(*img_ss_rgb, img_ss)
        overlay_weekday.update_weekday(img_ss)

        img_tb = imp.crop_textbox_image(img_ss)
        img_tb_rgb = np.array(img_tb.convert('RGB')).T

        overlay_tb.hide_if_not_needed(*img_tb_rgb, img_tb)
        if not overlay_tb.detect_gameobj(*img_tb_rgb, img_tb):
            continue

        # Detecting text in textbox
        img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
        img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

        name_ocr = None
        if not imp.check_is_text_empty(img_tb_name):
            img_tb_name = imp.trim_text(img_tb_name)
            name_ocr = pcr_name.detect(img_tb_name, should_recalibrate=True)

        text_ocr_lines = []
        for i, img_tb_line in enumerate(img_tb_lines):
            if not imp.check_is_text_empty(img_tb_line):
                text_ocr_line = pcr_text.detect(img_tb_line, should_recalibrate=True)
                if text_ocr_line == '':
                    print_str += "Empty line detected. This should not be happening " + \
                          "(empty line should not be considered by separate_into_lines). " + \
                          "Skipping...\n"
                    continue
                text_ocr_lines.append(text_ocr_line)

        # Text has stopped printing when all texts in history are the same as the current text.
        has_text_stopped_printing = True
        for prev_text_ocr_lines in history_text_ocr_lines:
            if len(prev_text_ocr_lines) > 0 and len(text_ocr_lines) > 0:
                if prev_text_ocr_lines[-1] != text_ocr_lines[-1]:
                    has_text_stopped_printing = False
                    break

        if not curr_line_cache:
            # Cache is empty. Fill it with the current text.
            curr_line_cache = text_ocr_lines
        elif not text_ocr_lines:
            # Textbox is empty. Cache should be empty as well.
            last_name_ocr = None
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
                    if i > 0:
                        name_ocr = last_name_ocr
                    break

            if not is_scrolling:
                curr_line_cache = text_ocr_lines

        text_ocr = "".join(curr_line_cache)

        # Translation
        display_name = name_ocr
        display_text = text_ocr

        # Text is the same as the last translated text
        # if text_ocr == last_translated_text_ocr:
        #     continue

        n_matches = -1
        if tr.should_translate_text(text_ocr) and (not "?" in text_ocr) and has_text_stopped_printing:
            # Translating character name
            display_name = db_names.retrieve_translation(name_ocr)
            if display_name is None and name_ocr is not None and has_text_stopped_printing:
                display_name = tr.translate_text(name_ocr, CONFIG["translation"]["backend"])
                db_names.insert_translation(name_ocr, display_name)

            # Translating character text
            n_matches, matched_jp_text, translated_text = db_texts.retrieve_translation(
                text_ocr, char_name_en=display_name, fuzziness=90,
                is_text_jp_complete=has_text_stopped_printing)

            if n_matches == 0:
                if has_text_stopped_printing:
                    # No match found, but text has stopped printing. Translate and add to database
                    translated_text = tr.translate_text(text_ocr, CONFIG["translation"]["backend"])
                    db_texts.insert_translation(text_ocr, translated_text, char_name=display_name)
                    display_text = translated_text
            elif n_matches == 1:
                # One match found. Display it.
                display_text = translated_text
            else:
                # Multiple matches found. Display the first one.
                print(f"Multiple matches found for '{text_ocr}'. Displaying the first one.")
                display_text = translated_text

            last_translated_text_ocr = text_ocr

        # Display
        overlay_tb.update(display_text, display_name)

        # Housekeeping
        history_text_ocr_lines.append(text_ocr_lines)
        history_text_ocr_lines = history_text_ocr_lines[-CONFIG["history_size"]:]
        last_name_ocr = name_ocr if name_ocr is not None else last_name_ocr

        tok = time.perf_counter_ns()
        print_str += f"Name (detected):\t\t {name_ocr}\n"
        print_str += f"Name (displayed):\t\t {display_name}\n"
        print_str += f"Text (detected):\t\t {text_ocr}\n"
        print_str += f"Text (displayed, {n_matches}):\t {display_text}\n"
        print_str += f"[[{time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms]]\n"
        print_str += "=" * 100 + "\n"

        print_str_history.append(print_str)
        print_str_history = print_str_history[-CONFIG["print_str_history_size"]:]
        print(print_str)

        # Save images on F12
        if keyboard.is_pressed("f12"):
            print_str_history[20000] += 1
            print("F12 pressed. Saving images...")
            curr_timestamp = time.strftime("%Y%m%d_%H%M%S")
            img_ss.save(f"data/tmp/{curr_timestamp}_img_ss.png")
            img_tb.save(f"data/tmp/{curr_timestamp}_img_tb.png")
            img_tb_bw.save(f"data/tmp/{curr_timestamp}_img_tb_bw.png")

            if img_tb_name:
                img_tb_name.save(f"data/tmp/{curr_timestamp}_img_tb_name.png")
            for i, img_tb_line in enumerate(img_tb_lines):
                img_tb_line.save(f"data/tmp/{curr_timestamp}_img_tb_line_{i}.png")

except Exception as e:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(f"data/log/{timestamp}", exist_ok=True)

    with open(f"data/log/{timestamp}/error.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())

    with open(f"data/log/{timestamp}/log.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(print_str_history))

    if img_ss is not None:
        img_ss.save(f"data/log/{timestamp}/img_ss.png")

    if img_tb is not None:
        img_tb.save(f"data/log/{timestamp}/img_tb.png")
