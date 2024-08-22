import os
import time
import traceback
import ctypes
import keyboard
import numpy as np
import win32gui
from PIL import Image
from thefuzz import fuzz

from character_creation_handler import CharacterCreationHandler
from scrolling_epilogue_handler import ScrollingEpilogueHandler
from title_screen_overlay import TitleScreenOverlayWindow
from save_selection_overlay import SaveSelectionOverlayWindow
from confession_handler import ConfessionHandler
from constants import convert_date_jp2en
from database import Database
from date_ymd_overlay import YearMonthDayOverlayWindow
from date_weekday_overlay import WeekdayOverlayWindow
from notebook_database import NotebookDatabase
from selectable_rect_overlay import SELECTABLE_RECTS, SelectableRectOverlay, SCREEN_CUES
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
from textbox_overlay import TextboxOverlayWindow
from attribute_overlay import AttributeOverlayWindow
import translator as tr
import image_processing as imp
from text_database import TextDatabase
from name_database import NameDatabase
from poorcr import PoorCR
from config import WINDOW_TITLE, CONFIG, VERBOSE

class App:
    def __init__(self):
        try:
            self.img_ss = None
            self.img_tb = None
            self.print_str_history = []

            self.last_translated_text_ocr = None
            self.last_inserted_text_ocr = None
            self.last_name_ocr = None
            self.last_img_tb_rgb = None
            self.iterations_wout_textbox = 0
            self.history_text_ocr_lines = []
            self.curr_line_cache = []

            self.pcr_name = PoorCR(only_perfect=True)
            self.pcr_text = PoorCR(only_perfect=True)

            self.db_texts = TextDatabase()
            self.db_names = NameDatabase()
            self.db_notebook = NotebookDatabase()

            self.window_id = get_window_by_title(WINDOW_TITLE)

            OverlayWindow.create_master()
            self.overlay_tb = TextboxOverlayWindow(self.window_id)
            self.overlay_attrs = [AttributeOverlayWindow(self.window_id, i) for i in range(9)]
            self.overlay_dateymds = [YearMonthDayOverlayWindow(self.window_id, i) for i in range(3)]
            self.overlay_rects = [SelectableRectOverlay(self.window_id, i, self.db_notebook) for i in range(len(SELECTABLE_RECTS))]
            self.overlay_weekday = WeekdayOverlayWindow(self.window_id)
            self.overlay_tss = [TitleScreenOverlayWindow(self.window_id, i) for i in range(2)]
            self.overlay_sss = [SaveSelectionOverlayWindow(self.window_id, i) for i in range(4)]
            self.character_creation_handler = CharacterCreationHandler(self.window_id)
            self.confession_handler = ConfessionHandler(self.window_id)
            self.scrolling_epilogue_handler = ScrollingEpilogueHandler(self.window_id)
        except Exception as e:
            self.handle_error(e)

    def step(self):
        img_ss = None
        img_tb = None

        try:
            print_str = ""
            tik = time.perf_counter_ns()

            # Take screenshot, crop textbox
            img_ss = get_window_image(self.window_id,
                                      offset_x=self.overlay_tb.letterbox_offset[0:2],
                                      offset_y=self.overlay_tb.letterbox_offset[2:4],
                                      use_scaling=True)
            img_ss = img_ss.resize((img_ss.size[0] // self.overlay_tb.game_scaling,
                                    img_ss.size[1] // self.overlay_tb.game_scaling),
                                   Image.NEAREST)
            img_ss_rgb = np.array(img_ss.convert('RGB')).T

            self.character_creation_handler.handle(img_ss_rgb, img_ss)
            self.confession_handler.handle(img_ss_rgb)
            self.scrolling_epilogue_handler.handle(img_ss_rgb, img_ss)

            # Detecting cues for various selectable rects
            cue_dict = {}
            for cue in SCREEN_CUES:
                prerequisites_fulfilled = True
                if cue["prerequisites"]:
                    for prerequisite in cue["prerequisites"]:
                        if not cue_dict.get(prerequisite):
                            prerequisites_fulfilled = False
                            break

                if prerequisites_fulfilled:
                    if VERBOSE:
                        print(f"Inspecting cue '{cue['id']}':")
                    is_detected = cue["fn"](*img_ss_rgb)
                else:
                    is_detected = False

                cue_dict[cue["id"]] = is_detected

            # TODO: many of these can be reintegrated within the cue system, to optimize performance
            for overlay_attr in self.overlay_attrs:
                overlay_attr.hide_if_not_needed(*img_ss_rgb, img_ss)
            for overlay_dateymd in self.overlay_dateymds:
                overlay_dateymd.hide_if_not_needed(*img_ss_rgb, img_ss)
            for overlay_rect in self.overlay_rects:
                overlay_rect.step(*img_ss_rgb, img_ss, cue_dict)
            self.overlay_weekday.hide_if_not_needed(*img_ss_rgb, img_ss)
            for overlay_ts in self.overlay_tss:
                overlay_ts.hide_if_not_needed(*img_ss_rgb, img_ss)
            for overlay_ss in self.overlay_sss:
                overlay_ss.hide_if_not_needed(*img_ss_rgb, img_ss)
            self.overlay_weekday.update_weekday(img_ss)

            img_tb = imp.crop_textbox_image(img_ss)
            img_tb_rgb = np.array(img_tb.convert('RGB')).T

            self.overlay_tb.hide_if_not_needed(*img_tb_rgb, img_tb)
            if not self.overlay_tb.detect_gameobj(*img_tb_rgb, img_tb):
                return

            # Detecting text in textbox
            img_tb_bw = imp.convert_emerald_textbox_to_black_and_white(img_tb)
            img_tb_name, img_tb_lines = imp.separate_into_lines(img_tb_bw)

            name_ocr = None
            if not imp.check_is_text_empty(img_tb_name):
                img_tb_name = imp.trim_text(img_tb_name)
                name_ocr = self.pcr_name.detect(img_tb_name, should_recalibrate=True)

            text_ocr_lines = []
            for i, img_tb_line in enumerate(img_tb_lines):
                if not imp.check_is_text_empty(img_tb_line):
                    text_ocr_line = self.pcr_text.detect(img_tb_line, should_recalibrate=True)
                    if text_ocr_line == '':
                        print_str += "Empty line detected. This should not be happening " + \
                              "(empty line should not be considered by separate_into_lines). " + \
                              "Skipping...\n"
                        continue
                    text_ocr_lines.append(text_ocr_line)

            # Text has stopped printing when all texts in history are the same as the current text.
            has_text_stopped_printing = True
            for prev_text_ocr_lines in self.history_text_ocr_lines:
                if len(prev_text_ocr_lines) > 0 and len(text_ocr_lines) > 0:
                    if prev_text_ocr_lines[-1] != text_ocr_lines[-1]:
                        has_text_stopped_printing = False
                        break

            if not self.curr_line_cache:
                # Cache is empty. Fill it with the current text.
                self.curr_line_cache = text_ocr_lines
            elif not text_ocr_lines:
                # Textbox is empty. Cache should be empty as well.
                self.last_name_ocr = None
                self.curr_line_cache = []
            else:
                # Textbox is not empty, and cache is not empty.
                # Check to see if current text is a continuation of the cache.
                # If it is, then append the current text to the cache.
                is_scrolling = False

                for i, line in enumerate(self.curr_line_cache):
                    if fuzz.ratio(text_ocr_lines[0], line) > 50 or text_ocr_lines[0].startswith(line):
                        is_scrolling = True
                        self.curr_line_cache = self.curr_line_cache[:i] + text_ocr_lines
                        if i > 0:
                            name_ocr = self.last_name_ocr
                        break

                if not is_scrolling:
                    self.curr_line_cache = text_ocr_lines

            text_ocr = "".join(self.curr_line_cache)

            # Translation
            display_name = name_ocr
            display_text = text_ocr

            # Text is the same as the last translated text
            if text_ocr == self.last_translated_text_ocr:
                return

            new_text_entry = False
            n_matches = -1
            if tr.should_translate_text(text_ocr) and (not "?" in text_ocr) and has_text_stopped_printing:
                # Translating character name
                display_name = self.db_names.retrieve_translation(name_ocr)
                if display_name is None and name_ocr is not None and has_text_stopped_printing:
                    display_name = tr.translate_text(name_ocr)
                    self.db_names.insert_translation(name_ocr, display_name)

                # Translating character text
                n_matches, matched_jp_text, translated_text = self.db_texts.retrieve_translation(
                    text_ocr, char_name_en=display_name, fuzziness=90,
                    is_text_jp_complete=has_text_stopped_printing)

                if n_matches == 0:
                    if has_text_stopped_printing:
                        # No match found, but text has stopped printing. Translate and add to database
                        translated_text = tr.translate_text(text_ocr)
                        self.db_texts.insert_translation(text_ocr, translated_text, char_name=display_name)

                        _, date_jp = Database.generalize_date(text_ocr)
                        display_text = Database.generalize_player_variables(translated_text)
                        display_text = Database.specify_player_variables(display_text)
                        display_text = Database.specify_date(display_text, convert_date_jp2en(date_jp))
                        new_text_entry = True
                elif n_matches == 1:
                    # One match found. Display it.
                    display_text = translated_text
                else:
                    # Multiple matches found. Display the first one.
                    print_str += f"Multiple matches found for '{text_ocr}'. Displaying the first one.\n"
                    display_text = translated_text

                self.last_translated_text_ocr = text_ocr

            # Display
            self.overlay_tb.update(display_text, display_name, color="yellow" if new_text_entry else "white")

            # Housekeeping
            self.history_text_ocr_lines.append(text_ocr_lines)
            self.history_text_ocr_lines = self.history_text_ocr_lines[-CONFIG["history_size"]:]
            self.last_name_ocr = name_ocr if name_ocr is not None else self.last_name_ocr

            tok = time.perf_counter_ns()
            print_str += f"Name (detected):\t\t {name_ocr}\n"
            print_str += f"Name (displayed):\t\t {display_name}\n"
            print_str += f"Text (detected):\t\t {text_ocr}\n"
            print_str += f"Text (displayed, {n_matches}):\t {display_text}\n"
            print_str += f"[[{time.strftime('%H:%M:%S')} ; {(tok - tik) / 1000000:.2f} ms]]\n"
            print_str += "=" * 100 + "\n"

            self.print_str_history.append(print_str)
            self.print_str_history = self.print_str_history[-CONFIG["print_str_history_size"]:]
            print(print_str)

        except Exception as e:
            self.handle_error(e, img_ss, img_tb)

    def handle_error(self, e, img_ss=None, img_tb=None):
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"data/log/{timestamp}", exist_ok=True)

        with open(f"data/log/{timestamp}/error.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

        if self.print_str_history:
            with open(f"data/log/{timestamp}/log.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(self.print_str_history))

        if img_ss is not None:
            img_ss.save(f"data/log/{timestamp}/img_ss.png")

        if img_tb is not None:
            img_tb.save(f"data/log/{timestamp}/img_tb.png")

        ctypes.windll.user32.MessageBoxW(0,
                                         f"An error has occurred:\n\"{e}\"\n\nPlease check full log at the folder "
                                         f"named 'data/log/{timestamp}'",
                                         "Project XEUPIU - Error!", 0x40000)

        raise e

if __name__ == "__main__":
    app = App()
    while True:
        app.step()
