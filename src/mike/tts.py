"""Lokální klient OmniVoice TTS; žádný systémový ani cloudový fallback."""

from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from .errors import MikeError

LOG = logging.getLogger(__name__)


class OmniVoiceError(MikeError):
    """Lokální OmniVoice služba neodpověděla platně."""


class OmniVoiceTTS:
    """Fronta a barge-in nad loopback API ``/speak``, ``/stop`` a ``/health``."""

    def __init__(
        self,
        base_url: str,
        *,
        enabled: bool = True,
        timeout: float = 5.0,
        opener: Callable[..., Any] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._speaking = False
        self._health_at = 0.0

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(  # noqa: S310 - URL is validated as literal loopback
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with self._open(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise OmniVoiceError(f"Lokální OmniVoice neodpovídá: {exc}") from exc
        if not isinstance(body, dict):
            raise OmniVoiceError("OmniVoice vrátil neplatnou JSON odpověď.")
        return body

    def health(self) -> dict[str, Any]:
        """Ověří připravenost modelu a obnoví krátkou speaking cache."""
        payload = self._request("/health")
        if payload.get("ok") is not True:
            raise OmniVoiceError("OmniVoice model není připravený.")
        with self._lock:
            self._speaking = bool(payload.get("speaking") or payload.get("pending"))
            self._health_at = self._clock()
        return payload

    @property
    def is_speaking(self) -> bool:
        """Vrátí stav bez zahlcení služby dotazem pro každý audio chunk."""
        now = self._clock()
        with self._lock:
            cached = self._speaking
            fresh = now - self._health_at < 0.25
        if fresh or not self.enabled:
            return cached
        try:
            self.health()
        except OmniVoiceError:
            return False
        with self._lock:
            return self._speaking

    def speak(self, text: str, *, wait: bool = False) -> bool:
        """Zařadí text do OmniVoice; ``wait`` zůstává kompatibilní a je asynchronní."""
        del wait
        text = text.strip()[:4000]
        if not self.enabled or not text:
            return False
        try:
            payload = self._request("/speak", {"text": text})
        except OmniVoiceError as exc:
            LOG.warning("OmniVoice TTS selhalo; odpověď zůstává textová: %s", exc)
            return False
        queued = payload.get("queued") is True
        if queued:
            with self._lock:
                self._speaking = True
                self._health_at = self._clock()
        return queued

    def stop(self) -> bool:
        """Přeruší přehrávání a zahodí čekající OmniVoice frontu."""
        if not self.enabled:
            return False
        try:
            payload = self._request("/stop", {})
        except OmniVoiceError:
            return False
        with self._lock:
            self._speaking = False
            self._health_at = self._clock()
        return bool(payload.get("stopped"))
