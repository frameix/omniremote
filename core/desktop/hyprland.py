"""OmniRemote - Hyprland Desktop Backend
Interfaces with Hyprland IPC socket via hyprctl.
"""
import json
import subprocess
from .base import BaseDesktop


class HyprlandDesktop(BaseDesktop):
    def switch_workspace(self, delta: int) -> None:
        cmd = f"+{abs(delta)}" if delta > 0 else f"-{abs(delta)}"
        try:
            subprocess.Popen(["hyprctl", "dispatch", f'hl.dsp.focus({{ workspace = "{cmd}" }})'])
        except Exception:
            # Fallback for standard Hyprland dispatch
            try:
                subprocess.Popen(["hyprctl", "dispatch", "workspace", f"e{cmd}"])
            except Exception as e:
                print(f"[HyprlandDesktop] Error switching workspace: {e}")

    def get_active_window(self) -> tuple[str, str]:
        try:
            out = subprocess.check_output(["hyprctl", "activewindow", "-j"], timeout=0.25)
            data = json.loads(out)
            cls = data.get("class", "").lower()
            title = data.get("title", "").lower()
            return cls, title
        except Exception:
            return "", ""

    def toggle_fullscreen(self) -> None:
        try:
            subprocess.Popen(["hyprctl", "dispatch", 'hl.dsp.window.fullscreen({ mode = "fullscreen" })'])
        except Exception:
            try:
                subprocess.Popen(["hyprctl", "dispatch", "fullscreen", "1"])
            except Exception as e:
                print(f"[HyprlandDesktop] Error fullscreen: {e}")
