"""Privátní cesty M.I.K.E. bez vazby na konkrétní uživatelský účet."""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Všechny per-user soubory pod jedním privátním adresářem."""

    root: Path
    config: Path
    data: Path
    logs: Path
    database: Path
    lock: Path
    pid: Path
    voiceprint: Path
    prompt_candidate: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> AppPaths:
        values = os.environ if env is None else env
        root = Path(
            values.get(
                "MIKE_HOME",
                str(Path.home() / "Library" / "Application Support" / "MIKE"),
            )
        ).expanduser()
        config = Path(values.get("MIKE_CONFIG", str(root / "config.toml"))).expanduser()
        return cls(
            root=root,
            config=config,
            data=root / "data",
            logs=root / "logs",
            database=root / "data" / "mike.sqlite3",
            lock=root / "data" / "mike.lock",
            pid=root / "data" / "mike.pid",
            voiceprint=root / "data" / "voiceprint.npy",
            prompt_candidate=root / "data" / "prompt-candidate.json",
        )

    def ensure(self) -> None:
        """Vytvoří adresáře s režimem 700 a opraví příliš volný režim."""
        for directory in (self.root, self.data, self.logs, self.config.parent):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory.chmod(0o700)


def secure_file(path: Path) -> None:
    """Nastaví existujícímu souboru režim 600."""
    if path.exists():
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def permission_bits(path: Path) -> int | None:
    """Vrátí unixová oprávnění bez typu souboru."""
    try:
        return stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        return None
