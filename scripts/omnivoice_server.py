#!/usr/bin/env python3
"""Privátní loopback server OmniVoice pro M.I.K.E.; pouze voice design, bez klonování."""

from __future__ import annotations

import json
import logging
import os
import queue
import signal
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mike.config import Config, load_config
from mike.paths import secure_file

LOG = logging.getLogger("mike.omnivoice")
MAX_TEXT_CHARS = 4000
MAX_BODY_BYTES = 16_384
SAMPLE_RATE = 24_000


class SynthesisState:
    """Serializuje generování, přehrává přes afplay a po sobě maže WAV."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.config.paths.ensure()
        self._model: Any | None = None
        self._soundfile: Any | None = None
        self._queue: queue.Queue[tuple[int, str]] = queue.Queue(maxsize=8)
        self._lock = threading.Lock()
        self._generation = 0
        self._pending = 0
        self._speaking = False
        self._playback: subprocess.Popen[bytes] | None = None
        self._closed = threading.Event()

    def load_model(self) -> None:
        try:
            import soundfile
            import torch
            from omnivoice import OmniVoice
        except ImportError as exc:
            raise RuntimeError('Chybí extra závislosti; nainstalujte ".[omnivoice]".') from exc
        LOG.info("Načítám samostatně licencovaný OmniVoice model na MPS.")
        self._model = OmniVoice.from_pretrained(
            self.config.tts.model,
            device_map="mps",
            dtype=torch.float16,
            load_asr=False,
        )
        self._soundfile = soundfile
        threading.Thread(target=self._worker, name="omnivoice-synthesis", daemon=True).start()

    def health(self) -> dict[str, Any]:
        with self._lock:
            return {
                "ok": self._model is not None,
                "provider": "omnivoice",
                "mode": "design",
                "model_loaded": self._model is not None,
                "speaking": self._speaking,
                "pending": self._pending,
            }

    def enqueue(self, text: str) -> dict[str, Any]:
        with self._lock:
            generation = self._generation
            self._pending += 1
            pending = self._pending
        try:
            self._queue.put_nowait((generation, text))
        except queue.Full as exc:
            with self._lock:
                self._pending -= 1
            raise RuntimeError("OmniVoice fronta je plná.") from exc
        return {"queued": True, "pending": pending}

    def stop(self) -> bool:
        with self._lock:
            self._generation += 1
            process = self._playback
            was_active = self._pending > 0 or self._speaking
        dropped = 0
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
            dropped += 1
        with self._lock:
            self._pending = max(0, self._pending - dropped)
        if process is not None and process.poll() is None:
            process.terminate()
        return was_active or dropped > 0

    def close(self) -> None:
        self._closed.set()
        self.stop()

    def _worker(self) -> None:
        while not self._closed.is_set():
            try:
                generation, text = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                self._synthesize_and_play(generation, text)
            except Exception:
                LOG.exception("OmniVoice syntéza selhala; server pokračuje.")
            finally:
                with self._lock:
                    self._pending = max(0, self._pending - 1)

    def _synthesize_and_play(self, generation: int, text: str) -> None:
        if self._model is None or self._soundfile is None:
            raise RuntimeError("OmniVoice model není načtený.")
        audio = self._model.generate(
            text=text,
            instruct=self.config.tts.instruct,
            num_step=self.config.tts.num_steps,
            speed=self.config.tts.speed,
        )
        sample = audio[0] if isinstance(audio, (list, tuple)) else audio
        descriptor, raw_path = tempfile.mkstemp(prefix="omnivoice-", suffix=".wav", dir=self.config.paths.data)
        os.close(descriptor)
        path = Path(raw_path)
        secure_file(path)
        try:
            self._soundfile.write(path, sample, SAMPLE_RATE)
            with self._lock:
                if generation != self._generation:
                    return
                self._speaking = True
            process = subprocess.Popen(  # noqa: S603 - fixed executable, no shell
                ["/usr/bin/afplay", str(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self._lock:
                self._playback = process
            process.wait()
        finally:
            with self._lock:
                self._playback = None
                self._speaking = False
            path.unlink(missing_ok=True)


STATE: SynthesisState | None = None


class Handler(BaseHTTPRequestHandler):
    """Minimální lokální API kompatibilní s klientem M.I.K.E."""

    def log_message(self, *_args: Any) -> None:
        return

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health" or STATE is None:
            self._json(404, {"error": "not found"})
            return
        self._json(200, STATE.health())

    def do_POST(self) -> None:  # noqa: N802
        if STATE is None:
            self._json(503, {"error": "not ready"})
            return
        if self.path == "/stop":
            self._json(200, {"stopped": STATE.stop()})
            return
        if self.path != "/speak":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY_BYTES:
                raise ValueError("invalid body length")
            payload = json.loads(self.rfile.read(length))
            text = payload.get("text", "").strip()
            if not isinstance(text, str) or not 0 < len(text) <= MAX_TEXT_CHARS:
                raise ValueError("invalid text")
            result = STATE.enqueue(text)
        except (AttributeError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._json(400, {"error": str(exc)})
            return
        except RuntimeError as exc:
            self._json(429, {"error": str(exc)})
            return
        self._json(202, result)


def main() -> int:
    global STATE  # noqa: PLW0603
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()
    if not config.tts.enabled:
        raise SystemExit("TTS je v config.toml vypnuté.")
    parsed = urlparse(config.tts.omnivoice_url)
    host, port = parsed.hostname, parsed.port
    if host != "127.0.0.1" or port is None:
        raise SystemExit("OmniVoice server smí poslouchat jen na 127.0.0.1 s explicitním portem.")
    STATE = SynthesisState(config)
    STATE.load_model()
    server = ThreadingHTTPServer((host, port), Handler)

    def shutdown(*_args: Any) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    for current_signal in (signal.SIGINT, signal.SIGTERM):
        signal.signal(current_signal, shutdown)
    LOG.info("OmniVoice poslouchá pouze na http://%s:%d", host, port)
    try:
        server.serve_forever()
    finally:
        STATE.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
