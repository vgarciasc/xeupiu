import glob
import time
import tkinter as tk

from numba import jit
import numpy as np
from PIL import Image

from translator import Translator
from constants import is_str_empty
from database import Database
from notebook_database import NotebookDatabase
from poorcr import PoorCR
from config import CONFIG
from screenshot import get_window_by_title, get_window_image, RESOLUTION_SCALE_OFFSET_Y
from overlay import OverlayWindow
from image_processing import get_count_by_equality, get_count_by_thresholds
import image_processing as imp

SELECTABLE_RECT_GROUPS = {
    "dc": {
        "fullname": "dialogue_choice",
        "textcolor": "#ffffff",
        "selected_color": "#39a930",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: np.mean((r < 30) & (g > 60) & (g < 140) & (b == 0)) > 0.5,
        "is_selected_fn": lambda r, g, b: np.mean((r > 30) & (r < 170) & (g > 150) & (b > 20) & (b < 120)) > 0.65,
    },
    "nb": {
        "fullname": "notebook",
        "textcolor": "#70779e",
        "selected_color": "#bbebbb",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (132, 132, 164)),
        "is_unselected_fn": lambda r, g, b: np.mean((r > 185) & (r < 225) & (r == g) & (r == b)) > 0.7,
        "is_selected_fn": lambda r, g, b: np.mean((g > 220) & (g < 250) & (r == b) & (r < 220)) > 0.55,
    },
    "ngp": {
        "fullname": "notebook_girl_pink",
        "textcolor": "#e600a5",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (230, 0, 164)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "ngg": {
        "fullname": "notebook_girl_grey",
        "textcolor": "#70779e",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (132, 132, 164)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "ngb": {
        "fullname": "notebook_girl_blue",
        "textcolor": "#0073ff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (0, 115, 255)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "csc": {
        "fullname": "character_selection_choice",
        "textcolor": "#ffffff",
        "selected_color": "#39a930",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: np.mean((r < 30) & (g > 60) & (g < 140) & (b == 0)) > 0.5,
        "is_selected_fn": lambda r, g, b: np.mean((r > 30) & (r < 170) & (g > 150) & (b > 20) & (b < 120)) > 0.5,
    },
    "an": {
        "fullname": "area_name",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "exr": {
        "fullname": "exam_results",
        "textcolor": "#70779e",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (132, 132, 164)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_movie": {
        "fullname": "magazine_movie",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (222, 239, 247)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_concert": {
        "fullname": "magazine_concert",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (247, 214, 239)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_event": {
        "fullname": "magazine_event",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (230, 222, 239)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_genre": {
        "fullname": "magazine_genre",
        "textcolor": "#8484a4",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (132, 132, 164)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_stadium": {
        "fullname": "magazine_stadium",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (222, 222, 230)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_info": {
        "fullname": "magazine_info",
        "textcolor": "#8484a4",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (132, 132, 164)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "mg_dspot": {
        "fullname": "magazine_date_spot",
        "textcolor": "#8484a4",
        "selected_color": None,
        "bw_conversion_fn": lambda x: None,
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "rpg_uig": {
        "fullname": "rpg_ui_grey",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "rpg_uiw": {
        "fullname": "rpg_ui_white",
        "textcolor": "#ffffff",
        "selected_color": "#631d1d",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white_multiple(x, [(247, 247, 255), (255, 189, 189)]),
        "is_unselected_fn": lambda r, g, b: not (np.mean((r > 100) & (g < 50) & (b < 50)) > 0.6),
        "is_selected_fn": lambda r, g, b: np.mean((r > 100) & (g < 170) & (b < 170)) > 0.6,
    },
    "chcr_k1": {
        "fullname": "character_creation_black1",
        "textcolor": "#0f0f0f",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (16, 16, 16)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "chcr_k2": {
        "fullname": "character_creation_black2",
        "textcolor": "#0f0f0f",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (8, 0, 0)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "chcr_g": {
        "fullname": "character_creation_grey",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "chcr_w": {
        "fullname": "character_creation_white",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (222, 239, 239)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "chcr_p": {
        "fullname": "character_creation_pink",
        "textcolor": "#ffffff",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (255, 197, 247)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "sss_k": {
        "fullname": "save_selection_screen_black",
        "textcolor": "#000000",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (8, 0, 0)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "bes": {
        "fullname": "bad_ending_song",
        "textcolor": "#a4cece",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "ngameplus": {
        "fullname": "new_game_plus",
        "textcolor": "#0f0f0f",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (8, 0, 0)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "si": {
        "fullname": "sports_instructions",
        "textcolor": "#000000",
        "selected_color": None,
        "bw_conversion_fn": None,
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    },
    "exm": {
        "fullname": "extras_menu",
        "textcolor": "#ffffff",
        "selected_color": "#ffc552",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: np.sum((r == 255) & (g == 255) & (b == 0)) < 15,
        "is_selected_fn": lambda r, g, b: np.sum((r == 255) & (g == 255) & (b == 0)) > 15,
    },
    "exb": {
        "fullname": "extras_menu_bonus",
        "textcolor": "#ffffff",
        "selected_color": "#ffc552",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white_multiple(x, [(90, 90, 90), (255, 255, 0), (247, 214, 0), (239, 197, 0), (230, 181, 0), (230, 156, 0), (222, 140, 0), (247, 214, 0), (230, 123, 0)], mode="blend"),
        "is_unselected_fn": lambda r, g, b: np.sum((r == 255) & (g == 255) & (b == 0)) < 15,
        "is_selected_fn": lambda r, g, b: np.sum((r == 255) & (g == 255) & (b == 0)) > 15,
    }
}

def detect_mark_by_count(red, green, blue, x, y, w, h, r, g, b, count):
    c = get_count_by_equality(red, green, blue, x, y, w, h, r, g, b)

    if CONFIG["verbose_level"] > 1:
        print(f"\tCount: {c}, expected: {count}")

    return c == count

def detect_mark_by_count_min(red, green, blue, x, y, w, h, r, g, b, min):
    c = get_count_by_equality(red, green, blue, x, y, w, h, r, g, b)

    if CONFIG["verbose_level"] > 1:
        print(f"\tCount: {c}, expected: greater than {min}")

    return c > min

def detect_mark_by_count_with_thresholds(red, green, blue, x, y, w, h, r_min, r_max, g_min, g_max, b_min, b_max, count):
    c = get_count_by_thresholds(red, green, blue, x, y, w, h, r_min, r_max, g_min, g_max, b_min, b_max)

    if CONFIG["verbose_level"] > 1:
        print(f"\tCount: {c}, expected: {count}")

    return c == count

def detect_mark_textbox_choice1(red, green, blue):
    is_cursor_there = detect_mark_by_count(red, green, blue, 274, 170, 6, 47, 239, 230, 239, 4)
    is_selection_there = detect_mark_by_count_with_thresholds(red, green, blue, 260, 166, 6, 54, 60, 120, 120, 180, 50, 100, 96)
    return is_cursor_there and is_selection_there

def detect_mark_textbox_choice2(red, green, blue):
    is_cursor_there = detect_mark_by_count(red, green, blue, 278, 166, 6, 47, 239, 230, 239, 4)
    is_selection_there = detect_mark_by_count_with_thresholds(red, green, blue, 276, 168, 4, 50, 60, 120, 120, 180, 50, 100, 64)
    return is_cursor_there and is_selection_there

def detect_mark_textbox_choice3(red, green, blue):
    is_selection_in_hgap_1 = detect_mark_by_count_with_thresholds(red, green, blue, 29, 183, 261, 3, 20, 105, 160, 190, 10, 100, 360)
    is_selection_in_hgap_2 = detect_mark_by_count_with_thresholds(red, green, blue, 29, 199, 261, 3, 20, 105, 160, 190, 10, 100, 360)
    is_selection_in_hgap_3 = detect_mark_by_count_with_thresholds(red, green, blue, 29, 215, 261, 3, 20, 120, 120, 190, 10, 100, 360)
    return is_selection_in_hgap_1 or is_selection_in_hgap_2 or is_selection_in_hgap_3

def detect_mark_character_selection_choice_1(red, green, blue):
    is_cursor_in_vgap_1 = detect_mark_by_count(red, green, blue, 80, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_2 = detect_mark_by_count(red, green, blue, 144, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_3 = detect_mark_by_count(red, green, blue, 208, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_4 = detect_mark_by_count(red, green, blue, 272, 170, 16, 54, 239, 230, 239, 68)

    is_selection_in_hgap_1 = 75 < get_count_by_thresholds(red, green, blue, 31, 182, 260, 4, 60, 120, 150, 210, 30, 120) < 100
    is_selection_in_hgap_2 = 75 < get_count_by_thresholds(red, green, blue, 31, 198, 260, 4, 60, 120, 150, 210, 30, 120) < 100
    is_selection_in_hgap_3 = 50 < get_count_by_thresholds(red, green, blue, 31, 214, 260, 4, 60, 120, 150, 210, 30, 120) < 100

    return (is_cursor_in_vgap_1 or is_cursor_in_vgap_2 or is_cursor_in_vgap_3 or is_cursor_in_vgap_4) and (is_selection_in_hgap_1 or is_selection_in_hgap_2 or is_selection_in_hgap_3)

def detect_mark_character_selection_choice_2(red, green, blue):
    is_players_house = detect_mark_by_count(red, green, blue, 252, 105, 29, 32, 173, 107, 82, 5)
    is_shinto_shrine = detect_mark_by_count(red, green, blue, 13, 90, 23, 27, 239, 222, 222, 64)
    is_shinto_shrine_2 = detect_mark_by_count(red, green, blue, 17, 50, 21, 24, 74, 66, 58, 30)
    is_corridor_school = detect_mark_by_count(red, green, blue, 9, 20, 50, 90, 58, 74, 66, 24)
    is_front_school = detect_mark_by_count(red, green, blue, 13, 7, 52, 127, 8, 8, 16, 17)

    is_selection_on_textbox = 30 < get_count_by_thresholds(red, green, blue, 16, 160, 280, 63, 60, 120, 160, 190, 20, 80) < 300

    return (is_players_house or is_shinto_shrine or is_shinto_shrine_2 or is_corridor_school or is_front_school) and is_selection_on_textbox

def detect_ending_game_save_menu(red, green, blue):
    cue1 = detect_mark_by_count(red, green, blue, 264, 30, 40, 40, 134, 166, 209, 65)
    cue2 = detect_mark_by_count_min(red, green, blue, 27, 166, 266, 52, 166, 209, 209, 5)
    cue3 = detect_mark_by_count_min(red, green, blue, 27, 166, 266, 52, 233, 134, 255, 5)
    return cue1 and not (cue2 or cue3)

SCREEN_CUES = [
    { "id": "textbox", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 16, 159, 288, 64, 164, 49, 25, 650), "prerequisites": []},
    { "id": "dc_3row1", "fn": detect_mark_textbox_choice1, "prerequisites": ["textbox"] },
    { "id": "dc_3row2", "fn": detect_mark_textbox_choice2, "prerequisites": ["textbox"] },
    { "id": "dc_2col1", "fn": detect_mark_textbox_choice3, "prerequisites": ["textbox"] },
    { "id": "csc_1", "fn": detect_mark_character_selection_choice_1, "prerequisites": ["textbox"] },
    { "id": "csc_2", "fn": detect_mark_character_selection_choice_2, "prerequisites": ["textbox"] },
    { "id": "nb_spiral", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,1, 91, 15, 8, 49, 49, 49, 9), "prerequisites": ["textbox"] },
    { "id": "nb_2col1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,145, 37, 7, 8, 99, 132, 164, 16), "prerequisites": ["nb_spiral"] },
    { "id": "nb_2col2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,145, 35, 7, 15, 41, 132, 164, 9), "prerequisites": ["nb_spiral"] },
    { "id": "nb_3col1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,100, 56, 9, 9, 41, 132, 164, 7), "prerequisites": ["nb_spiral"] },
    { "id": "nb_3col1_club", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,20, 35, 256, 16, 132, 132, 164, 165), "prerequisites": ["nb_3col1"] },
    { "id": "nb_3col1_club_1.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_1.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_1.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_1.4", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 112, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_1.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_2.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_2.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_2.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_2.4", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 112, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_2.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_3.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_3.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_3.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_club_3.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_club"] },
    { "id": "nb_3col1_phone", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,20, 35, 256, 16, 132, 132, 164, 209), "prerequisites": ["nb_3col1"] },
    { "id": "nb_3col1_phone_1.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_1.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_1.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_1.4", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 112, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_1.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 24, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_2.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_2.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_2.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_2.4", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 112, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_2.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 108, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_3.1", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 64, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_3.2", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 80, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_3.3", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 96, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "nb_3col1_phone_3.5", "fn": lambda r, g, b: detect_mark_by_count_min(r, g, b, 200, 128, 72, 16, 132, 132, 164, 5), "prerequisites": ["nb_3col1_phone"] },
    { "id": "ng_1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,23, 20, 8, 14, 230, 0, 164, 42), "prerequisites": ["nb_spiral"] },
    { "id": "ng_2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b,160, 21, 16, 15, 41, 164, 255, 76), "prerequisites": ["nb_spiral"] },
    { "id": "an", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 7, 16, 8, 45, 49, 0, 0, 87), "prerequisites": [] },
    { "id": "an_2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 47, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_3", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 61, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_4", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 75, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_5", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 89, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_6", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 103, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_7", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 117, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_8", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 131, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_9", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 145, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "an_10", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 159, 23, 6, 32, 49, 0, 0, 70), "prerequisites": ["an"] },
    { "id": "exr", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 82, 6, 156, 28, 49, 0, 0, 960), "prerequisites": [] },
    { "id": "exr_0", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 37, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_1", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 53, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_2", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 69, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_3", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 85, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_4", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 101, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_5", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 117, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_6", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 31, 133, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_7", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 37, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_8", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 53, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_9", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 69, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_10", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 85, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_11", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 101, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_12", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 117, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "exr_13", "fn": lambda r, g, b: not detect_mark_by_count(r, g, b, 191, 133, 90, 13, 132, 132, 164, 88), "prerequisites": ["exr"] },
    { "id": "magazine", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 6, 10, 97, 36, 255, 41, 0, 816), "prerequisites": [] },
    { "id": "mg_info", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 1, 59, 139, 13, 132, 132, 164) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_1", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 0, 230, 164) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_2", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 255, 41, 164) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_3", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 123, 189, 255) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_4", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 255, 140, 0) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_5", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 247, 132, 197) > 50, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_6", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 255, 214, 0) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_7", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 206, 156, 255) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_dspot_8", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 8, 56, 160, 24, 255, 132, 99) > 20, "prerequisites": ["magazine"] },
    { "id": "mg_event_1", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 16, 105, 225, 13, 230, 222, 239) > 10, "prerequisites": ["magazine"] },
    { "id": "mg_event_2", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 16, 121, 225, 13, 230, 222, 239) > 10, "prerequisites": ["magazine"] },
    { "id": "mg_event_3", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 11, 137, 225, 13, 230, 222, 239) > 10, "prerequisites": ["magazine"] },
    { "id": "mg_genre_m", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 240, 16, 64, 8, 132, 132, 164) > 5, "prerequisites": ["magazine"]},
    { "id": "mg_genre_m1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 16, 64, 8, 132, 132, 164, 59), "prerequisites": ["mg_genre_m"]},
    { "id": "mg_genre_m2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 16, 64, 8, 132, 132, 164, 90), "prerequisites": ["mg_genre_m"]},
    { "id": "mg_genre_m3", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 16, 64, 8, 132, 132, 164, 63), "prerequisites": ["mg_genre_m"]},
    { "id": "mg_genre_m4", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 16, 64, 8, 132, 132, 164, 37), "prerequisites": ["mg_genre_m"]},
    { "id": "mg_genre_m5", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 16, 64, 8, 132, 132, 164, 35), "prerequisites": ["mg_genre_m"]},
    { "id": "mg_genre_c", "fn": lambda r, g, b: get_count_by_equality(r, g, b, 240, 48, 64, 8, 132, 132, 164) > 5, "prerequisites": ["magazine"]},
    { "id": "mg_genre_c1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 48, 64, 8, 132, 132, 164, 64), "prerequisites": ["mg_genre_c"]},
    { "id": "mg_genre_c2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 48, 64, 8, 132, 132, 164, 49), "prerequisites": ["mg_genre_c"]},
    { "id": "mg_genre_c3", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 48, 64, 8, 132, 132, 164, 42), "prerequisites": ["mg_genre_c"]},
    { "id": "mg_genre_c4", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 240, 48, 64, 8, 132, 132, 164, 97), "prerequisites": ["mg_genre_c"]},
    { "id": "mg_stadium", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 166, 78, 75, 26, 173, 189, 189, 273), "prerequisites": ["magazine"]},
    { "id": "mg_stadium_3_1_b", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 88, 33, 15, 222, 222, 230, 113), "prerequisites": ["mg_stadium"]},
    { "id": "mg_stadium_3_1_w", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 88, 33, 15, 222, 222, 230, 75), "prerequisites": ["mg_stadium"]},
    { "id": "mg_stadium_3_2_b", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 104, 33, 15, 222, 222, 230, 113), "prerequisites": ["mg_stadium"]},
    { "id": "mg_stadium_3_2_w", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 104, 33, 15, 222, 222, 230, 75), "prerequisites": ["mg_stadium"]},
    { "id": "mg_stadium_3_3_b", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 120, 33, 15, 222, 222, 230, 113), "prerequisites": ["mg_stadium"]},
    { "id": "mg_stadium_3_3_w", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 272, 120, 33, 15, 222, 222, 230, 75), "prerequisites": ["mg_stadium"]},
    { "id": "chcr_h", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 214, 5, 40, 9, 247, 222, 247, 79), "prerequisites": []},
    { "id": "chcr_1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 22, 30, 283, 16, 255, 197, 247, 203), "prerequisites": ["chcr_h"] },
    { "id": "chcr_2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 22, 30, 283, 16, 255, 197, 247, 307), "prerequisites": ["chcr_h"] },
    { "id": "chcr_3", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 33, 56, 60, 35, 255, 197, 247, 88), "prerequisites": ["chcr_h"] },
    { "id": "chcr_4", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 33, 56, 60, 123, 255, 197, 247, 371), "prerequisites": ["chcr_h"] },
    { "id": "rpg_ui_bottom_ui", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 5, 166, 20, 20, 255, 255, 0, 44), "prerequisites": []},
    { "id": "rpg_ui_bottom_actions", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 106, 166, 20, 20, 255, 255, 0, 44), "prerequisites": ["rpg_ui_bottom_ui"]},
    { "id": "rpg_ui_top", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 14, 6, 20, 40, 255, 255, 0, 88), "prerequisites": ["rpg_ui_bottom_ui"]},
    { "id": "save_selection_screen", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 9, 209, 78, 18, 197, 189, 189, 64), "prerequisites": []},
    { "id": "save_selection_screen_load", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 98, 132, 97, 16, 0, 58, 132, 95), "prerequisites": ["save_selection_screen"]},
    { "id": "bad_ending_song", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 100, 49, 185, 136, 230, 255, 230, 2314), "prerequisites": ["not!textbox"]},
    { "id": "new_game_plus", "fn": detect_ending_game_save_menu, "prerequisites": ["not!textbox"]},
    { "id": "sports_instructions", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 0, 0, 320, 20, 99, 197, 255, 1276), "prerequisites": ["not!textbox"]},
    { "id": "sports_instructions_1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 56, 39, 213, 18, 74, 74, 74, 404), "prerequisites": ["sports_instructions"] },
    { "id": "sports_instructions_2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 56, 39, 213, 18, 74, 74, 74, 388), "prerequisites": ["sports_instructions"] },
    { "id": "sports_instructions_3", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 56, 39, 213, 18, 74, 74, 74, 501), "prerequisites": ["sports_instructions"] },
    { "id": "sports_instructions_4", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 56, 39, 213, 18, 74, 74, 74, 408), "prerequisites": ["sports_instructions"] },
    { "id": "shrine_instructions_1_1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 105, 32, 112, 17, 255, 164, 41, 151), "prerequisites": ["not!textbox"]},
    { "id": "shrine_instructions_1_2", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 104, 69, 102, 21, 255, 41, 99, 484), "prerequisites": ["not!textbox"]},
    # { "id": "extras_menu_1", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 24, 16, 128, 8, 148, 74, 0, 132), "prerequisites": []},
    # { "id": "extras_menu_bonus", "fn": lambda r, g, b: detect_mark_by_count(r, g, b, 80, 128, 128, 8, 148, 74, 0, 132), "prerequisites": []},
]

