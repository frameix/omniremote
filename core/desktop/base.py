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

    def start_presentation(self, input_driver) -> None:
        """Starts a presentation adapting to the active window (Google Slides, ONLYOFFICE, Canva, LibreOffice, PowerPoint)."""
        cls, title = self.get_active_window()
        cls = (cls or "").lower()
        title = (title or "").lower()

        browser_classes = ("chrome", "brave", "firefox", "chromium", "zen", "vivaldi", "edge", "opera")
        is_browser = any(b in cls for b in browser_classes)

        is_onlyoffice = "onlyoffice" in cls or "onlyoffice" in title or "desktopeditors" in cls
        is_google_slides = "google slides" in title or "slides.google" in title or (is_browser and any(w in title for w in ("slides", "presentaci", "diapositiva")))

        # 1. Google Slides y ONLYOFFICE: Ctrl + F5 (Inicia la presentación de diapositivas)
        if is_google_slides or is_onlyoffice:
            input_driver.key_combo(["ctrl"], "F5")
        # 2. Canva web: Ctrl + Alt + P
        elif "canva" in title or (is_browser and "canva" in cls):
            input_driver.key_combo(["ctrl", "alt"], "p")
        # 3. Suites de escritorio estándar (LibreOffice Impress, PowerPoint, PDF Okular/Evince): F5
        else:
            input_driver.tap_key("F5")

    def smart_copy(self, input_driver) -> None:
        """Performs context-aware copy: Ctrl+Shift+C in terminals, Ctrl+C elsewhere."""
        cls, _ = self.get_active_window()
        cls = (cls or "").lower()
        terminal_classes = ("kitty", "alacritty", "foot", "wezterm", "gnome-terminal", "konsole", "xterm")
        if any(term in cls for term in terminal_classes):
            input_driver.key_combo(["ctrl", "shift"], "c")
        else:
            input_driver.key_combo(["ctrl"], "c")

    def smart_paste(self, input_driver) -> None:
        """Performs context-aware paste: Ctrl+Shift+V in terminals, Ctrl+V elsewhere."""
        cls, _ = self.get_active_window()
        cls = (cls or "").lower()
        terminal_classes = ("kitty", "alacritty", "foot", "wezterm", "gnome-terminal", "konsole", "xterm")
        if any(term in cls for term in terminal_classes):
            input_driver.key_combo(["ctrl", "shift"], "v")
        else:
            input_driver.key_combo(["ctrl"], "v")
