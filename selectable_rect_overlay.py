import glob
import time
import tkinter as tk

import numpy as np
from PIL import Image

import translator
from constants import is_str_empty
from notebook_database import NotebookDatabase
from poorcr import PoorCR
from screenshot import get_window_by_title, get_window_image
from overlay import OverlayWindow
import image_processing as imp

def get_count_by_thresholds(red, green, blue, x, y, w, h, r_min, r_max, g_min, g_max, b_min, b_max):
    red = red[x:x + w, y:y + h]
    green = green[x:x + w, y:y + h]
    blue = blue[x:x + w, y:y + h]

    return np.sum((red > r_min) & (red < r_max) & (green > g_min) & (green < g_max) & (blue > b_min) & (blue < b_max))

def get_count_by_equality(red, green, blue, x, y, w, h, r, g, b):
    red = red[x:x + w, y:y + h]
    green = green[x:x + w, y:y + h]
    blue = blue[x:x + w, y:y + h]

    return np.sum((red == r) & (green == g) & (blue == b))

def detect_mark_by_count(red, green, blue, x, y, w, h, r, g, b, count):
    c = get_count_by_equality(red, green, blue, x, y, w, h, r, g, b)
    return c == count

def detect_mark_by_count_with_thresholds(red, green, blue, x, y, w, h, r_min, r_max, g_min, g_max, b_min, b_max, count):
    return get_count_by_thresholds(red, green, blue, x, y, w, h, r_min, r_max, g_min, g_max, b_min, b_max) == count

def detect_mark_textbox_choice1(red, green, blue):
    is_cursor_there = detect_mark_by_count(red, green, blue, 274, 170, 6, 47, 239, 230, 239, 4)
    is_selection_there = detect_mark_by_count_with_thresholds(red, green, blue, 260, 166, 6, 50, 60, 120, 150, 180, 50, 100, 96)
    return is_cursor_there and is_selection_there

def detect_mark_textbox_choice2(red, green, blue):
    is_cursor_there = detect_mark_by_count(red, green, blue, 278, 166, 6, 47, 239, 230, 239, 4)
    is_selection_there = detect_mark_by_count_with_thresholds(red, green, blue, 270, 166, 6, 50, 60, 120, 150, 180, 50, 100, 96)
    return is_cursor_there and is_selection_there

