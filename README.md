# 📱 OmniRemote

<p align="center">
  <img src="core/ui/assets/omniremote-app.png" alt="OmniRemote Logo" width="128" height="128" style="border-radius: 24px;" />
</p>

<p align="center">
  <b>El control remoto web 100% local, sin instalación en el móvil, para Linux y Windows.</b><br>
  <i>Controla tu trackpad, teclado, atajos de terminal y diapositivas directamente desde el navegador de tu smartphone a través de tu red Wi-Fi local.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Arch_Linux-Compatible-1793D1?logo=arch-linux&logoColor=white" alt="Arch Linux" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3" />
  <img src="https://img.shields.io/badge/Wayland-Native-4E9A06" alt="Wayland Native" />
  <img src="https://img.shields.io/badge/Windows-10%20%2F%2011-0078D6?logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT" />
</p>

---

## ⚡ Características Principales

1. **Zero-Install en el móvil:**
   - No requiere descargar aplicaciones de Google Play o App Store.
   - Solo escanea el código QR desde cualquier móvil (Chrome, Safari, Firefox) conectado a la misma red Wi-Fi.
   - Compatible con **PWA**: pulsa *"Agregar a la pantalla de inicio"* para usarlo a pantalla completa como una app nativa sin barras de navegación.

2. **Ventana Flotante y Bandeja del Sistema (Tray):**
   - Al abrirse, muestra una ventana oscura con el código QR, la dirección IP y un botón para copiar la URL al portapapeles.
   - Botón `✕` superior para apagar el servidor completamente.
   - Botón `Ocultar a la Barra (Tray)` para minimizarlo a la bandeja del sistema (compatible con **Waybar**, Caelestia, KDE Plasma, GNOME, etc.).

3. **Arquitectura Multi-Entorno de Baja Latencia:**
   - **Linux (Kernel `/dev/uinput`):** Emulación de hardware a nivel de kernel. 0 ms de latencia perceptiva. Compatible con Wayland puro y X11 (**Hyprland, Niri, Sway, KDE Plasma, GNOME, XFCE**).
   - **Windows (Win32 `SendInput`):** Sin librerías pesadas externas; llamadas directas a la API de Windows mediante `ctypes`.
   - **Detección inteligente de compositor:** Adaptación automática a las APIs de Hyprland, Niri, Sway y entornos universales.

4. **Experiencia Táctil y Teclado:**
   - **Trackpad de precisión:** Aceleración logarítmica fluida, scroll con 2 dedos, pellizco para zoom (Pinch-to-zoom) y toque sostenido para arrastre.
   - **Live Typing con Delta Tracking:** Algoritmo de sincronización diferencial que evita la duplicación de texto en teclados móviles inteligentes (Gboard, Samsung Keyboard, iOS).
   - **Caja de texto auto-expandible:** Diseño estilo mensajería (1 a 8 líneas) con botón de envío rápido.
   - **Macros y atajos de terminal:** Teclas dedicadas para `Esc`, `Tab`, `Ctrl+C` (interrupción), flechas direccionales, `Ctrl+Shift+C` y `Ctrl+Shift+V`.
   - **Modo Presentador:** Botones para diapositiva anterior/siguiente, cronómetro integrado para conferencias y control de volumen.

---

## 📦 Instalación

### Método 1: Arch Linux / CachyOS / Manjaro (Recomendado)

OmniRemote incluye configuración nativa para integrarse como paquete oficial de Arch Linux (`pacman`), con su lanzador de escritorio, iconos en el sistema y reglas de permisos de hardware sin necesidad de usar `sudo` para el teclado/ratón.

#### Opción A: Compilar e instalar con `makepkg`
```bash
git clone https://github.com/marc77mz/omniremote.git
cd omniremote

# Compilar e instalar dependencias automáticamente:
makepkg -si
```

#### Opción B: Instalar el paquete precompilado
```bash
sudo pacman -U omniremote-1.0.0-1-any.pkg.tar.zst
```

*Para desinstalarlo en cualquier momento:*
```bash
sudo pacman -R omniremote
```

---

### Método 2: Instalador Universal Linux (Ubuntu, Debian, Fedora, Mint, openSUSE)

Si utilizas otra distribución Linux, puedes usar el script de instalación universal:

```bash
git clone https://github.com/marc77mz/omniremote.git
cd omniremote

# Ejecutar el instalador con permisos de administrador:
sudo ./install.sh
```

El instalador:
1. Configura el binario en `/usr/local/bin/omniremote`.
2. Instala la regla de udev `/etc/udev/rules.d/99-omniremote-uinput.rules` para dar acceso seguro a `/dev/uinput` al usuario de escritorio activo.
3. Instala el lanzador de escritorio y los iconos del sistema.

