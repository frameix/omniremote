#!/usr/bin/env python3
"""
OmniRemote
The 100% Local, Zero-Install Web Remote for Linux & Windows.
https://github.com/marc77mz/omniremote
"""
import argparse
import asyncio
import os
import signal
import sys
import threading

# Add root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.desktop.detector import get_desktop_backend
from core.server import OmniServer, get_local_ip


def get_input_driver():
    if sys.platform == "win32":
        from core.input.windows_sendinput import WindowsSendInput
        return WindowsSendInput()
    else:
        from core.input.linux_uinput import LinuxUInput
        return LinuxUInput()


def main():
    parser = argparse.ArgumentParser(description="OmniRemote - Zero-Install Web Remote")
    parser.add_argument("--port", type=int, default=8765, help="Puerto del servidor (default: 8765)")
    parser.add_argument("--cli", action="store_true", help="Modo terminal puro (sin ventana flotante ni tray)")
    args = parser.parse_args()

    input_driver = get_input_driver()
    desktop_backend = get_desktop_backend(input_driver)

    tray_app = None

    def on_status_change(count):
        if tray_app:
            tray_app.update_clients_count(count)

    server = OmniServer(
        input_driver=input_driver,
        desktop_backend=desktop_backend,
        port=args.port,
        status_callback=on_status_change
    )

    loop = asyncio.new_event_loop()

    def run_server_thread():
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(server.start())
            loop.run_forever()
        except Exception as e:
            print(f"[OmniRemote Server] Error: {e}")

    server_thread = threading.Thread(target=run_server_thread, daemon=True)
    server_thread.start()

    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{args.port}"

    def shutdown():
        print("\n[OmniRemote] Cerrando servidor y liberando recursos...")
        asyncio.run_coroutine_threadsafe(server.stop(), loop)
        loop.call_soon_threadsafe(loop.stop())

    if args.cli or sys.platform == "win32":
        # Modo terminal o Windows fallback
        print(f"✓ OmniRemote ejecutándose en modo CLI: {local_url}")
        print("Presiona Ctrl+C para detener.")
        try:
            while server_thread.is_alive():
                server_thread.join(timeout=1.0)
        except KeyboardInterrupt:
            shutdown()
    else:
        # Modo GUI nativo con System Tray y Ventana Flotante QR
        try:
            from core.ui.tray_linux import LinuxTrayApp
            tray_app = LinuxTrayApp(local_url=local_url, on_quit_callback=shutdown)
            tray_app.run()
        except Exception as e:
            print(f"⚠ [OmniRemote] Fallback a modo CLI (No se pudo iniciar bandeja/GUI): {e}")
            try:
                while server_thread.is_alive():
                    server_thread.join(timeout=1.0)
            except KeyboardInterrupt:
                shutdown()


if __name__ == "__main__":
    main()
