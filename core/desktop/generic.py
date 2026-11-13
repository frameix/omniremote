"""OmniRemote - Generic Desktop Backend
Fallback backend using standard OS hotkeys (KDE, GNOME, Windows, XFCE).
"""
import sys
from .base import BaseDesktop


class GenericDesktop(BaseDesktop):
    def __init__(self, input_driver=None):
        self.input_driver = input_driver

    def switch_workspace(self, delta: int) -> None:
        if not self.input_driver:
            return

        # Windows workspace switch: Ctrl+Win+Left / Ctrl+Win+Right
        if sys.platform == "win32":
            key = "Right" if delta > 0 else "Left"
            self.input_driver.key_combo(["ctrl", "win"], key)
        else:
            # Linux GNOME / KDE generic fallback: Super+Page_Down / Super+Page_Up
            key = "Page_Down" if delta > 0 else "Page_Up"
            self.input_driver.key_combo(["super"], key)

    def get_active_window(self) -> tuple[str, str]:
        return "", ""

    def toggle_fullscreen(self) -> None:
        if self.input_driver:
            self.input_driver.tap_key("F11")
