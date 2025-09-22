"""Error message windows.

Currently we are using xdialog, but this could change.
"""

from __future__ import annotations

import xdialog


def display_error(window_title: str, message: str) -> None:
    """Display an error message with the given window title and message."""
    xdialog.error(window_title, message)
