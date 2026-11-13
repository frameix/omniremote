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
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "omniremote.png")

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

        if os.path.exists(self.icon_path):
            try:
                self.window.set_icon_from_file(self.icon_path)
            except Exception:
                pass

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
        }
        .subtitle {
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 10px;
        }
        .url-box {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 5px 8px 5px 14px;
        }
        .url-text {
            font-size: 13px;
            font-weight: 700;
            color: #4facfe;
        }
        .btn-copy {
            background: rgba(0, 242, 254, 0.12);
            border: 1px solid rgba(0, 242, 254, 0.35);
            color: #00f2fe;
            border-radius: 7px;
            font-size: 11px;
            font-weight: 700;
            padding: 5px 12px;
            transition: all 0.2s ease;
        }
        .btn-copy:hover {
            background: rgba(0, 242, 254, 0.25);
            border-color: #00f2fe;
        }
        .btn-copy.copied {
            background: rgba(63, 185, 80, 0.2);
            border-color: #3fb950;
            color: #3fb950;
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
            padding: 9px 18px;
            margin-bottom: 14px;
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
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)

        # Header Box with Logo + Title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_top(12)

        if os.path.exists(self.icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.icon_path, 30, 30, True)
                img_logo = Gtk.Image.new_from_pixbuf(pixbuf)
                header_box.pack_start(img_logo, False, False, 0)
            except Exception:
                pass

        lbl_title = Gtk.Label(label="OmniRemote")
        lbl_title.get_style_context().add_class("header-title")
        header_box.pack_start(lbl_title, False, False, 0)

        main_box.pack_start(header_box, False, False, 0)

        lbl_sub = Gtk.Label(label="Escanea desde tu móvil (en la misma red WiFi)")
        lbl_sub.get_style_context().add_class("subtitle")
        main_box.pack_start(lbl_sub, False, False, 0)

        # QR Code Image
        if os.path.exists(self.qr_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.qr_path, 230, 230, True)
            img_qr = Gtk.Image.new_from_pixbuf(pixbuf)
            main_box.pack_start(img_qr, False, False, 6)

        # Local URL Box with Quick Copy Button
        url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        url_box.get_style_context().add_class("url-box")

        lbl_url = Gtk.Label(label=self.local_url)
        lbl_url.set_xalign(0.0)
        lbl_url.get_style_context().add_class("url-text")
        url_box.pack_start(lbl_url, True, True, 0)

        self.btn_copy = Gtk.Button(label="📋 Copiar")
        self.btn_copy.get_style_context().add_class("btn-copy")
        self.btn_copy.connect("clicked", self._on_copy_clicked)
        url_box.pack_start(self.btn_copy, False, False, 0)

        main_box.pack_start(url_box, False, False, 4)

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

    def _on_copy_clicked(self, btn):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.local_url, -1)
        clipboard.store()

        btn.get_style_context().add_class("copied")
        btn.set_label("✓ Copiado")

        GLib.timeout_add(1800, self._reset_copy_btn, btn)

    def _reset_copy_btn(self, btn):
        btn.get_style_context().remove_class("copied")
        btn.set_label("📋 Copiar")
        return False

    def _build_tray_indicator(self):
        icon_name = self.icon_path if os.path.exists(self.icon_path) else "input-touchpad"
        self.indicator = appindicator.Indicator.new(
            "omniremote-indicator",
            icon_name,
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
        return True

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
