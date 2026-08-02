"""Výslovně zapínaný hlasový read-only terminál bez shellu."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .errors import FeatureDisabledError, PolicyError

VOICE_MARKER = re.compile(
    r"\b(?:v\s+)?termin[aá]lu\s+(?:spusť|spust|proveď|proved|ukaž|ukaz)\s+(.+)$",
    re.IGNORECASE,
)
SHELL_META = re.compile(r"[|;&><`\n\r]|\$\(|\$\{")
SIMPLE_COMMANDS = {"pwd", "ls", "rg", "head", "tail", "wc", "stat", "file", "du", "df", "uname", "sw_vers"}
GIT_SUBCOMMANDS = {"status", "log", "diff", "show", "branch", "rev-parse", "remote"}


@dataclass(frozen=True)
class TerminalResult:
    command: tuple[str, ...]
    returncode: int
    output: str
    truncated: bool = False


def extract_voice_command(text: str) -> str | None:
    match = VOICE_MARKER.search(text.strip())
    return match.group(1).strip() if match else None


class ReadOnlyTerminal:
    def __init__(self, roots: tuple[Path, ...], *, enabled: bool, timeout: float = 8.0) -> None:
        self.roots = tuple(path.resolve() for path in roots)
        self.enabled = enabled
        self.timeout = timeout

    def _validate(self, command: str) -> tuple[str, ...]:
        if not self.enabled:
            raise FeatureDisabledError("Read-only terminál je vypnutý v config.toml.")
        if SHELL_META.search(command):
            raise PolicyError("Shell operátory, přesměrování a více příkazů nejsou podporovány.")
        try:
            args = tuple(shlex.split(command, posix=True))
        except ValueError as exc:
            raise PolicyError("Příkaz má neplatné uvozovky.") from exc
        if not args:
            raise PolicyError("Příkaz je prázdný.")
        executable = Path(args[0]).name
        if executable == "git":
            if len(args) < 2 or args[1] not in GIT_SUBCOMMANDS:
                raise PolicyError("Povolené git operace jsou pouze status/log/diff/show/branch/rev-parse/remote.")
            if args[1] == "remote" and any(item not in {"remote", "-v", "--verbose"} for item in args[1:]):
                raise PolicyError("Git remote dovoluje pouze bezpečný výpis -v.")
        elif executable == "find":
            forbidden = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf"}
            if any(item in forbidden for item in args[1:]):
                raise PolicyError("Zápisové a spouštěcí akce find nejsou podporovány.")
        elif executable == "ollama":
            if args[1:] != ("list",):
                raise PolicyError("Z Ollamy je povolen pouze příkaz list.")
        elif executable not in SIMPLE_COMMANDS:
            raise PolicyError(f"Příkaz {executable!r} není na read-only allowlistu.")
        if executable == "rg" and any(item.startswith("--pre") for item in args[1:]):
            raise PolicyError("rg --pre může spouštět program a není povolen.")
        self._validate_paths(args[1:])
        return args

    def _validate_paths(self, args: tuple[str, ...]) -> None:
        for item in args:
            if item.startswith("-") or not item.startswith(os.sep):
                continue
            path = Path(item).expanduser().resolve(strict=False)
            if not any(path == root or root in path.parents for root in self.roots):
                raise PolicyError("Absolutní cesta leží mimo povolené terminal_roots.")

    def run(self, command: str, *, cwd: Path | None = None, max_chars: int = 8000) -> TerminalResult:
        args = self._validate(command)
        if cwd is None:
            if not self.roots:
                raise PolicyError("Nejdřív nastavte alespoň jeden features.terminal_roots.")
            cwd = self.roots[0]
        resolved = cwd.resolve()
        if not any(resolved == root or root in resolved.parents for root in self.roots):
            raise PolicyError("Pracovní adresář leží mimo terminal_roots.")
        completed = subprocess.run(
            args,
            cwd=resolved,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=self.timeout,
            check=False,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"), "LANG": "C.UTF-8"},
        )
        output = completed.stdout or ""
        truncated = len(output) > max_chars
        if truncated:
            output = output[:max_chars] + "\n… výstup zkrácen …"
        return TerminalResult(args, completed.returncode, output.strip(), truncated)
