#!/usr/bin/env bash
# OmniRemote - Universal Linux Installer
# Instala OmniRemote en cualquier distribución Linux

set -e

# Asegurar permisos de superusuario
if [ "$EUID" -ne 0 ]; then
    echo "==> OmniRemote requiere permisos de administrador para instalar archivos y reglas udev."
    echo "==> Solicitando permisos con sudo..."
    if [ -f "$0" ]; then
        exec sudo bash "$0" "$@"
    else
        # Si se ejecutó por pipe: curl ... | bash
        exec sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/frameix/omniremote/main/install.sh)" "$@"
    fi
fi

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo ".")")" 2>/dev/null && pwd || echo ".")"
PREFIX="${PREFIX:-/usr/local}"
REPO_URL="https://github.com/frameix/omniremote"
CLEANUP_TEMP=0

# Si no estamos en la carpeta del repositorio clonado (e.g. ejecución vía curl | bash)
if [ ! -f "$SCRIPT_DIR/omniremote.py" ] || [ ! -d "$SCRIPT_DIR/core" ]; then
    echo "-> Descargando la versión más reciente de OmniRemote desde GitHub..."
    TMP_DIR=$(mktemp -d /tmp/omniremote-setup.XXXXXX)
    CLEANUP_TEMP=1
    if command -v git >/dev/null 2>&1; then
        git clone --depth 1 "$REPO_URL.git" "$TMP_DIR" >/dev/null 2>&1
    else
        curl -fsSL "$REPO_URL/archive/refs/heads/main.tar.gz" | tar -xz -C "$TMP_DIR" --strip-components=1
    fi
    SCRIPT_DIR="$TMP_DIR"
fi

echo "=========================================================="
echo "      🚀 Instalador de OmniRemote para Linux"
echo "=========================================================="
echo ""
echo "-> Directorio de instalación: $PREFIX"

# 1. Comprobar dependencias del sistema
echo "-> Verificando dependencias..."
MISSING_DEPS=()

for cmd in python3 qrencode; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING_DEPS+=("$cmd")
    fi
done

if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AyatanaAppIndicator3', '0.1')" >/dev/null 2>&1; then
    MISSING_DEPS+=("python-gobject / gtk3 / libayatana-appindicator")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Aviso: Faltan dependencias recomendadas para la interfaz gráfica:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo "Puedes instalarlas según tu distribución:"
    echo "  • Arch/CachyOS: sudo pacman -S python python-gobject gtk3 libayatana-appindicator qrencode"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 qrencode"
    echo "  • Fedora:        sudo dnf install python3 python3-gobject gtk3 libayatana-appindicator-gtk3 qrencode"
    echo ""
    echo "(La instalación continuará; siempre podrás ejecutarlo con --cli o instalar los paquetes luego)"
    echo ""
fi

# 2. Copiar archivos de la aplicación a $PREFIX/lib/omniremote
echo "-> Instalando componentes en $PREFIX/lib/omniremote..."
mkdir -p "$PREFIX/lib/omniremote"
cp -r "$SCRIPT_DIR/core" "$SCRIPT_DIR/web" "$SCRIPT_DIR/omniremote.py" "$PREFIX/lib/omniremote/"
chmod 755 "$PREFIX/lib/omniremote/omniremote.py"
find "$PREFIX/lib/omniremote" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 3. Crear enlace en $PREFIX/bin
echo "-> Creando binario ejecutable en $PREFIX/bin/omniremote..."
mkdir -p "$PREFIX/bin"
ln -sf "$PREFIX/lib/omniremote/omniremote.py" "$PREFIX/bin/omniremote"

# 4. Instalar regla udev para /dev/uinput sin sudo
echo "-> Configurando permisos de /dev/uinput (udev)..."
mkdir -p /etc/udev/rules.d
cp "$SCRIPT_DIR/udev/99-omniremote-uinput.rules" /etc/udev/rules.d/99-omniremote-uinput.rules
chmod 644 /etc/udev/rules.d/99-omniremote-uinput.rules

if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger --subsystem-match=misc 2>/dev/null || true
fi

# 5. Instalar iconos de aplicación
echo "-> Instalando iconos del sistema..."
mkdir -p "$PREFIX/share/icons/hicolor/scalable/apps"
mkdir -p "$PREFIX/share/icons/hicolor/512x512/apps"
cp "$SCRIPT_DIR/core/ui/assets/omniremote-app.svg" "$PREFIX/share/icons/hicolor/scalable/apps/omniremote-app.svg"
cp "$SCRIPT_DIR/core/ui/assets/omniremote-app.png" "$PREFIX/share/icons/hicolor/512x512/apps/omniremote-app.png"

# También copiar a /usr/share/icons si PREFIX es diferente para compatibilidad universal con launchers
if [ "$PREFIX" != "/usr" ] && [ -d /usr/share/icons/hicolor ]; then
    mkdir -p /usr/share/icons/hicolor/scalable/apps /usr/share/icons/hicolor/512x512/apps
    cp "$SCRIPT_DIR/core/ui/assets/omniremote-app.svg" /usr/share/icons/hicolor/scalable/apps/omniremote-app.svg
    cp "$SCRIPT_DIR/core/ui/assets/omniremote-app.png" /usr/share/icons/hicolor/512x512/apps/omniremote-app.png
fi

# 6. Instalar lanzador .desktop
echo "-> Instalando lanzador de aplicaciones (.desktop)..."
mkdir -p "$PREFIX/share/applications"
cp "$SCRIPT_DIR/omniremote.desktop" "$PREFIX/share/applications/omniremote.desktop"

if [ "$PREFIX" != "/usr" ] && [ -d /usr/share/applications ]; then
    cp "$SCRIPT_DIR/omniremote.desktop" /usr/share/applications/omniremote.desktop
fi

# 7. Actualizar cachés del sistema
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" 2>/dev/null || true
    [ "$PREFIX" != "/usr" ] && gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q "$PREFIX/share/applications" 2>/dev/null || true
    [ "$PREFIX" != "/usr" ] && update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

# Limpiar directorio temporal si se descargó vía pipe
if [ "$CLEANUP_TEMP" -eq 1 ] && [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
fi

echo ""
echo "=========================================================="
echo "  ✅ OmniRemote se instaló con éxito."
echo ""
echo "  • Para abrirlo: escribe 'omniremote' o búscalo en tu menú."
echo "  • Modo terminal puro: 'omniremote --cli'"
echo "  • Para desinstalar: 'sudo ./uninstall.sh'"
echo "=========================================================="
