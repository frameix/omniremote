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
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "omniremote-app.png")

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

        # Intercept close event: Super+Q or window manager kill exits cleanly
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
            font-size: 19px;
            font-weight: 800;
            color: #00f2fe;
        }
        .btn-close-window {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #8b949e;
            border-radius: 50%;
            min-width: 28px;
            min-height: 28px;
            font-size: 13px;
            font-weight: 700;
            padding: 0;
            transition: all 0.2s ease;
        }
        .btn-close-window:hover {
            background: rgba(248, 81, 73, 0.3);
            border-color: #f85149;
            color: #ff7b72;
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
            padding: 6px 8px 6px 14px;
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
            margin-top: 4px;
        }
        .btn-hide {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            color: #000;
            font-weight: 700;
            border-radius: 8px;
            border: none;
            padding: 9px 18px;
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
        main_box.set_margin_bottom(10)

        # Top Bar: Logo + Title + Close Button [✕]
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top_bar.set_margin_top(8)

        # Left / Center brand box
        brand_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        brand_box.set_halign(Gtk.Align.CENTER)
        if os.path.exists(self.icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.icon_path, 28, 28, True)
                img_logo = Gtk.Image.new_from_pixbuf(pixbuf)
                brand_box.pack_start(img_logo, False, False, 0)
            except Exception:
                pass

        lbl_title = Gtk.Label(label="OmniRemote")
        lbl_title.get_style_context().add_class("header-title")
        brand_box.pack_start(lbl_title, False, False, 0)

        top_bar.pack_start(brand_box, True, True, 0)

        # Top-Right definitive close [✕] button
        btn_close_app = Gtk.Button(label="✕")
        btn_close_app.get_style_context().add_class("btn-close-window")
        btn_close_app.set_tooltip_text("Cerrar y apagar OmniRemote definitivamente")
        btn_close_app.connect("clicked", lambda _: self._quit(None))
        top_bar.pack_end(btn_close_app, False, False, 0)

        main_box.pack_start(top_bar, False, False, 0)

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

        # Primary Action: Hide to tray
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
        # Si se cierra la ventana con Super+Q o kill del compositor, apagar definitivamente
        self._quit(None)
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
