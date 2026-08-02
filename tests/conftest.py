from __future__ import annotations

import json
from pathlib import Path

import pytest

from mike.config import Config, load_config
from mike.paths import AppPaths


@pytest.fixture
def app_paths(tmp_path: Path) -> AppPaths:
    return AppPaths.from_env({"MIKE_HOME": str(tmp_path / "MIKE")})


@pytest.fixture
def config(app_paths: AppPaths) -> Config:
    return load_config(app_paths)


class FakeOllama:
    def __init__(self, replies: list[str] | None = None) -> None:
        self.replies = list(replies or ["Rozumím."])
        self.calls: list[tuple[list[dict[str, str]], dict]] = []

    def chat(self, messages, **kwargs):
        self.calls.append((list(messages), kwargs))
        return self.replies.pop(0) if self.replies else "Rozumím."

    def health(self):
        return {"ok": True, "model_installed": True, "models": ["test:latest"]}


class FakeTTS:
    def __init__(self) -> None:
        self.spoken: list[str] = []
        self.stopped = 0
        self.is_speaking = False

    def speak(self, text: str, **_kwargs) -> bool:
        self.spoken.append(text)
        return True

    def stop(self) -> bool:
        self.stopped += 1
        return True


@pytest.fixture
def fake_ollama() -> FakeOllama:
    return FakeOllama()


@pytest.fixture
def fake_tts() -> FakeTTS:
    return FakeTTS()


class FakeHeaders:
    def __init__(self, content_type: str = "text/html") -> None:
        self.content_type = content_type

    def get_content_type(self) -> str:
        return self.content_type


class FakeResponse:
    def __init__(self, body: str | dict, *, status: int = 200, content_type: str = "text/html") -> None:
        if isinstance(body, dict):
            body = json.dumps(body)
        self.body = body.encode("utf-8")
        self.status = status
        self.headers = FakeHeaders(content_type)

    def read(self, limit: int | None = None) -> bytes:
        return self.body if limit is None else self.body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False
