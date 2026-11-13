# Maintainer: Marco <https://github.com/marc77mz>
pkgname=omniremote
pkgver=1.0.0
pkgrel=1
pkgdesc="Zero-install local Wi-Fi web remote control for Linux (Trackpad, Keyboard, Presenter)"
arch=('any')
url="https://github.com/marc77mz/omniremote"
license=('MIT')
depends=(
    'python'
    'python-gobject'
    'gtk3'
    'libayatana-appindicator'
    'qrencode'
)
optdepends=(
    'playerctl: Control de reproducción multimedia (Spotify, VLC, navegadores)'
    'wireplumber: Control de volumen del sistema en PipeWire'
    'wl-clipboard: Pegado desde el portapapeles en sesiones Wayland'
    'xclip: Pegado desde el portapapeles en sesiones X11'
)
install=omniremote.install

package() {
    local src_root="$srcdir"
    if [ ! -f "$src_root/omniremote.py" ]; then
        src_root="$startdir"
    fi

    # 1. Código y componentes del servidor
    install -dm755 "$pkgdir/usr/lib/$pkgname"
    cp -r "$src_root/core" "$src_root/web" "$src_root/omniremote.py" "$pkgdir/usr/lib/$pkgname/"
    chmod 755 "$pkgdir/usr/lib/$pkgname/omniremote.py"

    # Limpiar __pycache__ residual del empaquetado
    find "$pkgdir/usr/lib/$pkgname" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

    # 2. Enlace simbólico en /usr/bin
    install -dm755 "$pkgdir/usr/bin"
    ln -sf "/usr/lib/$pkgname/omniremote.py" "$pkgdir/usr/bin/$pkgname"

    # 3. Reglas udev para /dev/uinput sin sudo
    install -Dm644 "$src_root/udev/99-omniremote-uinput.rules" "$pkgdir/usr/lib/udev/rules.d/99-omniremote-uinput.rules"

    # 4. Lanzador de escritorio .desktop
    install -Dm644 "$src_root/omniremote.desktop" "$pkgdir/usr/share/applications/omniremote.desktop"

    # 5. Iconos de aplicación (SVG escalable y PNG 512px)
    install -Dm644 "$src_root/core/ui/assets/omniremote-app.svg" "$pkgdir/usr/share/icons/hicolor/scalable/apps/omniremote-app.svg"
    install -Dm644 "$src_root/core/ui/assets/omniremote-app.png" "$pkgdir/usr/share/icons/hicolor/512x512/apps/omniremote-app.png"

    # 6. Licencia
    if [ -f "$src_root/LICENSE" ]; then
        install -Dm644 "$src_root/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    fi
}
