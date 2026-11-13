"""OmniRemote - Sway / i3 Desktop Backend
Interfaces with Sway / i3 IPC via swaymsg.
"""
import json
import subprocess
from .base import BaseDesktop


class SwayDesktop(BaseDesktop):
    def switch_workspace(self, delta: int) -> None:
        cmd = "next" if delta > 0 else "prev"
        try:
            subprocess.Popen(["swaymsg", "workspace", cmd])
        except Exception as e:
            print(f"[SwayDesktop] Error switching workspace: {e}")

    def get_active_window(self) -> tuple[str, str]:
        try:
            out = subprocess.check_output(["swaymsg", "-t", "get_tree"], timeout=0.3)
            # Find focused node in Sway tree
            data = json.loads(out)
            return self._find_focused(data)
        except Exception:
            return "", ""

    def _find_focused(self, node) -> tuple[str, str]:
        if node.get("focused"):
            app_id = node.get("app_id") or node.get("window_properties", {}).get("class", "")
            name = node.get("name", "")
            return str(app_id).lower(), str(name).lower()
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            res = self._find_focused(child)
            if res != ("", ""):
                return res
        return "", ""

    def toggle_fullscreen(self) -> None:
        try:
            subprocess.Popen(["swaymsg", "fullscreen", "toggle"])
        except Exception as e:
            print(f"[SwayDesktop] Error fullscreen: {e}")
