"""OmniRemote - Linux uinput Input Driver
Low-level direct kernel input injection for Linux (Wayland / X11).
"""
import fcntl
import os
import shutil
import struct
import subprocess
import time
from .base import BaseInput

# Linux uinput constants
UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_RELBIT = 0x40045566
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02

REL_X = 0x00
REL_Y = 0x01
REL_WHEEL = 0x08
REL_HWHEEL = 0x06

BTN_LEFT = 0x110
BTN_RIGHT = 0x111
BTN_MIDDLE = 0x112
KEY_LEFTCTRL = 29

KEY_MAP = {
    # Navigation & Slides
    "Right": 106, "Left": 105, "Up": 103, "Down": 108,
    "Page_Down": 109, "Page_Up": 104, "Next": 109, "Prior": 104,
    "Home": 102, "End": 107,

    # Control & Editing
    "Escape": 1, "Esc": 1,
    "Return": 28, "Enter": 28,
    "space": 57, "Space": 57,
    "BackSpace": 14,
    "Tab": 15,
    "Delete": 111,

    # Function Keys
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,

    # Media Keys
    "PlayPause": 164, "XF86AudioPlay": 164, "XF86AudioPause": 164,
    "NextSong": 163, "XF86AudioNext": 163,
    "PrevSong": 165, "XF86AudioPrev": 165,
    "VolumeMute": 113, "XF86AudioMute": 113,
    "VolumeDown": 114, "XF86AudioLowerVolume": 114,
    "VolumeUp": 115, "XF86AudioRaiseVolume": 115,

    # Modifiers
    "ctrl": 29, "Control_L": 29, "Control_R": 97,
    "shift": 42, "Shift_L": 42, "Shift_R": 54,
    "alt": 56, "Alt_L": 56, "Alt_R": 100,
    "super": 125, "win": 125,

    # Letters
    "a": 30, "b": 48, "c": 46, "d": 32, "e": 18, "f": 33, "g": 34,
    "h": 35, "i": 23, "j": 36, "k": 37, "l": 38, "m": 50, "n": 49,
    "o": 24, "p": 25, "q": 16, "r": 19, "s": 31, "t": 20, "u": 22,
    "v": 47, "w": 17, "x": 45, "y": 21, "z": 44,
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18, "F": 33, "G": 34,
    "H": 35, "I": 23, "J": 36, "K": 37, "L": 38, "M": 50, "N": 49,
    "O": 24, "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20, "U": 22,
    "V": 47, "W": 17, "X": 45, "Y": 21, "Z": 44,

    # Numbers
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,

    # Symbols
    "minus": 12, "-": 12,
    "equal": 13, "=": 13,
    "bracketleft": 26, "[": 26,
    "bracketright": 27, "]": 27,
    "semicolon": 39, ";": 39,
    "apostrophe": 40, "'": 40,
    "grave": 41, "`": 41,
    "backslash": 43, "\\": 43,
    "comma": 51, ",": 51,
    "period": 52, ".": 52,
    "slash": 53, "/": 53,
}


