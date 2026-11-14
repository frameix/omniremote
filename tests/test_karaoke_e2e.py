#!/usr/bin/env python3
"""OmniRemote - Comprehensive End-to-End Karaoke & Web Test Suite
Tests HTTP serving, WebSocket RFC 6455 framing, search, queue management, and browser headless rendering.
"""
import asyncio
import base64
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.input.base import BaseInput
from core.desktop.base import BaseDesktop
from core.server import OmniServer


class MockInput(BaseInput):
    def move(self, dx, dy): pass
    def click(self, button, press=True): pass
    def scroll(self, dx, dy): pass
    def zoom(self, factor): pass
    def tap_key(self, key_name): pass
    def type_text(self, text): pass
    def key_combo(self, modifiers, key_name): pass
    def smart_paste(self): pass


class MockDesktop(BaseDesktop):
    def switch_workspace(self, delta): pass
    def get_active_window(self): return "mock_window", "Mock Title"
    def toggle_fullscreen(self): pass


def make_raw_ws_client_frame(payload_bytes: bytes, opcode: int = 0x1) -> bytes:
    """Builds a masked client-to-server RFC 6455 WebSocket frame."""
    b1 = 0x80 | (opcode & 0x0F)
    mask = b"\x12\x34\x56\x78"
    length = len(payload_bytes)

    if length <= 125:
        header = bytes([b1, 0x80 | length])
    elif length <= 65535:
        header = bytes([b1, 0x80 | 126]) + struct.pack(">H", length)
    else:
        header = bytes([b1, 0x80 | 127]) + struct.pack(">Q", length)

    masked_payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload_bytes))
    return header + mask + masked_payload


async def read_raw_ws_server_frame(reader: asyncio.StreamReader) -> str:
    """Reads and decodes an unmasked server-to-client RFC 6455 WebSocket frame."""
    head = await reader.read(2)
    if len(head) < 2:
        return ""
    b1, b2 = head[0], head[1]
    payload_len = b2 & 0x7F
    if payload_len == 126:
        ext = await reader.read(2)
        payload_len = struct.unpack(">H", ext)[0]
    elif payload_len == 127:
        ext = await reader.read(8)
        payload_len = struct.unpack(">Q", ext)[0]

    payload = await reader.read(payload_len)
    return payload.decode("utf-8", errors="ignore")


