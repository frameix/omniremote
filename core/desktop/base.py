"""OmniRemote - Base Desktop Environment Interface
Abstract contract for window manager / desktop environment specific operations.
"""
from abc import ABC, abstractmethod


class BaseDesktop(ABC):
    @abstractmethod
    def switch_workspace(self, delta: int) -> None:
        """Switch workspace relatively (e.g. +1 for next, -1 for previous)."""
        pass

    @abstractmethod
    def get_active_window(self) -> tuple[str, str]:
        """Returns (window_class, window_title) of the focused application."""
        pass

    @abstractmethod
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen on the focused window."""
        pass
