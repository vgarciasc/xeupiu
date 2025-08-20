from xeupiu.config import CONFIG
from PIL import Image
import ewmhlib
import Xlib

BASE_DIMS = [None, None, None, None]

_e_root = ewmhlib.defaultEwmhRoot
_root = ewmhlib.defaultRoot

def get_window_by_title(window_title) -> int:
    """Returns the window ID of the window with the given title.
    If there are multiple windows with the same title, returns the first one.

    :param window_title: The title of the window to search for.
    :return: The window ID of the window with the given title.
    """
    for client_id in _e_root.getClientList():
        win = ewmhlib.EwmhWindow(client_id)
        if win.getName().startswith(window_title):
            return client_id
    raise ValueError(f"Window with title '{window_title}' not found.")

def _get_xwin(window_id) -> Xlib.xobject.drawable.Window:
    win = ewmhlib.EwmhWindow(window_id)
    wm_state = win.getWmState(True)
    if ewmhlib.Props.State.HIDDEN in wm_state:
        raise RuntimeError("Window is minimized!")
    xwin = win.xWindow
    return xwin


def get_window_image(window_id, offset_x=(0, 0), offset_y=(0, 0)) -> Image.Image:
    """
    Returns a PIL image of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :return: A PIL image of the window with the given ID.
    """
    xwin = _get_xwin(window_id)
    geometry = xwin.get_geometry()

    # these are the duckstation borders
    border_config = CONFIG.get_borders_var()
    top_offset = border_config["size_toolbar"]
    bottom_offset = border_config["size_window_border_bottom"]

    # grab X buffer
    x = geometry.x + offset_x[0]
    y = geometry.y + top_offset + offset_y[0]
    w = geometry.width - offset_x[1]
    h = geometry.height - top_offset - bottom_offset - offset_y[1]
    raw = xwin.get_image(x, y, w, h, Xlib.X.ZPixmap, 0xffffffff)  # all planes

    # convert to pillow image
    image = Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX", 0, 1)
    return image


def get_window_base_dims(window_id: int) -> tuple[int, int, int, int]:
    """
    Returns the position and size of the window with the given ID.

    :param window_id: The window ID of the window to capture.
    :return: The position of the window with the given ID.
    """
    xwin = _get_xwin(window_id)
    geometry = xwin.get_geometry()

    translated_coords = xwin.translate_coords(_root, geometry.x, geometry.y)
    xt = -translated_coords.x
    yt = -translated_coords.y
    return (
        xt,
        yt,
        geometry.width,
        geometry.height,
    )
