"""Read-only diagnostika platformy, soukromí, závislostí a lokálních služeb."""

from __future__ import annotations

import importlib.util
import json
import platform
import shutil
import sys
from dataclasses import asdict, dataclass

from .config import Config
from .launchd import legacy_processes, port_available
from .ollama import OllamaClient, OllamaError
from .security import is_private_path
from .tts import OmniVoiceError, OmniVoiceTTS


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def microphone_permission() -> tuple[str, str]:
    try:
        from AVFoundation import AVCaptureDevice, AVMediaTypeAudio
    except ImportError:
        return "WARN", "Stav TCC nelze bez PyObjC přečíst; oprávnění se vyžádá při prvním startu."
    value = int(AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio))
    mapping = {
        0: ("WARN", "O oprávnění mikrofonu zatím nebylo požádáno."),
        1: ("FAIL", "Přístup k mikrofonu je omezen systémem."),
        2: ("FAIL", "Přístup k mikrofonu byl zamítnut."),
        3: ("OK", "Přístup k mikrofonu je povolen."),
    }
    return mapping.get(value, ("WARN", f"Neznámý stav oprávnění {value}."))


def run_checks(config: Config) -> list[Check]:
    checks = [
        Check("macOS", "OK" if platform.system() == "Darwin" else "FAIL", platform.platform()),
        Check("Apple Silicon", "OK" if platform.machine() == "arm64" else "FAIL", platform.machine()),
        Check("Python", "OK" if sys.version_info >= (3, 11) else "FAIL", platform.python_version()),
        Check("launchctl", "OK" if shutil.which("launchctl") else "FAIL", shutil.which("launchctl") or "nenalezen"),
        Check(
            "config mode",
            "OK" if is_private_path(config.paths.config, directory=False) else "FAIL",
            str(config.paths.config),
        ),
        Check(
            "data mode", "OK" if is_private_path(config.paths.data, directory=True) else "FAIL", str(config.paths.data)
        ),
        Check("dashboard bind", "OK", f"{config.server.host}:{config.server.port}"),
        Check(
            "telemetrie",
            "OK" if not config.privacy.telemetry else "FAIL",
            "vypnuta" if not config.privacy.telemetry else "zapnuta",
        ),
        Check(
            "raw audio",
            "OK" if not config.privacy.save_raw_audio else "WARN",
            "neukládá se" if not config.privacy.save_raw_audio else "výslovně zapnuto",
        ),
    ]
    permission_status, permission_detail = microphone_permission()
    checks.append(Check("mikrofon", permission_status, permission_detail))
    if config.stt.enabled:
        dependency = "mlx_whisper" if config.stt.backend == "mlx" else "whisper"
        checks.append(
            Check(
                f"STT {config.stt.backend}",
                "OK" if importlib.util.find_spec(dependency) else "FAIL",
                dependency,
            )
        )
    else:
        checks.append(Check("STT", "OK", "výslovně vypnuto"))
    try:
        health = OllamaClient(config.assistant.ollama_url, config.assistant.model, timeout=2).health()
        checks.append(
            Check(
                "Ollama model",
                "OK" if health["model_installed"] else "FAIL",
                config.assistant.model,
            )
        )
    except OllamaError as exc:
        checks.append(Check("Ollama", "FAIL", str(exc)))
    if config.tts.enabled:
        try:
            OmniVoiceTTS(config.tts.omnivoice_url, timeout=2).health()
            checks.append(Check("OmniVoice", "OK", config.tts.omnivoice_url))
        except OmniVoiceError as exc:
            checks.append(Check("OmniVoice", "FAIL", str(exc)))
    else:
        checks.append(Check("OmniVoice", "OK", "TTS je výslovně vypnuté"))
    checks.append(
        Check(
            "port",
            "OK" if port_available(config.server.host, config.server.port) else "WARN",
            "volný"
            if port_available(config.server.host, config.server.port)
            else "obsazený (může patřit běžícímu M.I.K.E.)",
        )
    )
    legacy = legacy_processes()
    checks.append(
        Check(
            "stará instalace",
            "WARN" if legacy else "OK",
            f"nalezeno procesů: {len(legacy)}" if legacy else "kolize nenalezena",
        )
    )
    return checks


def as_json(checks: list[Check]) -> str:
    return json.dumps(
        {"ok": not any(check.status == "FAIL" for check in checks), "checks": [asdict(check) for check in checks]},
        ensure_ascii=False,
        indent=2,
    )
