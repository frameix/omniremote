"""OmniRemote - Base Input Driver Interface
Abstract contract for OS-specific input emulators.
"""
from abc import ABC, abstractmethod


class BaseInput(ABC):
    @abstractmethod
    def move(self, dx: float, dy: float) -> None:
        """Move cursor by relative delta (dx, dy)."""
        pass

    @abstractmethod
    def click(self, button: str, press: bool = True) -> None:
        """Click or hold/release mouse button ('left', 'right', 'middle')."""
        pass

    @abstractmethod
    def scroll(self, dx: float, dy: float) -> None:
        """Scroll horizontally and/or vertically."""
        pass

    @abstractmethod
    def zoom(self, factor: float) -> None:
        """Zoom in or out."""
        pass

    @abstractmethod
    def tap_key(self, key_name: str) -> None:
        """Tap a single hardware key (e.g. 'Return', 'Escape', 'Up')."""
        pass

    @abstractmethod
    def type_text(self, text: str) -> None:
        """Type arbitrary text."""
        pass

    @abstractmethod
    def key_combo(self, modifiers: list[str], key_name: str) -> None:
        """Trigger key combination (e.g. modifiers=['ctrl', 'shift'], key='c')."""
        pass

    @abstractmethod
    def smart_paste(self) -> None:
        """Paste clipboard content intelligently."""
        pass
