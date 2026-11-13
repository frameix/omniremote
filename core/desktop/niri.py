"""OmniRemote - Niri Desktop Backend
Interfaces with Niri IPC via niri msg.
"""
import subprocess
from .base import BaseDesktop


class NiriDesktop(BaseDesktop):
    def switch_workspace(self, delta: int) -> None:
        action = "focus-workspace-down" if delta > 0 else "focus-workspace-up"
        try:
            subprocess.Popen(["niri", "msg", "action", action])
        except Exception as e:
            print(f"[NiriDesktop] Error switching workspace: {e}")

    def get_active_window(self) -> tuple[str, str]:
        # Niri active window query
        try:
            out = subprocess.check_output(["niri", "msg", "focused-window"], timeout=0.25).decode()
            return "", out.lower()
        except Exception:
            return "", ""

    def toggle_fullscreen(self) -> None:
        try:
            subprocess.Popen(["niri", "msg", "action", "maximize-column"])
        except Exception as e:
            print(f"[NiriDesktop] Error fullscreen: {e}")