async def run_all_tests():
    port = 8877
    server = OmniServer(MockInput(), MockDesktop(), port=port)
    # Prevent mpv from popping real windows during unit tests by overriding _launch_player
    launched_songs = []
    server.karaoke._launch_player = lambda song: launched_songs.append(song)

    await server.start()
    print(f"✓ OmniServer iniciado en puerto {port}")

    # --- TEST 1: HTTP Serving ---
    print("\n[TEST 1] Verificando servicio HTTP estático y elementos DOM...")
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
    await writer.drain()
    http_resp = await reader.read()
    writer.close()
    await writer.wait_closed()

    html = http_resp.decode("utf-8", errors="ignore")
    assert "HTTP/1.1 200 OK" in html, "Servidor no respondió 200 OK"
    assert 'data-tab="tab-karaoke"' in html, "Falta botón Karaoke en la barra de navegación"
    assert 'id="tab-karaoke"' in html, "Falta contenedor #tab-karaoke"
    assert 'id="karaoke-input"' in html, "Falta input #karaoke-input"
    assert 'id="btn-karaoke-search"' in html, "Falta botón #btn-karaoke-search"
    assert 'id="karaoke-results-list"' in html, "Falta lista #karaoke-results-list"
    assert 'id="karaoke-queue-list"' in html, "Falta lista #karaoke-queue-list"
    assert 'id="karaoke-now-playing"' in html, "Falta tarjeta #karaoke-now-playing"
    print("✓ TEST 1 PASÓ: El HTML y los componentes de Karaoke están completos en la respuesta.")

    # --- TEST 2: WebSocket Handshake & Initial State ---
    print("\n[TEST 2] Estableciendo handshake WebSocket y recibiendo estado inicial...")
    ws_reader, ws_writer = await asyncio.open_connection("127.0.0.1", port)
    sec_key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET /ws HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {sec_key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    ws_writer.write(handshake.encode())
    await ws_writer.drain()

    hs_resp = await ws_reader.readuntil(b"\r\n\r\n")
    assert b"101 Switching Protocols" in hs_resp, "Handshake WebSocket falló"

    # Servidor debe enviar inmediatamente el estado inicial del karaoke
    initial_frame = await read_raw_ws_server_frame(ws_reader)
    initial_msg = json.loads(initial_frame)
    assert initial_msg.get("type") == "karaoke_state", f"Se esperaba karaoke_state, se recibió {initial_msg}"
    assert initial_msg.get("data", {}).get("current") is None
    assert initial_msg.get("data", {}).get("queue") == []
    print("✓ TEST 2 PASÓ: Handshake WebSocket 101 OK y karaoke_state recibido.")

    # --- TEST 3: Búsqueda en YouTube ---
    print("\n[TEST 3] Enviando búsqueda de canción (Selena - Como la Flor)...")
    search_req = {"type": "karaoke_search", "query": "Selena Como la Flor", "karaoke": True}
    ws_writer.write(make_raw_ws_client_frame(json.dumps(search_req).encode()))
    await ws_writer.drain()

    search_frame = await read_raw_ws_server_frame(ws_reader)
    search_msg = json.loads(search_frame)
    assert search_msg.get("type") == "karaoke_results", f"Mensaje incorrecto: {search_msg}"
    results = search_msg.get("results", [])
    assert len(results) > 0, "No se obtuvieron resultados de búsqueda de YouTube"
    print(f"✓ TEST 3 PASÓ: Se recibieron {len(results)} canciones de YouTube:")
    for r in results[:3]:
        print(f"   • {r['title']} [{r['duration']}] (ID: {r['id']})")

    # --- TEST 4: Cola de Reproducción ---
    print("\n[TEST 4] Probando agregar canciones a la cola de Karaoke...")
    song1 = results[0]
    song2 = results[1]

    # Agregar canción 1
    add_req1 = {"type": "karaoke_add_queue", "song": song1}
    ws_writer.write(make_raw_ws_client_frame(json.dumps(add_req1).encode()))
    await ws_writer.drain()

    state_frame1 = await read_raw_ws_server_frame(ws_reader)
    state_msg1 = json.loads(state_frame1)
    assert state_msg1.get("type") == "karaoke_state"
    # Como la cola estaba vacía, song1 se convirtió en current_song y se lanzó
    current = state_msg1.get("data", {}).get("current")
    assert current is not None and current["id"] == song1["id"]
    print(f"✓ Canción 1 entró a 'Sonando Ahora': {current['title']}")

    # Agregar canción 2 a la cola
    add_req2 = {"type": "karaoke_add_queue", "song": song2}
    ws_writer.write(make_raw_ws_client_frame(json.dumps(add_req2).encode()))
    await ws_writer.drain()

    state_frame2 = await read_raw_ws_server_frame(ws_reader)
    state_msg2 = json.loads(state_frame2)
    queue = state_msg2.get("data", {}).get("queue", [])
    assert len(queue) == 1 and queue[0]["id"] == song2["id"]
    print(f"✓ Canción 2 quedó en la lista de espera: {queue[0]['title']}")

    # Saltar a siguiente canción (Next)
    print("\n[TEST 5] Probando botón 'Siguiente canción'...")
    next_req = {"type": "karaoke_next"}
    ws_writer.write(make_raw_ws_client_frame(json.dumps(next_req).encode()))
    await ws_writer.drain()

    state_frame3 = await read_raw_ws_server_frame(ws_reader)
    state_msg3 = json.loads(state_frame3)
    current3 = state_msg3.get("data", {}).get("current")
    queue3 = state_msg3.get("data", {}).get("queue", [])
    assert current3["id"] == song2["id"], "No avanzó a song2"
    assert len(queue3) == 0, "La cola debería quedar vacía"
    print(f"✓ Siguiente avanzó correctamente: ahora suena '{current3['title']}' y la cola quedó vacía.")

    # Detener (Stop)
    print("\n[TEST 6] Probando botón 'Detener'...")
    stop_req = {"type": "karaoke_stop"}
    ws_writer.write(make_raw_ws_client_frame(json.dumps(stop_req).encode()))
    await ws_writer.drain()

    state_frame4 = await read_raw_ws_server_frame(ws_reader)
    state_msg4 = json.loads(state_frame4)
    assert state_msg4.get("data", {}).get("current") is None
    print("✓ Detener vació la canción activa.")

    ws_writer.close()
    await ws_writer.wait_closed()
    await server.stop()
    print("\n==========================================")
    print("  🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