*Para desinstalarlo limpiamente:*
```bash
sudo ./uninstall.sh
```

---

### Método 3: Ejecución Portable (Sin Instalar)

Puedes ejecutar OmniRemote directamente desde el repositorio sin necesidad de instalarlo en el sistema:

#### En Linux:
```bash
# Dependencias recomendadas:
# Arch:   sudo pacman -S python python-gobject gtk3 libayatana-appindicator qrencode
# Ubuntu: sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 qrencode

python3 omniremote.py
```

#### En Windows:
```cmd
python omniremote.py
```

---

## 📱 Cómo Conectarse desde el Celular

1. Asegúrate de que tu smartphone y tu computadora estén conectados a la **misma red Wi-Fi** o punto de acceso.
2. Abre **OmniRemote** desde tu menú de aplicaciones o escribiendo `omniremote` en la terminal.
3. Se abrirá la ventana flotante con el **código QR**:
   - Escanéalo con la cámara de tu móvil o la app de escaneo de QR.
   - O bien, escribe la dirección IP mostrada (por ejemplo: `http://192.168.100.52:8765`) en tu navegador móvil.
4. **(Opcional pero recomendado):** En el navegador de tu móvil, abre el menú de opciones (los tres puntos en Chrome o el botón de compartir en Safari) y selecciona **"Agregar a la pantalla de inicio"**. Esto habilitará el modo pantalla completa PWA sin barras de direcciones.

---

## ⚙️ Opciones de Línea de Comandos

```bash
# Modo normal (Ventana flotante + Bandeja del sistema):
omniremote

# Modo Terminal Puro (Headless / sin GUI ni bandeja, ideal para servidores o SSH):
omniremote --cli

# Usar un puerto personalizado:
omniremote --port 9090
```

---

## 🔒 Permisos de Hardware en Linux (`/dev/uinput`)

OmniRemote utiliza la interfaz del kernel `/dev/uinput` para simular hardware real (ratón y teclado) a nivel del sistema operativo. Esto garantiza cero latencia y compatibilidad total con Wayland.

Tanto el paquete de Arch Linux como el instalador universal configuran automáticamente la regla udev:
```udev
KERNEL=="uinput", SUBSYSTEM=="misc", MODE="0660", GROUP="input", TAG+="uaccess", OPTIONS+="static_node=uinput"
```
La etiqueta `TAG+="uaccess"` permite a systemd otorgar permisos de lectura y escritura al usuario que tiene la sesión gráfica activa (`logind`), **sin necesidad de ejecutar la aplicación como root ni pertenecer forzosamente a grupos adicionales**.

---

## 📂 Estructura del Proyecto

```text
omniremote/
├── PKGBUILD                     # Definición de empaquetado para Arch Linux / pacman
├── .SRCINFO                     # Metadatos del paquete para Arch / AUR
├── omniremote.install           # Scriptlet post-instalación de pacman
├── install.sh                   # Instalador universal para cualquier Linux
├── uninstall.sh                 # Desinstalador universal limpio
├── omniremote.desktop           # Lanzador XDG Desktop estándar
├── omniremote.py                # Punto de entrada ejecutable
├── udev/
│   └── 99-omniremote-uinput.rules # Regla udev con TAG+="uaccess"
├── core/
│   ├── server.py                # Servidor asíncrono HTTP y WebSocket
│   ├── input/
│   │   ├── base.py              # Interfaz abstracta de controladores
│   │   ├── linux_uinput.py      # Driver de hardware para Linux (/dev/uinput)
│   │   └── windows_sendinput.py # Driver nativo de Windows (Win32 SendInput)
│   ├── desktop/
│   │   ├── base.py              # Contrato de escritorio
│   │   ├── detector.py          # Auto-detección de entorno (Hyprland, Niri, Sway, etc.)
│   │   ├── hyprland.py          # Backend IPC de Hyprland
│   │   ├── niri.py              # Backend IPC de Niri
│   │   ├── sway.py              # Backend IPC de Sway
│   │   └── generic.py           # Backend genérico (KDE, GNOME, Windows)
│   └── ui/
│       ├── tray_linux.py        # Bandeja del sistema (Ayatana) y ventana flotante GTK3
│       └── assets/
│           ├── omniremote-app.svg # Icono vectorial oficial
│           └── omniremote-app.png # Icono rasterizado 512px
└── web/
    ├── index.html               # Interfaz táctil web del móvil
    ├── manifest.json            # Manifiesto PWA para instalación móvil
    └── icon.png                 # Icono de la web app
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](file:///home/frame/Proyectos/omniremote/LICENSE) para más detalles.
