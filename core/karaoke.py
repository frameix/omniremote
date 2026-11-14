"""OmniRemote - Karaoke & Jukebox Service
Searches YouTube without API keys and manages party playback queue.
Uses mpv for ad-free fullscreen playback on Linux, with fallback to default browser.
"""
import json
import re
import shutil
import subprocess
import threading
import urllib.parse
import urllib.request
import webbrowser


class KaraokeManager:
    def __init__(self, on_update=None):
        self.on_update = on_update
        self.queue: list[dict] = []
        self.current_song: dict | None = None
        self.process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def search(self, query: str, karaoke_mode: bool = True) -> list[dict]:
        """Search YouTube for songs or karaoke versions without API keys."""
        query_str = query.strip()
        if not query_str:
            return []

        if karaoke_mode and "karaoke" not in query_str.lower():
            search_query = f"{query_str} karaoke"
        else:
            search_query = query_str

        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[Karaoke] Error al buscar en YouTube: {e}")
            return []

        match = re.search(r"var ytInitialData = ({.*?});</script>", html)
        if not match:
            match = re.search(r"ytInitialData\s*=\s*({.*?});", html)

        results = []
        if match:
            try:
                data = json.loads(match.group(1))
                contents = (
                    data.get("contents", {})
                    .get("twoColumnSearchResultsRenderer", {})
                    .get("primaryContents", {})
                    .get("sectionListRenderer", {})
                    .get("contents", [])
                )
                for section in contents:
                    items = section.get("itemSectionRenderer", {}).get("contents", [])
                    for item in items:
                        v = item.get("videoRenderer")
                        if v:
                            vid = v.get("videoId")
                            title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
                            dur = v.get("lengthText", {}).get("simpleText", "")
                            thumbs = v.get("thumbnail", {}).get("thumbnails", [])
                            thumb = thumbs[-1].get("url", "") if thumbs else ""
                            if vid and title:
                                results.append({
                                    "id": vid,
                                    "title": title,
                                    "duration": dur or "--:--",
                                    "thumb": thumb,
                                })
                                if len(results) >= 6:
                                    break
                    if len(results) >= 6:
                        break
            except Exception as e:
                print(f"[Karaoke] Error al parsear resultados de YouTube: {e}")

        return results

    def add_to_queue(self, song: dict) -> None:
        with self._lock:
            should_start = self.current_song is None
            if not should_start:
                self.queue.append(song)

        if should_start:
            self.play_now(song)
        else:
            self._notify()

    def play_now(self, song: dict) -> None:
        self._stop_current_process()
        with self._lock:
            self.current_song = song
        self._launch_player(song)
        self._notify()

    def play_next(self) -> None:
        self._stop_current_process()
        next_song = None
        with self._lock:
            if self.queue:
                next_song = self.queue.pop(0)
                self.current_song = next_song
            else:
                self.current_song = None

        if next_song:
            self._launch_player(next_song)
        self._notify()

    def remove_from_queue(self, index: int) -> None:
        with self._lock:
            if 0 <= index < len(self.queue):
                self.queue.pop(index)
        self._notify()

    def stop(self) -> None:
        self._stop_current_process()
        with self._lock:
            self.current_song = None
        self._notify()

    def get_state(self) -> dict:
        with self._lock:
            return {
                "current": self.current_song,
                "queue": list(self.queue),
                "has_player": self.process is not None and self.process.poll() is None,
            }

    def _stop_current_process(self) -> None:
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

    def _launch_player(self, song: dict) -> None:
        vid = song.get("id")
        if not vid:
            return

        yt_url = f"https://www.youtube.com/watch?v={vid}"

        if shutil.which("mpv"):
            try:
                cmd = [
                    "mpv",
                    "--fs",
                    "--force-window=immediate",
                    f"--title=OmniRemote Karaoke - {song.get('title', '')}",
                    yt_url,
                ]
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                threading.Thread(
                    target=self._watch_player,
                    args=(self.process, song),
                    daemon=True,
                ).start()
                return
            except Exception as e:
                print(f"[Karaoke] Error al iniciar mpv: {e}")

        # Fallback to browser
        try:
            webbrowser.open(f"{yt_url}&autoplay=1")
        except Exception as e:
            print(f"[Karaoke] Error al abrir navegador: {e}")

    def _watch_player(self, proc: subprocess.Popen, song: dict) -> None:
        proc.wait()
        with self._lock:
            if self.current_song and self.current_song.get("id") == song.get("id"):
                pass
            else:
                return

        self.play_next()

    def _notify(self) -> None:
        if self.on_update:
            try:
                self.on_update(self.get_state())
            except Exception:
                pass
