"""Bezpečná správa vlastního LaunchAgentu a kolizí se starší instalací."""

from __future__ import annotations

import os
import plistlib
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .config import Config, ensure_default_config
from .errors import CollisionError, MikeError
from .paths import secure_file

LABEL = "io.github.emperorkundis.mike"
LEGACY_MARKERS = (
    "tools/mike_app.py",
    "tools/mic_logger.py",
    "whisperflow-miclogger",
    "MAJKA",
)


@dataclass(frozen=True)
class ServiceStatus:
    installed: bool
    loaded: bool
    healthy: bool
    pid: int | None
    detail: str


def launch_agents_dir(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    return Path(values.get("MIKE_LAUNCH_AGENTS_DIR", str(Path.home() / "Library" / "LaunchAgents"))).expanduser()


def plist_path(env: Mapping[str, str] | None = None) -> Path:
    return launch_agents_dir(env) / f"{LABEL}.plist"


def process_listing() -> str:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return completed.stdout if completed.returncode == 0 else ""


def legacy_processes(listing: str | None = None) -> list[str]:
    listing = process_listing() if listing is None else listing
    return [
        line.strip()
        for line in listing.splitlines()
        if any(marker.casefold() in line.casefold() for marker in LEGACY_MARKERS) and LABEL not in line
    ]


def port_available(host: str, port: int) -> bool:
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def collision_preflight(config: Config, *, listing: str | None = None) -> None:
    legacy = legacy_processes(listing)
    if legacy:
        sample = "\n  ".join(legacy[:5])
        raise CollisionError(
            "Běží starší Whisper Flow/MAJKA proces. M.I.K.E. jej nebude zastavovat ani mazat. "
            f"Nejdřív jej ukončete jeho vlastním nástrojem:\n  {sample}"
        )
    if not port_available(config.server.host, config.server.port):
        raise CollisionError(
            f"Port {config.server.host}:{config.server.port} je obsazen. Změňte server.port, "
            "nebo bezpečně ukončete službu, které port patří."
        )


def render_plist(config: Config, executable: str | None = None) -> bytes:
    executable = executable or sys.executable
    payload = {
        "Label": LABEL,
        "ProgramArguments": [executable, "-m", "mike.cli", "_run"],
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
        "ProcessType": "Interactive",
        "EnvironmentVariables": {"MIKE_HOME": str(config.paths.root)},
        "StandardOutPath": str(config.paths.logs / "runtime.log"),
        "StandardErrorPath": str(config.paths.logs / "runtime-error.log"),
    }
    return plistlib.dumps(payload, fmt=plistlib.FMT_XML, sort_keys=True)


def install(config: Config, *, env: Mapping[str, str] | None = None) -> Path:
    collision_preflight(config)
    ensure_default_config(config.paths)
    target = plist_path(env)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(render_plist(config))
    secure_file(target)
    return target


def _launchctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["launchctl", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _domain() -> str:
    return f"gui/{os.getuid()}"


def is_loaded() -> bool:
    return _launchctl("print", f"{_domain()}/{LABEL}").returncode == 0


def start(config: Config, *, env: Mapping[str, str] | None = None) -> None:
    target = plist_path(env)
    if not target.exists():
        raise MikeError("M.I.K.E. není nainstalovaný. Nejprve spusťte mike install.")
    if not is_loaded():
        collision_preflight(config)
        result = _launchctl("bootstrap", _domain(), str(target))
        if result.returncode != 0:
            raise MikeError(f"launchctl bootstrap selhal: {result.stderr.strip()}")
    result = _launchctl("kickstart", "-k", f"{_domain()}/{LABEL}")
    if result.returncode != 0:
        raise MikeError(f"launchctl kickstart selhal: {result.stderr.strip()}")


def stop() -> bool:
    if not is_loaded():
        return False
    result = _launchctl("bootout", f"{_domain()}/{LABEL}")
    if result.returncode != 0:
        raise MikeError(f"launchctl bootout selhal: {result.stderr.strip()}")
    return True


def uninstall(*, env: Mapping[str, str] | None = None) -> bool:
    stop()
    target = plist_path(env)
    if not target.exists():
        return False
    target.unlink()
    return True


def health(config: Config, timeout: float = 1.5) -> bool:
    url = f"http://{config.server.host}:{config.server.port}/api/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def status(config: Config, *, env: Mapping[str, str] | None = None) -> ServiceStatus:
    target = plist_path(env)
    pid = None
    try:
        pid = int(config.paths.pid.read_text(encoding="ascii").strip())
        os.kill(pid, 0)
    except (FileNotFoundError, ValueError, OSError):
        pid = None
    loaded = is_loaded()
    healthy = health(config)
    if healthy:
        detail = f"Dashboard odpovídá na {config.server.host}:{config.server.port}."
    elif loaded:
        detail = "LaunchAgent je načtený, ale dashboard neodpovídá. Zkontrolujte logy."
    else:
        detail = "Služba neběží."
    return ServiceStatus(target.exists(), loaded, healthy, pid, detail)
