"""OmniRemote - Windows SendInput Driver
Ultra low-latency native Win32 input injection via ctypes.
Zero extra dependencies, runs out of the box on Windows 10/11.
"""
import sys
from .base import BaseInput

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Win32 Constants
    INPUT_MOUSE = 0
    INPUT_KEYBOARD = 1

    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0009
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    MOUSEEVENTF_WHEEL = 0x0800
    MOUSEEVENTF_HWHEEL = 0x1000

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004

    # Win32 Structures
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong)
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong)
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD)
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT)
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("union", INPUT_UNION)
        ]

    WIN_VK_MAP = {
        "Escape": 0x1B, "Return": 0x0D, "Tab": 0x09, "BackSpace": 0x08,
        "space": 0x20, "Delete": 0x2E,
        "Left": 0x25, "Up": 0x26, "Right": 0x27, "Down": 0x28,
        "Page_Up": 0x21, "Page_Down": 0x22, "Home": 0x24, "End": 0x23,
        "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73, "F5": 0x74,
        "ctrl": 0x11, "shift": 0x10, "alt": 0x12, "win": 0x5B
    }


class WindowsSendInput(BaseInput):
    def __init__(self):
        if sys.platform != "win32":
            raise RuntimeError("WindowsSendInput solo puede ejecutarse en Windows.")
        self.user32 = ctypes.windll.user32

    def _send_input(self, inp):
        self.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def move(self, dx: float, dy: float) -> None:
        inp = INPUT(type=INPUT_MOUSE)
        inp.union.mi.dx = int(dx)
        inp.union.mi.dy = int(dy)
        inp.union.mi.dwFlags = MOUSEEVENTF_MOVE
        self._send_input(inp)

    def click(self, button: str, press: bool = True) -> None:
        down_flag = MOUSEEVENTF_LEFTDOWN if button == "left" else (
            MOUSEEVENTF_RIGHTDOWN if button == "right" else MOUSEEVENTF_MIDDLEDOWN
        )
        up_flag = MOUSEEVENTF_LEFTUP if button == "left" else (
            MOUSEEVENTF_RIGHTUP if button == "right" else MOUSEEVENTF_MIDDLEUP
        )

        inp = INPUT(type=INPUT_MOUSE)
        inp.union.mi.dwFlags = down_flag
        self._send_input(inp)
        if press:
            inp.union.mi.dwFlags = up_flag
            self._send_input(inp)

    def button_down(self, button: str) -> None:
        flag = MOUSEEVENTF_LEFTDOWN if button == "left" else (
            MOUSEEVENTF_RIGHTDOWN if button == "right" else MOUSEEVENTF_MIDDLEDOWN
        )
        inp = INPUT(type=INPUT_MOUSE)
        inp.union.mi.dwFlags = flag
        self._send_input(inp)

    def button_up(self, button: str) -> None:
        flag = MOUSEEVENTF_LEFTUP if button == "left" else (
            MOUSEEVENTF_RIGHTUP if button == "right" else MOUSEEVENTF_MIDDLEUP
        )
        inp = INPUT(type=INPUT_MOUSE)
        inp.union.mi.dwFlags = flag
        self._send_input(inp)

    def scroll(self, dx: float, dy: float) -> None:
        if dy != 0:
            inp = INPUT(type=INPUT_MOUSE)
            inp.union.mi.dwFlags = MOUSEEVENTF_WHEEL
            inp.union.mi.mouseData = int(dy * 120)
            self._send_input(inp)
        if dx != 0:
            inp = INPUT(type=INPUT_MOUSE)
            inp.union.mi.dwFlags = MOUSEEVENTF_HWHEEL
            inp.union.mi.mouseData = int(dx * 120)
            self._send_input(inp)

    def zoom(self, factor: float) -> None:
        # Hold Ctrl and scroll
        ctrl_vk = 0x11
        # Down
        inp_k = INPUT(type=INPUT_KEYBOARD)
        inp_k.union.ki.wVk = ctrl_vk
        self._send_input(inp_k)

        # Scroll
        inp_m = INPUT(type=INPUT_MOUSE)
        inp_m.union.mi.dwFlags = MOUSEEVENTF_WHEEL
        inp_m.union.mi.mouseData = 120 if factor > 0 else -120
        self._send_input(inp_m)

        # Up
        inp_k.union.ki.dwFlags = KEYEVENTF_KEYUP
        self._send_input(inp_k)

    def tap_key(self, key_name: str) -> None:
        vk = WIN_VK_MAP.get(key_name)
        if not vk and len(key_name) == 1:
            vk = ord(key_name.upper())

        if vk:
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.union.ki.wVk = vk
            self._send_input(inp)
            inp.union.ki.dwFlags = KEYEVENTF_KEYUP
            self._send_input(inp)

    def type_text(self, text: str) -> None:
        for char in text:
            # Unicode character injection
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.union.ki.wScan = ord(char)
            inp.union.ki.dwFlags = KEYEVENTF_UNICODE
            self._send_input(inp)
            inp.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            self._send_input(inp)

    def key_combo(self, modifiers: list[str], key_name: str) -> None:
        mod_vks = [WIN_VK_MAP.get(m) for m in modifiers if WIN_VK_MAP.get(m)]
        key_vk = WIN_VK_MAP.get(key_name)
        if not key_vk and len(key_name) == 1:
            key_vk = ord(key_name.upper())

        # Press modifiers
        for vk in mod_vks:
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.union.ki.wVk = vk
            self._send_input(inp)

        # Press key
        if key_vk:
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.union.ki.wVk = key_vk
            self._send_input(inp)
            inp.union.ki.dwFlags = KEYEVENTF_KEYUP
            self._send_input(inp)

        # Release modifiers
        for vk in reversed(mod_vks):
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.union.ki.wVk = vk
            inp.union.ki.dwFlags = KEYEVENTF_KEYUP
            self._send_input(inp)

    def smart_paste(self) -> None:
        self.key_combo(["ctrl"], "v")
