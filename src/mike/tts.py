"""Systémové macOS TTS přes ``say``; žádné klonování hlasu."""

from __future__ import annotations

import shutil
import subprocess
import threading
from collections.abc import Callable
from typing import Any


class SayTTS:
    def __init__(
        self,
        *,
        enabled: bool = True,
        voice: str = "",
        rate: int = 190,
        say_path: str | None = None,
        popen: Callable[..., Any] | None = None,
    ) -> None:
        self.enabled = enabled
        self.voice = voice.strip()
        self.rate = max(80, min(rate, 500))
        self.say_path = say_path or shutil.which("say") or "/usr/bin/say"
        self._popen = popen or subprocess.Popen
        self._process: Any | None = None
        self._lock = threading.Lock()

    @property
    def is_speaking(self) -> bool:
        with self._lock:
            return self._process is not None and self._process.poll() is None

    def command(self, text: str) -> list[str]:
        args = [self.say_path, "-r", str(self.rate)]
        if self.voice:
            args.extend(["-v", self.voice])
        args.append(text.strip()[:4000])
        return args

    def speak(self, text: str, *, wait: bool = False) -> bool:
        if not self.enabled or not text.strip():
            return False
        self.stop()
        process = self._popen(
            self.command(text),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with self._lock:
            self._process = process
        if wait:
            process.wait()
            with self._lock:
                if self._process is process:
                    self._process = None
        else:
            threading.Thread(target=self._reap, args=(process,), daemon=True).start()
        return True

    def _reap(self, process: Any) -> None:
        process.wait()
        with self._lock:
            if self._process is process:
                self._process = None

    def stop(self) -> bool:
        with self._lock:
            process = self._process
            self._process = None
        if process is None or process.poll() is not None:
            return False
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=1)
        return True
