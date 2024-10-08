import time
from ctypes import windll

from config import CONFIG
import win32gui
import win32ui
from PIL import Image

SCALE_FACTOR = windll.shcore.GetScaleFactorForDevice(0)

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

def get_window_image(window_id, offset_x=(0, 0), offset_y=(0, 0), use_scaling=True):
    """
    Returns a PIL image of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :param use_scaling: Whether to use the scaling factor of Windows to scale the image.
    :return: A PIL image of the window with the given ID.
    """

    if use_scaling:
        scaling = SCALE_FACTOR / 100
    else:
        scaling = 1.0

    left, top, right, bot = win32gui.GetClientRect(window_id)
    w = int((right - left) * scaling)
    h = int((bot - top) * scaling)

    hwndDC = win32gui.GetWindowDC(window_id)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(window_id, saveDC.GetSafeHdc(), 3)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

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

def get_window_pos(window_id):
    """
    Returns the position of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :return: The position of the window with the given ID.
    """
    _, _, left, top = win32gui.GetClientRect(window_id)
    return left, top

if __name__ == "__main__":
    # Capture the entire screen
    # screen_pixels = capture_pixels("VLC")
    # if screen_pixels:
    #     screen_pixels.save("data/tmp.png")

    # Capture a specific window
    window_id = get_window_by_title("Tokimeki Memorial")
    window_pixels = get_window_image(window_id)
    if window_pixels:
        window_pixels.save("data/tmp/ss.png")

    # tik = time.perf_counter()
    # for _ in range(100):
    #     window_id = get_window_by_title("Tokimeki Memorial")
    #     window_pixels = get_window_image(window_id)
    # tok = time.perf_counter()
    # print(f"Capturing the window took {(tok - tik)/100*1000} miliseconds on average.")
