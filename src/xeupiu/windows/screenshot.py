from ctypes import windll

from xeupiu.config import CONFIG, RES_SCALE_FACTOR
import win32gui
import win32ui
from PIL import Image

RESOLUTION_SCALE_OFFSET_Y = (round((CONFIG.get_borders_var()["size_toolbar"] + CONFIG.get_borders_var()["size_window_border_top"]) * RES_SCALE_FACTOR) - (CONFIG.get_borders_var()["size_toolbar"] + CONFIG.get_borders_var()["size_window_border_top"]))
BASE_DIMS = None

def get_window_by_title(window_title):
    """
    Returns the window ID of the window with the given title.
    If there are multiple windows with the same title, returns the first one.

    :param window_title: The title of the window to search for.
    :return: The window ID of the window with the given title.
    """

    toplist, winlist = [], []

    def enum_cb(hwnd, _):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)
    window = [(hwnd, title) for hwnd, title in winlist if window_title.lower() in title.lower()]

    if not window:
        raise ValueError(f"Window with title '{window_title}' not found.")

    window_id, window_name = window[0]

    return window_id

def get_window_image(window_id, offset_x=(0, 0), offset_y=(0, 0)):
    """
    Returns a PIL image of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :return: A PIL image of the window with the given ID.
    """

    _, _, w, h = get_window_base_dims(window_id)

    hwndDC = win32gui.GetWindowDC(window_id)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(window_id, saveDC.GetSafeHdc(), 3)
    bmpstr = saveBitMap.GetBitmapBits(True)

    try:
        img = Image.frombuffer('RGB', (w, h), bmpstr, 'raw', 'BGRX', 0, 1)
    except ValueError:
        raise Exception("Image Buffer Error: failed to capture game screen.")

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(window_id, hwndDC)

    border_config = CONFIG.get_borders_var()

    img = img.crop((offset_x[0],
                    offset_y[0] + border_config["size_toolbar"],
                    img.width - offset_x[1],
                    img.height - offset_y[1] - border_config["size_window_border_bottom"]))

    return img

def get_window_base_dims(window_id) -> tuple[int, int, int, int]:
    """
    Returns the position and size of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :return: The position of the window with the given ID.
    """
    global BASE_DIMS

    if BASE_DIMS is None:
        x0, y0, x1, y1 = win32gui.GetClientRect(window_id)
        w = round((x1 - x0) * RES_SCALE_FACTOR)
        h = round((y1 - y0) * RES_SCALE_FACTOR)

        windll.shcore.SetProcessDpiAwareness(1)
        x, y, _, _ = win32gui.GetWindowRect(window_id)

        BASE_DIMS = (x, y, w, h)

    return BASE_DIMS
