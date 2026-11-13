"""OmniRemote - Linux Native System Tray & Floating QR Window
Uses GTK3 and AyatanaAppIndicator3 via PyGObject.
Integrates with Waybar (Hyprland), Sway, GNOME, KDE Plasma.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import AyatanaAppIndicator3 as appindicator
from gi.repository import GLib, Gdk, GdkPixbuf, Gtk


class LinuxTrayApp:
    def __init__(self, local_url: str, on_quit_callback=None):
        self.local_url = local_url
        self.on_quit_callback = on_quit_callback
        self.qr_path = os.path.join(tempfile.gettempdir(), "omniremote_qr.png")

        self._generate_qr()
        self._build_floating_window()
        self._build_tray_indicator()

    def _generate_qr(self):
        if shutil.which("qrencode"):
            try:
                subprocess.run(
                    ["qrencode", "-s", "8", "-m", "2", "-o", self.qr_path, self.local_url],
                    check=True,
                    timeout=2.0
                )
            except Exception as e:
                print(f"[OmniRemote Tray] Error generando QR: {e}")

    def _build_floating_window(self):
        self.window = Gtk.Window(title="OmniRemote")
        self.window.set_default_size(360, 480)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_resizable(False)

        # Intercept close button to hide to tray instead of quitting
        self.window.connect("delete-event", self._on_window_delete)

        # Modern Dark CSS
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: #0b0e14;
            color: #e6edf3;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .header-title {
            font-size: 20px;
            font-weight: 800;
            color: #00f2fe;
            margin-top: 16px;
        }
        .subtitle {
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 12px;
        }
        .url-box {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 700;
            color: #4facfe;
        }
        .status-badge {
            font-size: 11px;
            color: #3fb950;
            font-weight: 600;
            margin-top: 6px;
        }
        .btn-hide {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            color: #000;
            font-weight: 700;
            border-radius: 8px;
            border: none;
            padding: 8px 18px;
            margin-bottom: 16px;
        }
        .btn-hide:hover {
            opacity: 0.9;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)

        # Header Title
        lbl_title = Gtk.Label(label="📱 OmniRemote")
        lbl_title.get_style_context().add_class("header-title")
        main_box.pack_start(lbl_title, False, False, 0)

        lbl_sub = Gtk.Label(label="Escanea desde tu móvil (en la misma red WiFi)")
        lbl_sub.get_style_context().add_class("subtitle")
        main_box.pack_start(lbl_sub, False, False, 0)

        # QR Code Image
        if os.path.exists(self.qr_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.qr_path, 230, 230, True)
            img_qr = Gtk.Image.new_from_pixbuf(pixbuf)
            main_box.pack_start(img_qr, False, False, 6)

        # Local URL Box
        lbl_url = Gtk.Label(label=self.local_url)
        lbl_url.set_selectable(True)
        lbl_url.get_style_context().add_class("url-box")
        main_box.pack_start(lbl_url, False, False, 4)

        # Status Label
        self.lbl_status = Gtk.Label(label="⚡ Listo para conectar")
        self.lbl_status.get_style_context().add_class("status-badge")
        main_box.pack_start(self.lbl_status, False, False, 2)

        # Hide to tray button
        btn_hide = Gtk.Button(label="Ocultar a la Barra (Tray)")
        btn_hide.get_style_context().add_class("btn-hide")
        btn_hide.connect("clicked", lambda _: self.window.hide())
        main_box.pack_start(btn_hide, False, False, 8)

        self.window.add(main_box)

    def _build_tray_indicator(self):
        # AyatanaAppIndicator
        self.indicator = appindicator.Indicator.new(
            "omniremote-indicator",
            "input-touchpad",
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        menu = Gtk.Menu()

        item_qr = Gtk.MenuItem(label="📱 Mostrar Código QR / Enlace")
        item_qr.connect("activate", self._show_window)
        menu.append(item_qr)

        item_open = Gtk.MenuItem(label="🌐 Abrir en Navegador Local")
        item_open.connect("activate", self._open_browser)
        menu.append(item_open)

        item_copy = Gtk.MenuItem(label="📋 Copiar Enlace Móvil")
        item_copy.connect("activate", self._copy_url)
        menu.append(item_copy)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="🚪 Salir de OmniRemote")
        item_quit.connect("activate", self._quit)
        menu.append(item_quit)

        menu.show_all()
        self.indicator.set_menu(menu)

    def _on_window_delete(self, widget, event):
        self.window.hide()
        return True  # Do not destroy window

    def _show_window(self, _):
        self.window.show_all()
        self.window.present()

    def _open_browser(self, _):
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", self.local_url])

    def _copy_url(self, _):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.local_url, -1)
        clipboard.store()

    def update_clients_count(self, count: int):
        GLib.idle_add(self._update_status_ui, count)

    def _update_status_ui(self, count: int):
        if count > 0:
            self.lbl_status.set_text(f"🟢 {count} dispositivo(s) conectado(s)")
            self.indicator.set_title(f"OmniRemote ({count})")
        else:
            self.lbl_status.set_text("⚡ Listo para conectar")
            self.indicator.set_title("")

    def run(self):
        self.window.show_all()
        self.window.present()
        Gtk.main()

    def _quit(self, _):
        if self.on_quit_callback:
            self.on_quit_callback()
        Gtk.main_quit()
