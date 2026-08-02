"""Malý klient pro lokální Ollamu; bez cloudového fallbacku."""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from typing import Any

from .errors import MikeError


class OllamaError(MikeError):
    """Lokální model neodpověděl platně."""


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout: float = 90.0,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(  # noqa: S310 - URL is local-only after config validation
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with self._open(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError, urllib.error.URLError) as exc:
            raise OllamaError(f"Lokální Ollama neodpovídá: {exc}") from exc

    def health(self) -> dict[str, Any]:
        payload = self._request("/api/tags")
        names = [item.get("name", "") for item in payload.get("models", [])]
        return {
            "ok": True,
            "model_installed": any(name.split(":")[0] == self.model.split(":")[0] for name in names),
            "models": names,
        }

    def chat(
        self,
        messages: Sequence[dict[str, str]],
        *,
        json_mode: bool = False,
        temperature: float = 0.4,
        max_tokens: int = 420,
    ) -> str:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": list(messages),
            "stream": False,
            "keep_alive": "2m",
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "think": False,
        }
        if json_mode:
            body["format"] = "json"
        try:
            payload = self._request("/api/chat", body)
        except OllamaError as first:
            body.pop("think", None)
            try:
                payload = self._request("/api/chat", body)
            except OllamaError as second:
                raise first from second
        text = payload.get("message", {}).get("content", "")
        if not isinstance(text, str) or not text.strip():
            raise OllamaError("Ollama vrátila prázdnou odpověď.")
        return text.strip()

    async def achat(self, messages: Sequence[dict[str, str]], **kwargs: Any) -> str:
        return await asyncio.to_thread(self.chat, messages, **kwargs)