SELECTABLE_RECTS = [
    ("nb_3col1_h", (20, 35), (256, 16), "#e0e0e0", "nb_3col1_club", 1, 3, "Club list"),
    ("nb_3col1_1.1", (24, 64), (72, 16), "#e0e0e0", "nb_3col1_club_1.1", 1, 3, "Literature"),
    ("nb_3col1_1.2", (24, 80), (72, 16), "#e0e0e0", "nb_3col1_club_1.2", 1, 3, "Theatre"),
    ("nb_3col1_1.3", (24, 96), (72, 16), "#e0e0e0", "nb_3col1_club_1.3", 1, 3, "Science"),
    ("nb_3col1_1.4", (24, 112), (72, 16), "#e0e0e0", "nb_3col1_club_1.4", 1, 3, "Cyber"),
    ("nb_3col1_1.5", (24, 128), (72, 16), "#dddddd", "nb_3col1_club_1.5", 1, 3, "Art"),
    ("nb_3col1_2.1", (108, 64), (72, 16), "#e0e0e0", "nb_3col1_club_2.1", 1, 3, "Brass band"),
    ("nb_3col1_2.2", (108, 80), (72, 16), "#dedede", "nb_3col1_club_2.2", 1, 3, "Baseball"),
    ("nb_3col1_2.3", (108, 96), (72, 16), "#d8d8d8", "nb_3col1_club_2.3", 1, 3, "Soccer"),
    ("nb_3col1_2.4", (108, 112), (72, 16), "#d3d3d3", "nb_3col1_club_2.4", 1, 3, "Tennis"),
    ("nb_3col1_2.5", (108, 128), (72, 16), "#cecece", "nb_3col1_club_2.5", 1, 3, "Swimming"),
    ("nb_3col1_3.1", (200, 64), (72, 16), "#d8d8d8", "nb_3col1_club_3.1", 1, 3, "Basketball"),
    ("nb_3col1_3.5", (200, 128), (72, 16), "#c8c8c8", "nb_3col1_club_3.5", 1, 3, "Cancel"),
    ("nb_3col1_h", (20, 35), (256, 16), "#e0e0e0", "nb_3col1_phone", 1, 3, "Contacts"),
    ("nb_3col1_1.1", (24, 64), (72, 16), "#e0e0e0", "nb_3col1_phone_1.1", 1, 3, "Yoshio Saotome"),
    ("nb_3col1_1.2", (24, 80), (72, 16), "#e0e0e0", "nb_3col1_phone_1.2", 1, 3, "Shiori Fujisaki"),
    ("nb_3col1_1.3", (24, 96), (72, 16), "#e0e0e0", "nb_3col1_phone_1.3", 1, 3, "Mio Kisaragi"),
    ("nb_3col1_1.4", (24, 112), (72, 16), "#e0e0e0", "nb_3col1_phone_1.4", 1, 3, "Yuina Himoo"),
    ("nb_3col1_1.5", (24, 128), (72, 16), "#dddddd", "nb_3col1_phone_1.5", 1, 3, "Ayako Katagiri"),
    ("nb_3col1_2.1", (108, 64), (72, 16), "#e0e0e0", "nb_3col1_phone_2.1", 1, 3, "Saki Nijino"),
    ("nb_3col1_2.2", (108, 80), (72, 16), "#dedede", "nb_3col1_phone_2.2", 1, 3, "Yukari Koshiki"),
    ("nb_3col1_2.3", (108, 96), (72, 16), "#d8d8d8", "nb_3col1_phone_2.3", 1, 3, "Nozomi Kiyokawa"),
    ("nb_3col1_2.4", (108, 112), (72, 16), "#d3d3d3", "nb_3col1_phone_2.4", 1, 3, "Mira Kagami"),
    ("nb_3col1_2.5", (108, 128), (72, 16), "#cecece", "nb_3col1_phone_2.5", 1, 3, "Yuko Asahina"),
    ("nb_3col1_3.1", (200, 64), (72, 16), "#d8d8d8", "nb_3col1_phone_3.1", 1, 3, "Megumi Mikihara"),
    ("nb_3col1_3.2", (200, 80), (72, 16), "#d5d5d5", "nb_3col1_phone_3.2", 1, 3, "Yumi Saotome"),
    ("nb_3col1_3.3", (200, 96), (72, 16), "#d2d2d2", "nb_3col1_phone_3.3", 1, 3, "Rei Ijuin"),
    ("nb_3col1_3.5", (200, 128), (72, 16), "#c8c8c8", "nb_3col1_phone_3.5", 1, 3, "Cancel"),

    ("nb_2col1_1.1", (35, 55), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.2", (35, 67), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.3", (35, 79), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.4", (35, 91), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.5", (35, 103), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.6", (35, 115), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.7", (35, 127), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_1.8", (35, 139), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.1", (35, 55), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.2", (35, 67), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.3", (35, 79), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.4", (35, 91), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.5", (35, 103), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.6", (35, 115), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.7", (35, 127), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("ngp_2col1_1.8", (35, 139), (100, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_2.1", (155, 55), (111, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_2.2", (155, 71), (111, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_2.3", (155, 87), (111, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_2.4", (155, 103), (111, 13), "#e0e0e0", "nb_2col1", 1, 3),
    ("nb_2col1_2.5", (155, 119), (111, 13), "#e0e0e0", "nb_2col1", 1, 3),

    ("nb_2col2_h1", (31, 36), (98, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_h2", (158, 36), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_1.1", (23, 62), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_1.2", (23, 78), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_1.3", (23, 94), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_1.4", (23, 110), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_1.5", (23, 126), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_2.1", (158, 62), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_2.2", (158, 78), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_2.3", (158, 94), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_2.4", (158, 110), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),
    ("nb_2col2_2.5", (158, 126), (109, 15), "#e0e0e0", "nb_2col2", 1, 3),

    ("dc_3row1_1", (39, 169), (230, 17), "#135800", "dc_3row1", 1, 3),
    ("dc_3row1_2", (39, 185), (230, 17), "#135800", "dc_3row1", 1, 3),
    ("dc_3row1_3", (39, 201), (230, 17), "#135800", "dc_3row1", 1, 3),

    ("dc_3row2_1", (32, 167), (252, 16), "#135800", "dc_3row2", 1, 3),
    ("dc_3row2_2", (32, 183), (252, 16), "#135800", "dc_3row2", 1, 3),
    ("dc_3row2_3", (32, 199), (252, 16), "#135800", "dc_3row2", 1, 3),

    ("dc_2col1_1.1", (32, 170), (120, 16), "#135800", "dc_2col1", 1, 3),
    ("dc_2col1_1.2", (32, 186), (120, 16), "#135800", "dc_2col1", 1, 3),
    ("dc_2col1_1.3", (32, 202), (120, 16), "#135800", "dc_2col1", 1, 3),
    ("dc_2col1_2.1", (152, 170), (120, 16), "#135800", "dc_2col1", 1, 3),
    ("dc_2col1_2.2", (152, 186), (120, 16), "#135800", "dc_2col1", 1, 3),
    ("dc_2col1_2.3", (152, 202), (120, 16), "#135800", "dc_2col1", 1, 3),

    ("ngp_1_1", (21, 41), (44, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngp_1_2", (21, 57), (30, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngp_1_3", (21, 73), (44, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngp_1_4", (21, 89), (44, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngp_1_5", (21, 105), (44, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngp_1_6", (21, 121), (30, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_h", (31, 21), (91, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_1", (71, 41), (115, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_2", (71, 57), (115, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_3", (71, 73), (115, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_4", (71, 89), (115, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_5", (71, 105), (115, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_6", (71, 121), (215, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngg_1_6", (71, 137), (215, 13), "#e0e0e0", "ng_1", 1, 3),
    ("ngb_1_1", (127, 21), (60, 13), "#e0e0e0", "ng_1", 1, 3),

    ("ngp_1_h", (31, 21), (114, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_1", (29, 47), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_2", (29, 63), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_3", (29, 79), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_4", (29, 95), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_5", (29, 111), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_1_6", (29, 127), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_2_1", (159, 47), (70, 13), "#e0e0e0", "ng_2", 1, 3),
    ("ngg_2_2", (159, 63), (70, 13), "#d9d9d9", "ng_2", 1, 3),
    ("ngg_2_3", (159, 79), (70, 13), "#d9d9d9", "ng_2", 1, 3),
    ("ngg_2_4", (159, 95), (70, 13), "#d9d9d9", "ng_2", 1, 3),
    ("ngg_2_5", (159, 111), (70, 13), "#cccccc", "ng_2", 1, 3),
    ("ngg_2_6", (159, 127), (70, 13), "#cccccc", "ng_2", 1, 3),

    ("csc_1_1", (32, 170), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_2", (32, 186), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_3", (32, 202), (48, 15), "#135800", "csc_1", 1, 3),
    ("csc_1_4", (96, 170), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_5", (96, 186), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_6", (96, 202), (48, 15), "#135800", "csc_1", 1, 3),
    ("csc_1_7", (160, 170), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_8", (160, 186), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_9", (160, 202), (48, 15), "#135800", "csc_1", 1, 3),
    ("csc_1_10", (224, 170), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_11", (224, 186), (48, 16), "#135800", "csc_1", 1, 3),
    ("csc_1_12", (224, 202), (48, 15), "#135800", "csc_1", 1, 3),

    ("csc_2_1", (32, 168), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_2", (32, 184), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_3", (32, 200), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_4", (96, 168), (42, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_5", (96, 184), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_6", (96, 200), (42, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_7", (160, 168), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_8", (160, 184), (28, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_9", (160, 200), (42, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_10", (224, 168), (42, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_11", (224, 184), (42, 16), "#135800", "csc_2", 0.7, 3),
    ("csc_2_12", (224, 200), (42, 16), "#135800", "csc_2", 0.7, 3),

    ("an_2", (17, 31), (29, 15), "#135800", "an_2", 0.7, 3),
    ("an_3", (17, 31), (44, 15), "#135800", "an_3", 0.7, 3),
    ("an_4", (17, 31), (59, 15), "#135800", "an_4", 1, 3),
    ("an_5", (17, 31), (74, 15), "#135800", "an_5", 1, 3),
    ("an_6", (17, 31), (89, 15), "#135800", "an_6", 1, 3),
    ("an_7", (17, 31), (104, 15), "#135800", "an_7", 1, 3),
    ("an_8", (17, 31), (119, 15), "#135800", "an_8", 1, 3),
    ("an_9", (17, 31), (134, 15), "#135800", "an_9", 1, 3),
    ("an_10", (17, 31), (149, 15), "#135800", "an_10", 1, 3),

    ("an_exr_h", (103, 13), (112, 14), "#135800", "exr", 0.8, 3),
    ("exr_1_1", (31, 37), (90, 13), "#e0e0e0", "exr_0", 1, 3),
    ("exr_1_2", (31, 53), (90, 13), "#e0e0e0", "exr_1", 1, 3),
    ("exr_1_3", (31, 69), (90, 13), "#e0e0e0", "exr_2", 1, 3),
    ("exr_1_4", (31, 85), (90, 13), "#e0e0e0", "exr_3", 1, 3),
    ("exr_1_5", (31, 101), (90, 13), "#e0e0e0", "exr_4", 1, 3),
    ("exr_1_6", (31, 117), (90, 13), "#e0e0e0", "exr_5", 1, 3),
    ("exr_1_7", (31, 133), (90, 13), "#e0e0e0", "exr_6", 1, 3),
    ("exr_2_1", (191, 37), (90, 13), "#e0e0e0", "exr_7", 1, 3),
    ("exr_2_2", (191, 53), (90, 13), "#e0e0e0", "exr_8", 1, 3),
    ("exr_2_3", (191, 69), (90, 13), "#e0e0e0", "exr_9", 1, 3),
    ("exr_2_4", (191, 85), (90, 13), "#e0e0e0", "exr_10", 1, 3),
    ("exr_2_5", (191, 101), (90, 13), "#e0e0e0", "exr_11", 1, 3),
    ("exr_2_6", (191, 117), (90, 13), "#e0e0e0", "exr_12", 1, 3),
    ("exr_2_7", (191, 133), (90, 13), "#e0e0e0", "exr_13", 1, 3),

    ("mg_info_1", (1, 59), (139, 15), "#e0e0e0", "mg_info", 0.8, 3),
    ("mg_info_2", (1, 75), (139, 15), "#e0e0e0", "mg_info", 0.8, 3),
    ("mg_movie", (188, 25), (116, 15), "#003abd", "magazine", 1, 3),
    ("mg_concert", (188, 57), (116, 15), "#f763a3", "magazine", 1, 3),
    ("mg_event_1", (16, 105), (225, 13), "#7b4ace", "mg_event_1", 1, 3),
    ("mg_event_2", (16, 121), (225, 13), "#7b4ace", "mg_event_2", 1, 3),
    ("mg_event_3", (16, 137), (225, 13), "#7b4ace", "mg_event_3", 1, 3),
    ("mg_genre_c1", (240, 48), (64, 8), "#e0e0e0", "mg_genre_c1", 0.8, 3, "Classical"),
    ("mg_genre_c2", (240, 48), (64, 8), "#e0e0e0", "mg_genre_c2", 0.8, 3, "Idol"),
    ("mg_genre_c3", (240, 48), (64, 8), "#e0e0e0", "mg_genre_c3", 0.8, 3, "Rock"),
    ("mg_genre_c4", (240, 48), (64, 8), "#e0e0e0", "mg_genre_c4", 0.8, 3, "New Music"),
    ("mg_genre_m1", (240, 16), (64, 8), "#e0e0e0", "mg_genre_m1", 0.8, 3, "Comedy"),
    ("mg_genre_m2", (240, 16), (64, 8), "#e0e0e0", "mg_genre_m2", 0.8, 3, "Romance"),
    ("mg_genre_m3", (240, 16), (64, 8), "#e0e0e0", "mg_genre_m3", 0.8, 3, "Action"),
    ("mg_genre_m4", (240, 16), (64, 8), "#e0e0e0", "mg_genre_m4", 0.8, 3, "Horror"),
    ("mg_genre_m5", (240, 16), (64, 8), "#e0e0e0", "mg_genre_m5", 0.8, 3, "Anime"),
    ("mg_stadium_3_1_b", (272, 88), (32, 15), "#526a6a", "mg_stadium_3_1_b", 0.8, 3, "Baseball"),
    ("mg_stadium_3_2_b", (272, 104), (32, 15), "#526a6a", "mg_stadium_3_2_b", 0.8, 3, "Baseball"),
    ("mg_stadium_3_3_b", (272, 120), (32, 15), "#526a6a", "mg_stadium_3_3_b", 0.8, 3, "Baseball"),
    ("mg_stadium_3_1_w", (272, 88), (32, 15), "#526a6a", "mg_stadium_3_1_w", 0.8, 3, "Wrestling"),
    ("mg_stadium_3_2_w", (272, 104), (32, 15), "#526a6a", "mg_stadium_3_2_w", 0.8, 3, "Wrestling"),
    ("mg_stadium_3_3_w", (272, 120), (32, 15), "#526a6a", "mg_stadium_3_3_w", 0.8, 3, "Wrestling"),
    ("mg_dspot_1", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_1", 0.8, 3, "(Kirameki Central Park introduced!)"),
    ("mg_dspot_2", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_2", 0.8, 3, "(Art Museum completed!)"),
    ("mg_dspot_3", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_3", 0.8, 3, "(Aquarium special feature!)"),
    ("mg_dspot_4", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_4", 0.8, 3, "(Stadium completed!)"),
    ("mg_dspot_5", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_5", 0.8, 3, "(Botanical Garden special feature!)"),
    ("mg_dspot_6", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_6", 0.8, 3, "(Bowling Alley special feature!)"),
    ("mg_dspot_7", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_7", 0.8, 3, "(Planetarium special feature!)"),
    ("mg_dspot_8", (14, 80), (148, 8), "#e0e0e0", "mg_dspot_8", 0.8, 3, "(Karaoke BOX special feature!)"),

    ("chcr_g_h_1", (6, 14), (300, 15), "#1f1f1f", "chcr_1", 1, 5),
    ("chcr_w_h_1", (6, 14), (300, 15), "#1f1f1f", "chcr_1", 1, 5),
    ("chcr_p_1_1", (14, 30), (32, 16), "#1f1f1f", "chcr_1", 0.8, 5),
    ("chcr_p_1_1", (174, 30), (48, 16), "#1f1f1f", "chcr_1", 0.8, 5),

    ("chcr_g_info_1", (46, 175), (255, 15), "#000000", "chcr_1", 1, 5, f"XEUPIU VERSION {CONFIG['version']}:"),
    ("chcr_g_info_2", (46, 190), (255, 48), "#1f1f1f", "chcr_1", 0.9, 5, "Currently, the tool expects the player data to be 'PLA' for surname, 'YER' for name, and 'PLAYA' for nickname (third menu on the left). For the tool to work as intended, please follow this pattern, and fill in the configuration file with your desired character name. Character's birthday may be chosen as you wish.\n\nWe thank you for your understanding."),

    ("chcr_w_h_2", (6, 14), (300, 15), "#1f1f1f", "chcr_2", 1, 5),
    ("chcr_p_2_1", (20, 30), (48, 16), "#1f1f1f", "chcr_2", 0.8, 5),
    ("chcr_p_2_2", (198, 30), (48, 16), "#1f1f1f", "chcr_2", 0.8, 5),
    ("chcr_p_2_3", (38, 62), (48, 16), "#1f1f1f", "chcr_2", 0.8, 5),
    ("chcr_p_2_4", (38, 110), (48, 16), "#1f1f1f", "chcr_2", 0.8, 5),
    ("chcr_p_2_5", (38, 174), (48, 16), "#1f1f1f", "chcr_2", 0.8, 5),

    ("chcr_p_3_1", (38, 62), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),
    ("chcr_p_3_2", (38, 94), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),
    ("chcr_p_3_3", (38, 126), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),
    ("chcr_p_3_4", (38, 158), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),
    ("chcr_w_3_1", (135, 182), (93, 16), "#1f1f1f", "chcr_3", 1, 5),
    ("chcr_p_3_5", (128, 200), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),
    ("chcr_p_3_6", (182, 200), (48, 16), "#1f1f1f", "chcr_3", 0.8, 5),

    ("chcr_w_4_1", (102, 62), (32, 16), "#1f1f1f", "chcr_4", 0.8, 5),
    ("chcr_w_4_2", (158, 62), (32, 16), "#1f1f1f", "chcr_4", 0.8, 5),

    ("rpg_uig_t_alert", (33, 17), (260, 13), "#084aad", "rpg_ui_top", 1, 3),
    ("rpg_uig_b_enemy_1", (18, 186), (83, 15), "#084aad", "rpg_ui_bottom_ui", 1, 3),
    ("rpg_uig_b_party_1", (176, 178), (65, 15), "#084aad", "rpg_ui_bottom_ui", 1, 3),
    ("rpg_uig_b_party_2", (176, 194), (65, 15), "#084aad", "rpg_ui_bottom_ui", 1, 3),
    ("rpg_uiw_b_action_1", (122, 178), (27, 13), "#084aad", "rpg_ui_bottom_actions", 0.6, 3),
    ("rpg_uiw_b_action_2", (122, 193), (27, 13), "#084aad", "rpg_ui_bottom_actions", 0.6, 3),
    ("rpg_uiw_b_action_3", (122, 208), (27, 13), "#084aad", "rpg_ui_bottom_actions", 0.6, 3),

    ("sss_k_slot", (18, 86), (30, 14), "#ffffff", "save_selection_screen", 0.8, 3, "SLOT"),
    ("sss_k_nb1_1", (96, 151), (195, 13), "#ffffff", "save_selection_screen", 0.8, 3),
    ("sss_k_nb1_2", (96, 167), (195, 13), "#ffffff", "save_selection_screen", 0.8, 3),
    ("sss_k_nb1_3", (96, 183), (195, 13), "#ffffff", "save_selection_screen", 0.8, 3),
    ("sss_k_nb1_4", (96, 199), (195, 13), "#ffffff", "save_selection_screen", 0.8, 3),
    ("sss_k_save_1_1", (120, 44), (48, 13), "#e6e6e6", "save_selection_screen", 1, 3, "Name"),
    ("sss_k_save_1_2", (120, 60), (48, 13), "#ffffff", "save_selection_screen", 1, 3, "Nickname"),
    ("sss_k_save_1_3", (120, 76), (48, 13), "#e6e6e6", "save_selection_screen", 1, 3, "Club"),
    ("sss_k_save_1_4", (120, 92), (48, 15), "#ffffff", "save_selection_screen", 1, 3, "Endings"),
    ("sss_k_save_2_h", (98, 132), (97, 16), "#63bdce", "save_selection_screen_load", 1, 3, "Attributes"),
    ("sss_k_save_2_1", (98, 151), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "HEALTH"),
    ("sss_k_save_2_2", (98, 167), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "HUMAN"),
    ("sss_k_save_2_3", (98, 183), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "SCIENC"),
    ("sss_k_save_2_4", (98, 199), (42, 15), "#e6e6e6", "save_selection_screen_load", 1, 3, "ARTS"),
    ("sss_k_save_2_5", (200, 133), (42, 15), "#e6e6e6", "save_selection_screen_load", 1, 3, "EXERC"),
    ("sss_k_save_2_6", (200, 151), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "TRIVIA"),
    ("sss_k_save_2_6", (200, 167), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "STYLE"),
    ("sss_k_save_2_6", (200, 183), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "GUTS"),
    ("sss_k_save_2_6", (200, 199), (42, 13), "#e6e6e6", "save_selection_screen_load", 1, 3, "STRESS"),

    ("bes_subtitle", (70, 198), (190, 15), "#000000", "bad_ending_song", 0.8, 3),
    ("ngameplus_prompt", (15, 55), (240, 15), "#c3c3c3", "new_game_plus", 1, 3),

    ("si_1_h", (46, 187), (226, 15), "#cccccc", "sports_instructions_1", 1, 3, "BALL ROLLING"),
    ("si_1_t", (46, 202), (226, 35), "#ffffff", "sports_instructions_1", 1, 3, "First, choose a girl to partner with. Then, during the game, use the D-Pad to move forward, backward, left and right, and push the ball with ◯. Make sure to push the left and right buttons evenly."),
    ("si_2_h", (46, 187), (226, 15), "#cccccc", "sports_instructions_2", 1, 3, "SPOON RELAY"),
    ("si_2_t", (46, 202), (226, 35), "#ffffff", "sports_instructions_2", 1, 3, "Press ◯ repeatedly to run. When the egg is moving to the left, press the L1 button, and when it is moving to the right, press the R1 button. Keep your balance so it doesn't fall!"),
    ("si_3_h", (46, 187), (226, 15), "#cccccc", "sports_instructions_3", 1, 3, "BORROWING RACE"),
    ("si_3_t", (46, 202), (226, 35), "#ffffff", "sports_instructions_3", 1, 3, "Press ◯ repeatedly to run. When you arrive at the stop, use the D-Pad to find the girl written on the envelope and take her with you to the goal."),
    ("si_4_h", (46, 187), (226, 15), "#cccccc", "sports_instructions_4", 1, 3, "THREE-LEGGED RACE"),
    ("si_4_t", (46, 202), (226, 35), "#ffffff", "sports_instructions_4", 1, 3, "Follow my voice! Press the L1 button when I say 'left' (hidari), and R1 when I say 'right' (migi). If you press the wrong button you'll fall, so be careful! We'll start with left. Ready?"),

    ("si_s_1_h", (46, 187), (226, 15), "#eeeeee", "shrine_instructions_1_1", 1, 3, "GOLDFISH SCOOPING"),
    ("si_s_1_t", (46, 202), (226, 35), "#ffffff", "shrine_instructions_1_1", 1, 3, "Use the D-Pad to move the net. Press ◯ to dip the net into the water, and release it to scoop it up."),
    ("si_s_1_h", (105, 69), (103, 21), "#cee6e6", "shrine_instructions_1_2", 1, 3, "TODAY'S RESULTS"),

    # ("exm_1_1", (38, 31), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_2", (38, 51), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_3", (38, 71), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_4", (38, 91), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_5", (38, 111), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_6", (38, 131), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_7", (38, 151), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exm_1_8", (38, 171), (102, 15), "#83939b", "extras_menu_1", 1, 3),
    # ("exb_b_1", (95, 143), (99, 13), "#83939b", "extras_menu_bonus", 1, 3),
    # ("exb_b_2", (95, 159), (99, 13), "#83939b", "extras_menu_bonus", 1, 3),
    # ("exb_b_3", (95, 175), (99, 13), "#83939b", "extras_menu_bonus", 1, 3),
    # ("exb_b_4", (95, 191), (99, 13), "#83939b", "extras_menu_bonus", 1, 3),

    # ("chcr_k1_1_1", (120, 43), (48, 13), "#e6e6e6", detect_chcr_0, 0.8, 5),
    # ("chcr_k1_1_2", (120, 59), (48, 13), "#ffffff", detect_chcr_0, 0.8, 5),
    # ("chcr_k1_1_3", (120, 75), (48, 13), "#e6e6e6", detect_chcr_0, 0.8, 5),
    # ("chcr_k2_1_4_1", (95, 149), (208, 15), "#ffffff", detect_chcr_0_1, 1, 3),
    # ("chcr_k2_1_4_2", (95, 165), (208, 15), "#ffffff", detect_chcr_0_1, 1, 3),
    # ("chcr_k2_1_4_3", (95, 181), (208, 15), "#ffffff", detect_chcr_0_1, 1, 3),
    # ("chcr_k2_1_4_4", (95, 197), (208, 15), "#ffffff", detect_chcr_0_1, 1, 3),
    # ("chcr_k1_1_4_1", (100, 149), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_2", (100, 165), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_3", (100, 181), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_4", (100, 197), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_5", (205, 132), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_6", (205, 149), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_7", (205, 165), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
    # ("chcr_k1_1_4_8", (205, 181), (36, 15), "#e6e6e6", detect_chcr_0_4, 0.8, 5),
]

class SelectableRectOverlay(OverlayWindow):
    def __init__(self, window_id: int, item_idx: int, db: NotebookDatabase, pcr: PoorCR = None, tt: Translator = None):
        selectable_rect = SELECTABLE_RECTS[item_idx]
        self.item_id = selectable_rect[0]
        self.rect_x, self.rect_y = selectable_rect[1]
        self.rect_w, self.rect_h = selectable_rect[2]
        self.bg_color = selectable_rect[3]
        self.screen_cue_id = selectable_rect[4]
        self.font_scaling = selectable_rect[5]
        self.padding_x = selectable_rect[6]
        self.fixed_text = selectable_rect[7] if len(selectable_rect) > 7 else None

        self.db = db if db is not None else NotebookDatabase()
        self.pcr = pcr if pcr is not None else PoorCR(only_perfect=True, padding_x=self.padding_x)
        self.tt = tt if tt is not None else Translator()

        self.is_cue_detected = False
        self.last_overlay_area_rgb = None

        self.group = None
        for key, val in SELECTABLE_RECT_GROUPS.items():
            if self.item_id.startswith(key):
                self.group = val
                break

        if self.group is None:
            raise ValueError(f"SelectableRectOverlay: No group found for {self.item_id}")

        super().__init__(window_id)

    def create_overlay(self, window_pos_x: int, window_pos_y: int, window_width: int, window_height: int) -> None:
        self.font_size = min(int(self.game_scaling * 6 * self.font_scaling), 32)

        self.pos_x = window_pos_x + (self.rect_x * self.game_scaling)
        self.pos_y = window_pos_y + (self.rect_y * self.game_scaling)
        self.textbox_width = int(self.rect_w * self.game_scaling)
        self.textbox_height = int(self.rect_h * self.game_scaling)

        self.root = tk.Toplevel()
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.root.geometry(f"{self.textbox_width}x{self.textbox_height}+{self.pos_x}+{self.pos_y}")
        self.label = tk.Label(self.root, text="", font=("MS Gothic", self.font_size), fg=self.group['textcolor'],
                              width=self.textbox_width, height=self.textbox_height,
                              wraplength=self.textbox_width, bg=self.bg_color,
                              justify='left', compound='left', anchor='w')
        self.label.pack()

        self.root.update_idletasks()
        self.root.update()

    def detect_gameobj(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image) -> bool:
        if not self.is_cue_detected:
            return False

        r = r[self.rect_x:(self.rect_x + self.rect_w), self.rect_y:(self.rect_y + self.rect_h)]
        g = g[self.rect_x:(self.rect_x + self.rect_w), self.rect_y:(self.rect_y + self.rect_h)]
        b = b[self.rect_x:(self.rect_x + self.rect_w), self.rect_y:(self.rect_y + self.rect_h)]

        is_unselected = self.group['is_unselected_fn'](r, g, b)
        is_selected = self.group['is_selected_fn'](r, g, b)
        is_detected = is_unselected or is_selected

        # Calibrate if previously hidden
        if is_detected and self.is_hidden and self.fixed_text is None:
            img_item = img_ss.crop((self.rect_x, self.rect_y, (self.rect_x + self.rect_w), (self.rect_y + self.rect_h)))
            img_item_bw = self.group['bw_conversion_fn'](img_item)

            if imp.check_is_text_empty(img_item_bw):
                return False

            img_item_bw = imp.trim_text(img_item_bw)
            img_item_bw_np = np.array(img_item_bw.convert('1'))
            self.pcr.calibrate(img_item_bw_np)

        self.toggle_selected(is_selected)

        return is_detected

    def update_text(self, img_ss: Image):
        if self.fixed_text is not None:
            text = self.fixed_text
        else:
            img_item = img_ss.crop((self.rect_x, self.rect_y, (self.rect_x + self.rect_w), (self.rect_y + self.rect_h)))
            img_item_rgb = np.array(img_item.convert('RGB')).T

            if self.last_overlay_area_rgb is not None and np.all(self.last_overlay_area_rgb == img_item_rgb):
                return

            img_item_bw = self.group['bw_conversion_fn'](img_item)
            img_item_bw = imp.trim_text(img_item_bw)

            if imp.check_is_text_empty(img_item_bw):
                self.hide()
                return

            text_jp = self.pcr.detect(img_item_bw)
            if "?" in text_jp:
                img_item_bw_np = np.array(img_item_bw.convert('1'))
                self.pcr.calibrate(img_item_bw_np)
                text_jp = self.pcr.detect(img_item_bw)

            if is_str_empty(text_jp):
                self.hide()
                text = text_jp
            else:
                text_en = self.db.retrieve_translation(text_jp)
                if text_en is None:
                    text_jp_processed, _ = Database.generalize_string(text_jp)
                    text_en = self.tt.translate(text_jp_processed)
                    self.db.insert_translation(text_jp, text_en)
                text = text_en

        self.update(" " + text)

    def step(self, r: np.ndarray, g: np.ndarray, b: np.ndarray, img_ss: Image, cue_dict: dict) -> None:
        if self.screen_cue_id not in cue_dict:
            raise ValueError(f"Screen cue {self.screen_cue_id} not found in cue_dict")

        self.is_cue_detected = cue_dict[self.screen_cue_id]
        self.hide_if_not_needed(r, g, b, img_ss)

        if not self.is_hidden:
            self.update_text(img_ss)

    def toggle_selected(self, val: bool):
        if val:
            self.label.config(bg=self.group['selected_color'])
        else:
            self.label.config(bg=self.bg_color)


if __name__ == "__main__":
    window_id = get_window_by_title("Tokimeki Memorial")

    OverlayWindow.create_master()
    db = NotebookDatabase()

    overlays = [SelectableRectOverlay(window_id, i, db) for i in range(len(SELECTABLE_RECTS))]

    while True:
        img_ss = get_window_image(window_id,
                                  offset_x=(overlays[0].letterbox_offset[0], overlays[0].letterbox_offset[1]),
                                  offset_y=(overlays[0].letterbox_offset[2], overlays[0].letterbox_offset[3]))
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)
        img_rgb = np.array(img_ss.convert('RGB')).T

        for overlay in overlays:
            overlay.hide_if_not_needed(*img_rgb, img_ss)
            overlay.update_text(img_ss)
