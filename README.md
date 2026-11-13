# 📱 OmniRemote

> **The 100% Local, Zero-Install Web Remote for Linux & Windows.**  
> Control your desktop touchpad, keyboard, terminal shortcuts, and presentation slides directly from your smartphone's web browser over local Wi-Fi.

---

## ⚡ Por qué OmniRemote (Features)

1. **Zero-Install en el móvil:**
   * No necesitas descargar apps de la Play Store o App Store.
   * Funciona directamente desde cualquier navegador móvil (Chrome, Safari, Firefox) escaneando un código QR.
   * Compatible con **PWA** ("Agregar a pantalla de inicio" para pantalla completa nativa sin barras del navegador).

2. **Ventana Flotante & Bandeja del Sistema (System Tray):**
   * Al iniciar, se abre una elegante ventana flotante con el código QR y la IP local.
   * Al escanear o presionar `✕`, la ventana se oculta a la bandeja del sistema (**Waybar**, KDE, GNOME, Windows Tray) sin terminales abiertas de fondo.
   * Menú contextual rápido: Mostrar QR, Abrir en navegador, Copiar enlace y Salir.

3. **Arquitectura Multi-Entorno de Vanguardia:**
   * **Linux (Kernel `/dev/uinput`):** Emulación de hardware a nivel de kernel. Compatible 100% con Wayland nativo y X11 (**Hyprland, Niri, Sway, KDE Plasma, GNOME, XFCE**).
   * **Windows (Win32 `SendInput`):** 0 ms de latencia mediante llamadas nativas de C vía `ctypes`.
   * **Detección inteligente de escritorio:** Reconoce gestos de cambio de escritorio y ventanas activas según el compositor.

4. **Experiencia de Entrada Refinada:**
   * **Trackpad multitáctil:** Aceleración logarítmica suave, scroll con 2 dedos, pellizco para zoom (Pinch-to-Zoom), clic izquierdo con sostener para arrastrar/seleccionar con otro dedo.
   * **Teclado en Vivo con Delta Tracking:** Algoritmo de prefijo común más largo que previene la duplicación de letras de Gboard/IME.
   * **Caja de texto auto-expandible (1 a 8 líneas):** Estilo WhatsApp/Telegram con botón circular de envío `➤`.
   * **Macros y Hardware:** `Esc`, `Tab`, `SIGINT (Ctrl+C)`, flechas de dirección para `nano`/`vim`/`fzf`, y `Ctrl+Shift+C`/`Ctrl+Shift+V` para terminal.
   * **Control de Presentaciones:** Diapositivas anterior/siguiente, cronómetro de exposición integrado y control de volumen PipeWire/PulseAudio.

---

## 🚀 Inicio Rápido

### Requisitos en Linux
* Python 3.10+
* Usuario con acceso a `/dev/uinput` (grupo `input`):
  ```bash
  sudo usermod -aG input $USER
  ```
* Herramientas recomendadas: `qrencode` (para generar QR visual), `playerctl` y `wpctl` (para audio/multimedia).

### Ejecutar

```bash
# Modo GUI (con Ventana Flotante y Bandeja del Sistema / Waybar):
./omniremote.py

# Modo CLI (Terminal pura sin interfaz gráfica):
./omniremote.py --cli

# Cambiar puerto personalizado:
./omniremote.py --port 9000
```

---

## 📁 Estructura del Proyecto

```text
omniremote/
├── omniremote.py              # Punto de entrada principal
├── core/
│   ├── server.py              # Servidor HTTP y WebSocket asíncrono
│   ├── input/
│   │   ├── base.py            # Interfaz abstracta de entrada
│   │   ├── linux_uinput.py    # Driver Linux (/dev/uinput kernel)
│   │   └── windows_sendinput.py # Driver Windows (Win32 SendInput)
│   ├── desktop/
│   │   ├── base.py            # Interfaz de entorno de escritorio
│   │   ├── detector.py        # Detector automático de SO/Compositor
│   │   ├── hyprland.py        # IPC de Hyprland
│   │   ├── niri.py            # IPC de Niri
│   │   ├── sway.py            # IPC de Sway
│   │   └── generic.py         # Fallback universal (KDE, GNOME, Windows)
│   └── ui/
│       └── tray_linux.py      # Bandeja nativa (AyatanaAppIndicator) y ventana QR
└── web/
    ├── index.html             # Interfaz web móvil (PWA)
    └── manifest.json          # Manifiesto PWA para instalación móvil
```

---

## 📄 Licencia
Licencia MIT. Hecho con ❤️ para la comunidad de software libre.
