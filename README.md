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

## 📦 Instalación Sencilla (Para cualquier usuario)

Tienes varias formas de instalar OmniRemote, desde un comando de una sola línea hasta paquetes nativos de Arch Linux.

### ⚡ Opción 1: Instalación en 1 Línea (Cualquier Linux)

No necesitas clonar el repositorio manualmente ni lidiar con carpetas. Simplemente copia y pega este comando en tu terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/frameix/omniremote/main/install.sh | sudo bash
```

> **¿Qué hace este comando automáticamente?**
> 1. Descarga e instala los archivos en `/usr/local/lib/omniremote`.
> 2. Crea el comando `omniremote` en tu sistema (`/usr/local/bin`).
> 3. Configura los permisos de hardware `/dev/uinput` vía udev (sin necesidad de reiniciar).
> 4. Instala el icono oficial y el acceso directo para que aparezca en tu menú de aplicaciones.

*Para desinstalarlo en cualquier momento:*
```bash
curl -fsSL https://raw.githubusercontent.com/frameix/omniremote/main/uninstall.sh | sudo bash
```

---

### 🏹 Opción 2: Arch Linux / CachyOS / Manjaro (Nativo con `pacman`)

Si utilizas Arch Linux o derivados, puedes instalarlo como cualquier programa oficial (como VS Code o Brave):

#### A. Con tu AUR helper favorito (`paru` / `yay`):
```bash
paru -S omniremote-git
# o
yay -S omniremote-git
```

#### B. Directo con `pacman` (Precompilado desde GitHub Releases):
`pacman` puede instalar paquetes directamente desde una URL sin tener que compilar nada:
```bash
sudo pacman -U https://github.com/frameix/omniremote/releases/latest/download/omniremote-1.0.0-1-any.pkg.tar.zst
```

#### C. Desde el repositorio clonado con `makepkg`:
```bash
git clone https://github.com/frameix/omniremote.git
cd omniremote
makepkg -si
```

*Para desinstalarlo vía pacman:*
```bash
sudo pacman -R omniremote
```

---

### 🪟 Opción 3: Windows (10 / 11)

Para los usuarios de Windows no es necesario instalar Python ni usar la consola:

1. Ve a la sección de **[Releases de GitHub](https://github.com/frameix/omniremote/releases/latest)** y descarga **`OmniRemote-Windows-x64.zip`**.
2. Descomprime la carpeta (Clic derecho -> *Extraer todo*).
3. Haz doble clic en **`OmniRemote.exe`**. Se abrirá automáticamente tu navegador web con el código QR listo para escanear con tu móvil.

---

### 💻 Opción 4: Ejecución desde el Código Fuente (Desarrolladores)

Si prefieres ejecutarlo manualmente con Python:

#### En Linux:
```bash
git clone https://github.com/frameix/omniremote.git
cd omniremote
python3 omniremote.py
```

#### En Windows (con Python instalado):
```cmd
git clone https://github.com/frameix/omniremote.git
cd omniremote
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
