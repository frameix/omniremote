"""OmniRemote - Asyncio Core Server
Pure Python asynchronous HTTP and WebSocket server for local network remote control.
"""
import asyncio
import base64
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import time

MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class OmniServer:
    def __init__(self, input_driver, desktop_backend, port=8765, web_dir=None, status_callback=None, show_callback=None):
        self.input_driver = input_driver
        self.desktop_backend = desktop_backend
        self.port = port
        self.web_dir = web_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "web")
        self.status_callback = status_callback
        self.show_callback = show_callback

        self.action_queue = asyncio.Queue()
        self.clients = set()
        self.is_running = False
        self._server = None

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._action_worker())
        self._server = await asyncio.start_server(self._handle_client, "0.0.0.0", self.port)
        local_ip = get_local_ip()
        print(f"\n==========================================")
        print(f"  🚀 OmniRemote Activo")
        print(f"  URL Local: http://{local_ip}:{self.port}")
        print(f"==========================================\n")
        return local_ip

    async def stop(self):
        self.is_running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        if hasattr(self.input_driver, 'close'):
            self.input_driver.close()

    async def _action_worker(self):
        while self.is_running:
            action_type, args = await self.action_queue.get()
            try:
                await asyncio.to_thread(self._execute_action, action_type, args)
            except Exception as e:
                print(f"[OmniServer Worker] Error ejecutando {action_type}: {e}")
            finally:
                self.action_queue.task_done()

    def _execute_action(self, action_type, args):
        if action_type == "move":
            dx, dy = args
            self.input_driver.move(dx, dy)
        elif action_type == "click":
            btn = args[0]
            self.input_driver.click(btn, press=True)
        elif action_type == "down":
            btn = args[0]
            if hasattr(self.input_driver, 'button_down'):
                self.input_driver.button_down(btn)
        elif action_type == "up":
            btn = args[0]
            if hasattr(self.input_driver, 'button_up'):
                self.input_driver.button_up(btn)
        elif action_type == "scroll":
            dx, dy = args
            self.input_driver.scroll(dx, dy)
        elif action_type == "zoom":
            direction = args[0]
            self.input_driver.zoom(1.0 if direction == "in" else -1.0)
        elif action_type == "key":
            key_name = args[0]
            self.input_driver.tap_key(key_name)
        elif action_type == "type":
            text = args[0]
            self.input_driver.type_text(text)
        elif action_type == "combo":
            modifiers, key_name = args
            self.input_driver.key_combo(modifiers, key_name)
        elif action_type == "smart_paste":
            self.desktop_backend.smart_paste(self.input_driver)
        elif action_type == "smart_copy":
            self.desktop_backend.smart_copy(self.input_driver)
        elif action_type == "smart_present":
            self.desktop_backend.start_presentation(self.input_driver)
        elif action_type == "workspace_next":
            self.desktop_backend.switch_workspace(1)
        elif action_type == "workspace_prev":
            self.desktop_backend.switch_workspace(-1)
        elif action_type == "fullscreen":
            self.desktop_backend.toggle_fullscreen()
        elif action_type == "media":
            cmd = args[0]
            self.desktop_backend.handle_media(cmd, self.input_driver)

    async def _handle_client(self, reader, writer):
        try:
            request = await reader.read(4096)
            if not request:
                writer.close()
                return

            req_str = request.decode("utf-8", errors="ignore")
            headers = {}
            for line in req_str.split("\r\n")[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v

            first_line = req_str.split("\r\n")[0] if req_str else ""
            parts = first_line.split()
            path = parts[1] if len(parts) > 1 else "/"

            if headers.get("upgrade", "").lower() == "websocket":
                await self._handle_websocket(reader, writer, headers)
            elif path == "/api/show":
                if self.show_callback:
                    try:
                        self.show_callback()
                    except Exception:
                        pass
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nOK")
                await writer.drain()
                writer.close()
            else:
                await self._serve_static(writer, path)
        except Exception:
            try:
                writer.close()
            except Exception:
                pass

    async def _serve_static(self, writer, path):
        if path == "/" or path == "":
            path = "/index.html"

        safe_path = os.path.normpath(path.lstrip("/"))
        file_path = os.path.join(self.web_dir, safe_path)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            file_path = os.path.join(self.web_dir, "index.html")

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".json": "application/json",
            ".js": "application/javascript",
            ".css": "text/css",
            ".png": "image/png",
            ".svg": "image/svg+xml"
        }
        ext = os.path.splitext(file_path)[1].lower()
        content_type = content_types.get(ext, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + content
            writer.write(response)
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    async def _handle_websocket(self, reader, writer, headers):
        sec_key = headers.get("sec-websocket-key", "")
        accept_val = base64.b64encode(hashlib.sha1((sec_key + MAGIC.decode()).encode()).digest()).decode()

        handshake = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_val}\r\n\r\n"
        )
        writer.write(handshake.encode())
        await writer.drain()

        self.clients.add(writer)
        if self.status_callback:
            self.status_callback(len(self.clients))

        try:
            while self.is_running:
                data = await self._read_ws_frame(reader)
                if data is None:
                    break

                try:
                    msg = json.loads(data)
                    self._dispatch_ws_message(msg)
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            self.clients.discard(writer)
            if self.status_callback:
                self.status_callback(len(self.clients))
            try:
                writer.close()
            except Exception:
                pass

    def _dispatch_ws_message(self, msg):
        mtype = msg.get("type")
        if mtype == "move":
            dx = msg.get("dx", 0)
            dy = msg.get("dy", 0)
            self.action_queue.put_nowait(("move", (dx, dy)))
        elif mtype == "click":
            btn = msg.get("button", "left")
            self.action_queue.put_nowait(("click", (btn,)))
        elif mtype == "down":
            btn = msg.get("button", "left")
            self.action_queue.put_nowait(("down", (btn,)))
        elif mtype == "up":
            btn = msg.get("button", "left")
            self.action_queue.put_nowait(("up", (btn,)))
        elif mtype == "scroll":
            dx = msg.get("dx", 0)
            dy = msg.get("dy", 0)
            self.action_queue.put_nowait(("scroll", (dx, dy)))
        elif mtype == "zoom":
            direction = msg.get("direction", "in")
            self.action_queue.put_nowait(("zoom", (direction,)))
        elif mtype == "key":
            key_name = msg.get("key", "")
            if key_name == "F5":
                self.action_queue.put_nowait(("smart_present", ()))
            else:
                self.action_queue.put_nowait(("key", (key_name,)))
        elif mtype == "type":
            text = msg.get("text", "")
            self.action_queue.put_nowait(("type", (text,)))
        elif mtype == "combo":
            modifiers = msg.get("modifiers", [])
            key_name = msg.get("key", "")
            self.action_queue.put_nowait(("combo", (modifiers, key_name)))
        elif mtype == "smart_paste":
            self.action_queue.put_nowait(("smart_paste", ()))
        elif mtype == "smart_copy":
            self.action_queue.put_nowait(("smart_copy", ()))
        elif mtype == "smart_present":
            self.action_queue.put_nowait(("smart_present", ()))
        elif mtype == "gesture":
            action = msg.get("action")
            if action in ("workspace_next", "workspace_prev", "fullscreen"):
                self.action_queue.put_nowait((action, ()))
        elif mtype == "media":
            action = msg.get("action")
            self.action_queue.put_nowait(("media", (action,)))

    async def _read_ws_frame(self, reader):
        head = await reader.read(2)
        if len(head) < 2:
            return None

        byte1, byte2 = head[0], head[1]
        opcode = byte1 & 0x0F
        if opcode == 0x8:  # Close frame
            return None

        masked = bool(byte2 & 0x80)
        payload_len = byte2 & 0x7F

        if payload_len == 126:
            ext = await reader.read(2)
            payload_len = struct.unpack(">H", ext)[0]
        elif payload_len == 127:
            ext = await reader.read(8)
            payload_len = struct.unpack(">Q", ext)[0]

        mask = await reader.read(4) if masked else None
        payload = await reader.read(payload_len)

        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))

        return payload.decode("utf-8", errors="ignore")