class LinuxUInput(BaseInput):
    def __init__(self):
        self.mouse_fd = None
        self.kbd_fd = None
        self._init_mouse()
        self._init_keyboard()

    def _init_mouse(self):
        try:
            self.mouse_fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
            fcntl.ioctl(self.mouse_fd, UI_SET_EVBIT, EV_REL)
            fcntl.ioctl(self.mouse_fd, UI_SET_RELBIT, REL_X)
            fcntl.ioctl(self.mouse_fd, UI_SET_RELBIT, REL_Y)
            fcntl.ioctl(self.mouse_fd, UI_SET_RELBIT, REL_WHEEL)
            fcntl.ioctl(self.mouse_fd, UI_SET_RELBIT, REL_HWHEEL)

            fcntl.ioctl(self.mouse_fd, UI_SET_EVBIT, EV_KEY)
            for btn in [BTN_LEFT, BTN_RIGHT, BTN_MIDDLE]:
                fcntl.ioctl(self.mouse_fd, UI_SET_KEYBIT, btn)

            name = b"OmniRemote Touchpad\x00" + b"\x00" * 59
            id_struct = struct.pack("HHHH", 0x03, 0x1234, 0x5678, 0x01)
            uinput_user_dev = name + id_struct + b"\x00" * (1116 - len(name) - len(id_struct))

            os.write(self.mouse_fd, uinput_user_dev)
            fcntl.ioctl(self.mouse_fd, UI_DEV_CREATE)
            print("✓ [OmniRemote] Ratón virtual activo (/dev/uinput)")
        except Exception as e:
            print(f"⚠ [OmniRemote] Error al crear ratón en /dev/uinput: {e}")
            if self.mouse_fd is not None:
                os.close(self.mouse_fd)
                self.mouse_fd = None

    def _init_keyboard(self):
        try:
            self.kbd_fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
            fcntl.ioctl(self.kbd_fd, UI_SET_EVBIT, EV_KEY)
            for k in range(1, 248):
                fcntl.ioctl(self.kbd_fd, UI_SET_KEYBIT, k)

            name = b"OmniRemote Keyboard\x00" + b"\x00" * 59
            id_struct = struct.pack("HHHH", 0x03, 0x1234, 0x5679, 0x01)
            uinput_user_dev = name + id_struct + b"\x00" * (1116 - len(name) - len(id_struct))

            os.write(self.kbd_fd, uinput_user_dev)
            fcntl.ioctl(self.kbd_fd, UI_DEV_CREATE)
            print("✓ [OmniRemote] Teclado virtual activo (/dev/uinput)")
        except Exception as e:
            print(f"⚠ [OmniRemote] Error al crear teclado en /dev/uinput: {e}")
            if self.kbd_fd is not None:
                os.close(self.kbd_fd)
                self.kbd_fd = None

    def _emit(self, fd, ev_type, code, val):
        if fd is not None:
            data = struct.pack("qqHHi", 0, 0, ev_type, code, int(val))
            os.write(fd, data)

    def move(self, dx: float, dy: float) -> None:
        if self.mouse_fd is not None:
            self._emit(self.mouse_fd, EV_REL, REL_X, dx)
            self._emit(self.mouse_fd, EV_REL, REL_Y, dy)
            self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def click(self, button: str, press: bool = True) -> None:
        if self.mouse_fd is not None:
            code = BTN_RIGHT if button == "right" else (BTN_MIDDLE if button == "middle" else BTN_LEFT)
            if press:
                self._emit(self.mouse_fd, EV_KEY, code, 1)
                self._emit(self.mouse_fd, EV_SYN, 0, 0)
                self._emit(self.mouse_fd, EV_KEY, code, 0)
                self._emit(self.mouse_fd, EV_SYN, 0, 0)
            else:
                self._emit(self.mouse_fd, EV_KEY, code, 0)
                self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def button_down(self, button: str) -> None:
        if self.mouse_fd is not None:
            code = BTN_RIGHT if button == "right" else (BTN_MIDDLE if button == "middle" else BTN_LEFT)
            self._emit(self.mouse_fd, EV_KEY, code, 1)
            self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def button_up(self, button: str) -> None:
        if self.mouse_fd is not None:
            code = BTN_RIGHT if button == "right" else (BTN_MIDDLE if button == "middle" else BTN_LEFT)
            self._emit(self.mouse_fd, EV_KEY, code, 0)
            self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def scroll(self, dx: float, dy: float) -> None:
        if self.mouse_fd is not None:
            if dy != 0:
                self._emit(self.mouse_fd, EV_REL, REL_WHEEL, dy)
            if dx != 0:
                self._emit(self.mouse_fd, EV_REL, REL_HWHEEL, dx)
            self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def zoom(self, factor: float) -> None:
        if self.mouse_fd is not None:
            val = 1 if factor > 0 else -1
            if self.kbd_fd is not None:
                self._emit(self.kbd_fd, EV_KEY, KEY_LEFTCTRL, 1)
                self._emit(self.kbd_fd, EV_SYN, 0, 0)
                self._emit(self.mouse_fd, EV_REL, REL_WHEEL, val)
                self._emit(self.mouse_fd, EV_SYN, 0, 0)
                self._emit(self.kbd_fd, EV_KEY, KEY_LEFTCTRL, 0)
                self._emit(self.kbd_fd, EV_SYN, 0, 0)
            else:
                self._emit(self.mouse_fd, EV_REL, REL_WHEEL, val)
                self._emit(self.mouse_fd, EV_SYN, 0, 0)

    def tap_key(self, key_name: str) -> None:
        code = KEY_MAP.get(key_name)
        if code and self.kbd_fd is not None:
            self._emit(self.kbd_fd, EV_KEY, code, 1)
            self._emit(self.kbd_fd, EV_SYN, 0, 0)
            time.sleep(0.012)
            self._emit(self.kbd_fd, EV_KEY, code, 0)
            self._emit(self.kbd_fd, EV_SYN, 0, 0)

    def key_combo(self, modifiers: list[str], key_name: str) -> None:
        code = KEY_MAP.get(key_name)
        if not code or self.kbd_fd is None:
            return

        mod_codes = [KEY_MAP.get(m) for m in modifiers if KEY_MAP.get(m)]
        for m in mod_codes:
            self._emit(self.kbd_fd, EV_KEY, m, 1)
        if mod_codes:
            self._emit(self.kbd_fd, EV_SYN, 0, 0)
            time.sleep(0.02)

        self._emit(self.kbd_fd, EV_KEY, code, 1)
        self._emit(self.kbd_fd, EV_SYN, 0, 0)
        time.sleep(0.025)
        self._emit(self.kbd_fd, EV_KEY, code, 0)
        self._emit(self.kbd_fd, EV_SYN, 0, 0)

        if mod_codes:
            time.sleep(0.02)
        for m in reversed(mod_codes):
            self._emit(self.kbd_fd, EV_KEY, m, 0)
        if mod_codes:
            self._emit(self.kbd_fd, EV_SYN, 0, 0)

    def type_text(self, text: str) -> None:
        # Check if single ASCII char can be typed via uinput directly
        if len(text) == 1:
            char = text
            if char in KEY_MAP:
                is_upper = char.isupper()
                mods = ['shift'] if is_upper else []
                self.key_combo(mods, char)
                return
            elif char == ' ':
                self.tap_key('space')
                return
            elif char == '\n':
                self.tap_key('Return')
                return

        # Multi-char or Unicode: wtype or clipboard fallback
        if shutil.which("wtype"):
            try:
                subprocess.run(["wtype", "--", text], check=True, timeout=1.0)
                return
            except Exception:
                pass

        # Clipboard paste fallback
        if shutil.which("wl-copy"):
            try:
                p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode('utf-8'), timeout=1.0)
                self.smart_paste()
            except Exception:
                pass

    def smart_paste(self) -> None:
        # Default smart paste: Ctrl+V or Ctrl+Shift+V
        self.key_combo(["ctrl"], "v")

    def close(self):
        if self.mouse_fd is not None:
            try:
                fcntl.ioctl(self.mouse_fd, UI_DEV_DESTROY)
                os.close(self.mouse_fd)
            except Exception:
                pass
            self.mouse_fd = None
        if self.kbd_fd is not None:
            try:
                fcntl.ioctl(self.kbd_fd, UI_DEV_DESTROY)
                os.close(self.kbd_fd)
            except Exception:
                pass
            self.kbd_fd = None
