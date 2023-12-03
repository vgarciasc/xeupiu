from ctypes import windll

import pygetwindow as gw
import win32gui
import win32ui
from PIL import ImageGrab, Image

def capture_pixels(window_title=None):
    if window_title:
        window = gw.getWindowsWithTitle(window_title)
        if not window:
            print(f"Window with title '{window_title}' not found.")
            return None
        window = window[0]

        window.activate()
        screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
    else:
        screenshot = ImageGrab.grab()

    return screenshot

def get_window_by_title(window_title):
    toplist, winlist = [], []

    def enum_cb(hwnd, _):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)
    window = [(hwnd, title) for hwnd, title in winlist if window_title.lower() in title.lower()]
    window_id, window_name = window[0]

    return window_id

def get_window_image(hwnd, use_scaling=True):
    if use_scaling:
        scaling = windll.shcore.GetScaleFactorForDevice(0) / 100
    else:
        scaling = 1.0

    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = int((right - left) * scaling)
    h = int((bot - top) * scaling)

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def get_window_pos(window_id):
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
