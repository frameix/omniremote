#!/usr/bin/env bash
# OmniRemote - Universal Linux Uninstaller
# Desinstala OmniRemote limpiamente del sistema

set -e

if [ "$EUID" -ne 0 ]; then
    echo "==> Solicitando permisos de superusuario (sudo)..."
    exec sudo bash "$0" "$@"
fi

PREFIX="${PREFIX:-/usr/local}"

echo "=========================================================="
echo "      🗑️  Desinstalador de OmniRemote"
echo "=========================================================="
echo ""

echo "-> Eliminando archivos del sistema..."

rm -f "$PREFIX/bin/omniremote"
rm -rf "$PREFIX/lib/omniremote"
rm -f "$PREFIX/share/applications/omniremote.desktop"
rm -f /usr/share/applications/omniremote.desktop 2>/dev/null || true
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/omniremote-app.svg"
rm -f "$PREFIX/share/icons/hicolor/512x512/apps/omniremote-app.png"
rm -f /usr/share/icons/hicolor/scalable/apps/omniremote-app.svg 2>/dev/null || true
rm -f /usr/share/icons/hicolor/512x512/apps/omniremote-app.png 2>/dev/null || true
rm -f /etc/udev/rules.d/99-omniremote-uinput.rules
rm -f /usr/lib/udev/rules.d/99-omniremote-uinput.rules 2>/dev/null || true

if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" 2>/dev/null || true
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q "$PREFIX/share/applications" 2>/dev/null || true
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

echo ""
echo "✅ OmniRemote ha sido desinstalado completamente de tu sistema."
echo "=========================================================="
