"""OmniRemote - Desktop Environment Detector
Automatically selects the optimal desktop backend based on OS and environment variables.
"""
import os
import shutil
import sys
from .base import BaseDesktop
from .generic import GenericDesktop
from .hyprland import HyprlandDesktop
from .niri import NiriDesktop
from .sway import SwayDesktop


def get_desktop_backend(input_driver=None) -> BaseDesktop:
    if sys.platform == "win32":
        return GenericDesktop(input_driver)

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()

    if "hyprland" in desktop or "hyprland" in session or shutil.which("hyprctl"):
        if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
            return HyprlandDesktop()

    if "niri" in desktop or shutil.which("niri"):
        if os.environ.get("NIRI_SOCKET"):
            return NiriDesktop()

    if "sway" in desktop or shutil.which("swaymsg"):
        if os.environ.get("SWAYSOCK"):
            return SwayDesktop()

    return GenericDesktop(input_driver)
