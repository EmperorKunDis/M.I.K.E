"""Načítání, výchozí hodnoty a validace ``config.toml``."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .errors import ConfigError
from .paths import AppPaths, secure_file

DEFAULT_CONFIG = """# M.I.K.E. v0.1.1 — aplikace a hlasové povely jsou česky.
# Ve výchozím stavu nic neposílá na internet a neukládá surové audio.

[assistant]
model = "gemma3:12b"
ollama_url = "http://127.0.0.1:11434"
always_respond = false
context_turns = 8

[stt]
enabled = true
backend = "mlx"
model = "large-v3-turbo"
language = "cs"
device = ""
silence_ms = 650
max_utterance_ms = 30000

[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0

[server]
host = "127.0.0.1"
port = 8140

[features]
research = false
terminal = false
terminal_roots = []
voiceprint = false
barge_in = true
self_improve = true

[privacy]
telemetry = false
save_raw_audio = false
"""


@dataclass(frozen=True)
class AssistantConfig:
    model: str = "gemma3:12b"
    ollama_url: str = "http://127.0.0.1:11434"
    always_respond: bool = False
    context_turns: int = 8


@dataclass(frozen=True)
class SttConfig:
    enabled: bool = True
    backend: str = "mlx"
    model: str = "large-v3-turbo"
    language: str = "cs"
    device: str = ""
    silence_ms: int = 650
    max_utterance_ms: int = 30_000


@dataclass(frozen=True)
class TtsConfig:
    enabled: bool = True
    omnivoice_url: str = "http://127.0.0.1:8130"
    model: str = "k2-fsa/OmniVoice"
    instruct: str = "male, middle-aged, low pitch"
    num_steps: int = 32
    speed: float = 1.0


@dataclass(frozen=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8140


@dataclass(frozen=True)
class FeatureConfig:
    research: bool = False
    terminal: bool = False
    terminal_roots: tuple[Path, ...] = field(default_factory=tuple)
    voiceprint: bool = False
    barge_in: bool = True
    self_improve: bool = True


@dataclass(frozen=True)
class PrivacyConfig:
    telemetry: bool = False
    save_raw_audio: bool = False


@dataclass(frozen=True)
class Config:
    paths: AppPaths
    assistant: AssistantConfig = field(default_factory=AssistantConfig)
    stt: SttConfig = field(default_factory=SttConfig)
    tts: TtsConfig = field(default_factory=TtsConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)


def ensure_default_config(paths: AppPaths, *, overwrite: bool = False) -> Path:
    """Vytvoří komentovaný výchozí config; existující nikdy bez požadavku nepřepíše."""
    paths.ensure()
    if overwrite or not paths.config.exists():
        paths.config.write_text(DEFAULT_CONFIG, encoding="utf-8")
    secure_file(paths.config)
    return paths.config


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(f"Sekce [{name}] musí být tabulka TOML.")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{name} musí být true nebo false.")
    return value


def _int(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ConfigError(f"{name} musí být celé číslo {low}–{high}.")
    return value


def _float(value: Any, name: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= float(value) <= high:
        raise ConfigError(f"{name} musí být číslo {low}–{high}.")
    return float(value)


def _text(value: Any, name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > max_length:
        raise ConfigError(f"{name} musí být neprázdný text do {max_length} znaků.")
    return value.strip()


def _local_ollama_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise ConfigError("assistant.ollama_url musí mířit na lokální Ollamu.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigError("assistant.ollama_url nesmí obsahovat přihlašovací údaje ani query.")
    return value.rstrip("/")


def _local_omnivoice_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
        raise ConfigError("tts.omnivoice_url musí mířit na http://127.0.0.1.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise ConfigError("tts.omnivoice_url nesmí obsahovat cestu, přihlašovací údaje ani query.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigError("tts.omnivoice_url obsahuje neplatný port.") from exc
    if port is None:
        raise ConfigError("tts.omnivoice_url musí obsahovat port.")
    return value.rstrip("/")


def load_config(
    paths: AppPaths | None = None,
    *,
    env: Mapping[str, str] | None = None,
    create: bool = True,
) -> Config:
    """Načte TOML a omezené veřejné ``MIKE_*`` overrides."""
    values = os.environ if env is None else env
    paths = paths or AppPaths.from_env(values)
    if create:
        ensure_default_config(paths)
    try:
        with paths.config.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Konfigurace neexistuje: {paths.config}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Neplatný TOML v {paths.config}: {exc}") from exc

    assistant = _section(data, "assistant")
    stt = _section(data, "stt")
    tts = _section(data, "tts")
    server = _section(data, "server")
    features = _section(data, "features")
    privacy = _section(data, "privacy")

    model = values.get("MIKE_MODEL", str(assistant.get("model", "gemma3:12b"))).strip()
    if not model or len(model) > 200:
        raise ConfigError("assistant.model je prázdný nebo příliš dlouhý.")
    host = values.get("MIKE_HOST", str(server.get("host", "127.0.0.1")))
    if host not in {"127.0.0.1", "::1"}:
        raise ConfigError("server.host musí být 127.0.0.1 nebo ::1.")
    backend = str(stt.get("backend", "mlx"))
    if backend not in {"mlx", "torch"}:
        raise ConfigError("stt.backend musí být mlx nebo torch.")

    roots_raw = features.get("terminal_roots", [])
    if not isinstance(roots_raw, list) or not all(isinstance(item, str) for item in roots_raw):
        raise ConfigError("features.terminal_roots musí být seznam cest.")
    roots = tuple(Path(item).expanduser().resolve() for item in roots_raw)

    result = Config(
        paths=paths,
        assistant=AssistantConfig(
            model=model,
            ollama_url=_local_ollama_url(
                values.get("MIKE_OLLAMA_URL", str(assistant.get("ollama_url", "http://127.0.0.1:11434")))
            ),
            always_respond=_bool(assistant.get("always_respond", False), "assistant.always_respond"),
            context_turns=_int(assistant.get("context_turns", 8), "assistant.context_turns", 1, 50),
        ),
        stt=SttConfig(
            enabled=_bool(stt.get("enabled", True), "stt.enabled"),
            backend=backend,
            model=str(stt.get("model", "large-v3-turbo")),
            language=str(stt.get("language", "cs")),
            device=str(stt.get("device", "")),
            silence_ms=_int(stt.get("silence_ms", 650), "stt.silence_ms", 100, 5000),
            max_utterance_ms=_int(stt.get("max_utterance_ms", 30_000), "stt.max_utterance_ms", 1000, 120_000),
        ),
        tts=TtsConfig(
            enabled=_bool(tts.get("enabled", True), "tts.enabled"),
            omnivoice_url=_local_omnivoice_url(
                values.get("MIKE_OMNIVOICE_URL", str(tts.get("omnivoice_url", "http://127.0.0.1:8130")))
            ),
            model=_text(tts.get("model", "k2-fsa/OmniVoice"), "tts.model", 200),
            instruct=_text(tts.get("instruct", "male, middle-aged, low pitch"), "tts.instruct", 200),
            num_steps=_int(tts.get("num_steps", 32), "tts.num_steps", 8, 64),
            speed=_float(tts.get("speed", 1.0), "tts.speed", 0.5, 2.0),
        ),
        server=ServerConfig(
            host=host,
            port=_int(int(values.get("MIKE_PORT", server.get("port", 8140))), "server.port", 1024, 65535),
        ),
        features=FeatureConfig(
            research=_bool(features.get("research", False), "features.research"),
            terminal=_bool(features.get("terminal", False), "features.terminal"),
            terminal_roots=roots,
            voiceprint=_bool(features.get("voiceprint", False), "features.voiceprint"),
            barge_in=_bool(features.get("barge_in", True), "features.barge_in"),
            self_improve=_bool(features.get("self_improve", True), "features.self_improve"),
        ),
        privacy=PrivacyConfig(
            telemetry=_bool(privacy.get("telemetry", False), "privacy.telemetry"),
            save_raw_audio=_bool(privacy.get("save_raw_audio", False), "privacy.save_raw_audio"),
        ),
    )
    if result.privacy.telemetry:
        raise ConfigError("Telemetrie není ve v0.1 implementována a musí zůstat vypnutá.")
    return result