def detect_mark_character_selection_choice_1(red, green, blue):
    is_cursor_in_vgap_1 = detect_mark_by_count(red, green, blue, 80, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_2 = detect_mark_by_count(red, green, blue, 144, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_3 = detect_mark_by_count(red, green, blue, 208, 170, 16, 54, 239, 230, 239, 68)
    is_cursor_in_vgap_4 = detect_mark_by_count(red, green, blue, 272, 170, 16, 54, 239, 230, 239, 68)

    is_selection_in_hgap_1 = 75 < get_count_by_thresholds(red, green, blue, 31, 182, 260, 4, 60, 120, 150, 210, 30, 120) < 100
    is_selection_in_hgap_2 = 75 < get_count_by_thresholds(red, green, blue, 31, 198, 260, 4, 60, 120, 150, 210, 30, 120) < 100
    is_selection_in_hgap_3 = 50 < get_count_by_thresholds(red, green, blue, 31, 214, 260, 4, 60, 120, 150, 210, 30, 120) < 100

    return (is_cursor_in_vgap_1 or is_cursor_in_vgap_2 or is_cursor_in_vgap_3 or is_cursor_in_vgap_4) and (is_selection_in_hgap_1 or is_selection_in_hgap_2 or is_selection_in_hgap_3)

detect_mark_nb_3col1 = lambda r, g, b: detect_mark_by_count(r, g, b,100, 56, 9, 9, 41, 132, 164, 7)
detect_mark_nb_2col1 = lambda r, g, b: detect_mark_by_count(r, g, b,145, 37, 7, 8, 99, 132, 164, 16)
detect_mark_nb_2col2 = lambda r, g, b: detect_mark_by_count(r, g, b,145, 35, 7, 15, 41, 132, 164, 9)
detect_mark_ng_1 = lambda r, g, b: detect_mark_by_count(r, g, b,23, 20, 8, 14, 230, 0, 164, 42)
detect_mark_ng_2 = lambda r, g, b: detect_mark_by_count(r, g, b,160, 21, 16, 15, 41, 164, 255, 76)
detect_mark_an_2 = lambda r, g, b: detect_mark_by_count(r, g, b, 47, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_3 = lambda r, g, b: detect_mark_by_count(r, g, b, 61, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_4 = lambda r, g, b: detect_mark_by_count(r, g, b, 75, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_5 = lambda r, g, b: detect_mark_by_count(r, g, b, 89, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_6 = lambda r, g, b: detect_mark_by_count(r, g, b, 103, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_7 = lambda r, g, b: detect_mark_by_count(r, g, b, 117, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_8 = lambda r, g, b: detect_mark_by_count(r, g, b, 131, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_9 = lambda r, g, b: detect_mark_by_count(r, g, b, 145, 23, 6, 32, 49, 0, 0, 70)
detect_mark_an_10 = lambda r, g, b: detect_mark_by_count(r, g, b, 159, 23, 6, 32, 49, 0, 0, 70)
detect_mark_exr = lambda r, g, b: detect_mark_by_count(r, g, b, 82, 6, 156, 28, 49, 0, 0, 960)
detect_mark_magazine = lambda r, g, b: detect_mark_by_count(r, g, b, 6, 10, 97, 36, 255, 41, 0, 816)
detect_chcr_0 = lambda r, g, b: detect_mark_by_count(r, g, b, 7, 1, 103, 15, 82, 197, 206, 68)
detect_chcr_0_1 = lambda r, g, b: detect_mark_by_count(r, g, b, 130, 132, 8, 83, 247, 239, 239, 32)
detect_chcr_0_4 = lambda r, g, b: detect_mark_by_count(r, g, b, 130, 132, 8, 83, 230, 230, 230, 407)
detect_chcr_1 = lambda r, g, b: detect_mark_by_count(r, g, b, 22, 30, 283, 16, 255, 197, 247, 203)
detect_chcr_2 = lambda r, g, b: detect_mark_by_count(r, g, b, 22, 30, 283, 16, 255, 197, 247, 307)
detect_chcr_3 = lambda r, g, b: detect_mark_by_count(r, g, b, 33, 56, 60, 35, 255, 197, 247, 88)
detect_chcr_4 = lambda r, g, b: detect_mark_by_count(r, g, b, 33, 56, 60, 123, 255, 197, 247, 371)

SELECTABLE_RECT_GROUPS = {
    "dc": {
        "fullname": "dialogue_choice",
        "textcolor": "#ffffff",
        "selected_color": "#39a930",
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (164, 206, 206)),
        "is_unselected_fn": lambda r, g, b: np.mean((r < 30) & (g > 60) & (g < 140) & (b == 0)) > 0.7,
        "is_selected_fn": lambda r, g, b: np.mean((r > 30) & (r < 170) & (g > 150) & (b > 20) & (b < 120)) > 0.7,
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
        "is_unselected_fn": lambda r, g, b: np.mean((r < 30) & (g > 60) & (g < 140) & (b == 0)) > 0.6,
        "is_selected_fn": lambda r, g, b: np.mean((r > 30) & (r < 170) & (g > 150) & (b > 20) & (b < 120)) > 0.55,
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
        "textcolor": "#e600a5",
        "selected_color": None,
        "bw_conversion_fn": lambda x: imp.convert_to_black_and_white(x, (255, 197, 247)),
        "is_unselected_fn": lambda r, g, b: True,
        "is_selected_fn": lambda r, g, b: False,
    }
}

SELECTABLE_RECTS = [
    ("nb_3col1_h", (20, 35), (256, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_1.1", (24, 64), (72, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_1.2", (24, 80), (72, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_1.3", (24, 96), (72, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_1.4", (24, 112), (72, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_1.5", (24, 128), (72, 16), "#dddddd", detect_mark_nb_3col1, 1),
    ("nb_3col1_2.1", (108, 64), (72, 16), "#e0e0e0", detect_mark_nb_3col1, 1),
    ("nb_3col1_2.2", (108, 80), (72, 16), "#dedede", detect_mark_nb_3col1, 1),
    ("nb_3col1_2.3", (108, 96), (72, 16), "#d8d8d8", detect_mark_nb_3col1, 1),
    ("nb_3col1_2.4", (108, 112), (72, 16), "#d3d3d3", detect_mark_nb_3col1, 1),
    ("nb_3col1_2.5", (108, 128), (72, 16), "#cecece", detect_mark_nb_3col1, 1),
    ("nb_3col1_3.1", (200, 64), (72, 16), "#d8d8d8", detect_mark_nb_3col1, 1),
    ("nb_3col1_3.2", (200, 80), (72, 16), "#d5d5d5", detect_mark_nb_3col1, 1),
    ("nb_3col1_3.3", (200, 96), (72, 16), "#d2d2d2", detect_mark_nb_3col1, 1),
    ("nb_3col1_3.4", (200, 112), (72, 16), "#cacaca", detect_mark_nb_3col1, 1),
    ("nb_3col1_3.5", (200, 128), (72, 16), "#c8c8c8", detect_mark_nb_3col1, 1),

    ("nb_2col1_1.1", (35, 55), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.2", (35, 67), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.3", (35, 79), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.4", (35, 91), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.5", (35, 103), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.6", (35, 115), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.7", (35, 127), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),
    ("nb_2col1_1.8", (35, 139), (100, 13), "#e0e0e0", detect_mark_nb_2col1, 1),

    ("nb_2col2_h1", (31, 36), (98, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_h2", (158, 36), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_1.1", (23, 62), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_1.2", (23, 78), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_1.3", (23, 94), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_1.4", (23, 110), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_1.5", (23, 126), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_2.1", (158, 62), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_2.2", (158, 78), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_2.3", (158, 94), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_2.4", (158, 110), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),
    ("nb_2col2_2.5", (158, 126), (109, 15), "#e0e0e0", detect_mark_nb_2col2, 1),

    ("dc_3row1_1", (39, 169), (230, 17), "#135800", detect_mark_textbox_choice1, 1),
    ("dc_3row1_2", (39, 185), (230, 17), "#135800", detect_mark_textbox_choice1, 1),

    ("dc_3row2_1", (32, 167), (252, 16), "#135800", detect_mark_textbox_choice2, 1),
    ("dc_3row2_2", (32, 183), (252, 16), "#135800", detect_mark_textbox_choice2, 1),
    ("dc_3row2_3", (32, 199), (252, 16), "#135800", detect_mark_textbox_choice2, 1),

    ("ngp_1_1", (21, 41), (44, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngp_1_2", (21, 57), (30, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngp_1_3", (21, 73), (44, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngp_1_4", (21, 89), (44, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngp_1_5", (21, 105), (44, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngp_1_6", (21, 121), (30, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_h", (31, 21), (91, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_1", (71, 41), (115, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_2", (71, 57), (115, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_3", (71, 73), (115, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_4", (71, 89), (115, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_5", (71, 105), (115, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_6", (71, 121), (215, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngg_1_6", (71, 137), (215, 13), "#e0e0e0", detect_mark_ng_1, 1),
    ("ngb_1_1", (127, 21), (60, 13), "#e0e0e0", detect_mark_ng_1, 1),

    ("ngp_1_h", (31, 21), (114, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_1", (29, 47), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_2", (29, 63), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_3", (29, 79), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_4", (29, 95), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_5", (29, 111), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_1_6", (29, 127), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_2_1", (159, 47), (70, 13), "#e0e0e0", detect_mark_ng_2, 1),
    ("ngg_2_2", (159, 63), (70, 13), "#d9d9d9", detect_mark_ng_2, 1),
    ("ngg_2_3", (159, 79), (70, 13), "#d9d9d9", detect_mark_ng_2, 1),
    ("ngg_2_4", (159, 95), (70, 13), "#d9d9d9", detect_mark_ng_2, 1),
    ("ngg_2_5", (159, 111), (70, 13), "#cccccc", detect_mark_ng_2, 1),
    ("ngg_2_6", (159, 127), (70, 13), "#cccccc", detect_mark_ng_2, 1),

    ("csc_1_1", (32, 170), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_2", (32, 186), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_3", (32, 202), (48, 15), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_4", (96, 170), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_5", (96, 186), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_6", (96, 202), (48, 15), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_7", (160, 170), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_8", (160, 186), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_9", (160, 202), (48, 15), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_10", (224, 170), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_11", (224, 186), (48, 16), "#135800", detect_mark_character_selection_choice_1, 1),
    ("csc_1_12", (224, 202), (48, 15), "#135800", detect_mark_character_selection_choice_1, 1),

    ("an_2", (17, 31), (29, 15), "#135800", detect_mark_an_2, 0.7),
    ("an_3", (17, 31), (44, 15), "#135800", detect_mark_an_3, 0.8),
    ("an_4", (17, 31), (59, 15), "#135800", detect_mark_an_4, 1),
    ("an_5", (17, 31), (74, 15), "#135800", detect_mark_an_5, 1),
    ("an_6", (17, 31), (89, 15), "#135800", detect_mark_an_6, 1),
    ("an_7", (17, 31), (104, 15), "#135800", detect_mark_an_7, 1),
    ("an_8", (17, 31), (119, 15), "#135800", detect_mark_an_8, 1),
    ("an_9", (17, 31), (134, 15), "#135800", detect_mark_an_9, 1),
    ("an_10", (17, 31), (149, 15), "#135800", detect_mark_an_10, 1),

    ("an_exr_h", (103, 13), (112, 14), "#135800", detect_mark_exr, 0.8),
    ("exr_1_1", (31, 37), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 37, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_2", (31, 53), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 37, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_3", (31, 69), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 69, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_4", (31, 85), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 85, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_5", (31, 101), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 101, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_6", (31, 117), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 117, 90, 13, 132, 132, 164, 88), 1),
    ("exr_1_7", (31, 133), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 31, 133, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_1", (191, 37), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 37, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_2", (191, 53), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 53, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_3", (191, 69), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 69, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_4", (191, 85), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 85, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_5", (191, 101), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 101, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_6", (191, 117), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 117, 90, 13, 132, 132, 164, 88), 1),
    ("exr_2_7", (191, 133), (90, 13), "#e0e0e0", lambda r, g, b: detect_mark_exr(r,g,b) and not detect_mark_by_count(r, g, b, 191, 133, 90, 13, 132, 132, 164, 88), 1),

    ("mg_movie", (188, 25), (116, 13), "#003abd", detect_mark_magazine, 1),
    ("mg_concert", (188, 57), (116, 13), "#f763a3", detect_mark_magazine, 1),
    ("mg_event_1", (16, 105), (225, 13), "#7b4ace", lambda r, g, b: detect_mark_magazine(r,g,b) and get_count_by_equality(r, g, b, 16, 105, 225, 13, 230, 222, 239) > 10, 1),
    ("mg_event_2", (16, 121), (225, 13), "#7b4ace", lambda r, g, b: detect_mark_magazine(r,g,b) and get_count_by_equality(r, g, b, 16, 121, 225, 13, 230, 222, 239) > 10, 1),
    ("mg_event_3", (16, 137), (225, 13), "#7b4ace", lambda r, g, b: detect_mark_magazine(r,g,b) and get_count_by_equality(r, g, b, 11, 137, 225, 13, 230, 222, 239) > 10, 1),

    ("chcr_g_h_1", (6, 14), (300, 15), "#1f1f1f", detect_chcr_1, 1, 5),
    ("chcr_w_h_1", (6, 14), (300, 15), "#1f1f1f", detect_chcr_1, 1, 5),
    ("chcr_p_1_1", (14, 30), (32, 16), "#1f1f1f", detect_chcr_1, 0.8, 5),
    ("chcr_p_1_1", (174, 30), (48, 16), "#1f1f1f", detect_chcr_1, 0.8, 5),
    ("chcr_w_h_2", (6, 14), (300, 15), "#1f1f1f", detect_chcr_2, 1, 5),
    ("chcr_p_2_1", (20, 30), (48, 16), "#1f1f1f", detect_chcr_2, 0.8, 5),
    ("chcr_p_2_2", (198, 30), (48, 16), "#1f1f1f", detect_chcr_2, 0.8, 5),
    ("chcr_p_2_3", (38, 62), (48, 16), "#1f1f1f", detect_chcr_2, 0.8, 5),
    ("chcr_p_2_4", (38, 110), (48, 16), "#1f1f1f", detect_chcr_2, 0.8, 5),
    ("chcr_p_2_5", (38, 174), (48, 16), "#1f1f1f", detect_chcr_2, 0.8, 5),
    ("chcr_p_3_1", (38, 62), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_p_3_2", (38, 94), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_p_3_3", (38, 126), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_p_3_4", (38, 158), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_w_3_1", (135, 182), (93, 16), "#1f1f1f", detect_chcr_3, 1, 5),
    ("chcr_p_3_5", (128, 200), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_p_3_6", (182, 200), (48, 16), "#1f1f1f", detect_chcr_3, 0.8, 5),
    ("chcr_w_4_1", (102, 62), (32, 16), "#1f1f1f", detect_chcr_4, 0.8, 5),
    ("chcr_w_4_2", (158, 62), (32, 16), "#1f1f1f", detect_chcr_4, 0.8, 5),
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
    def __init__(self, window_id: int, item_idx: int, db: NotebookDatabase, pcr: PoorCR = None):
        selectable_rect = SELECTABLE_RECTS[item_idx]
        self.item_id = selectable_rect[0]
        self.rect_x, self.rect_y = selectable_rect[1]
        self.rect_w, self.rect_h = selectable_rect[2]
        self.bg_color = selectable_rect[3]
        self.detect_mark_fn = selectable_rect[4]
        self.font_scaling = selectable_rect[5]
        self.padding_x = selectable_rect[6] if len(selectable_rect) > 6 else 3

        self.db = db if db is not None else NotebookDatabase()
        self.pcr = pcr if pcr is not None else PoorCR(only_perfect=True, padding_x=self.padding_x)

        for key, val in SELECTABLE_RECT_GROUPS.items():
            if self.item_id.startswith(key):
                self.group = val
                break

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

    def detect_gameobj(self, img_ss: Image) -> bool:
        r, g, b = np.array(img_ss.convert('RGB')).T

        # Sometimes the screenshot comes out black. This is a workaround for that.
        if np.mean((r < 10) & (g < 10) & (b < 10)) > 0.6:
            if self.is_hidden:
                return False
            return True

        is_mark_there = self.detect_mark_fn(r, g, b)
        if not is_mark_there:
            return False

        img_item = img_ss.crop((self.rect_x, self.rect_y, (self.rect_x + self.rect_w), (self.rect_y + self.rect_h)))
        r, g, b = np.array(img_item.convert('RGB')).T

        is_unselected = self.group['is_unselected_fn'](r, g, b)
        is_selected = self.group['is_selected_fn'](r, g, b)
        is_detected = is_unselected or is_selected

        if is_detected and self.is_hidden:
            img_item_bw = self.group['bw_conversion_fn'](img_item)

            if imp.check_is_text_empty(img_item_bw):
                return False

            img_item_bw = imp.trim_text(img_item_bw)
            img_item_bw_np = np.array(img_item_bw.convert('1'))
            self.pcr.calibrate(img_item_bw_np)

        self.toggle_selected(is_selected)

        return is_detected

    def update_text(self, img_ss: Image):
        img_item = img_ss.crop((self.rect_x, self.rect_y, (self.rect_x + self.rect_w), (self.rect_y + self.rect_h)))
        img_item_bw = self.group['bw_conversion_fn'](img_item)
        img_item_bw = imp.trim_text(img_item_bw)

        if imp.check_is_text_empty(img_item_bw):
            self.hide()
            return

        text_jp = self.pcr.detect(img_item_bw)
        if is_str_empty(text_jp):
            self.hide()
            text = text_jp
        else:
            text_en = self.db.retrieve_translation(text_jp)
            if text_en is None:
                text_en = translator.translate_text(text_jp, "google_cloud")
                self.db.insert_translation(text_jp, text_en)
                print(f"Adding new notebook item: {text_jp} - {text_en}")
            text = text_en

        self.update(" " + text)

    def step(self, img_ss: Image):
        self.hide_if_not_needed(img_ss)

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
                                  offset_y=(overlays[0].letterbox_offset[2], overlays[0].letterbox_offset[3]),
                                  use_scaling=False)
        img_ss = img_ss.resize((img_ss.size[0] // overlays[0].game_scaling,
                                img_ss.size[1] // overlays[0].game_scaling),
                               Image.NEAREST)

        for overlay in overlays:
            overlay.hide_if_not_needed(img_ss)
            overlay.update_text(img_ss)
