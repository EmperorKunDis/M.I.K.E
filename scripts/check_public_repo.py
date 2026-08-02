#!/usr/bin/env python3
"""Fail closed on personal data, binaries and incomplete translated guides."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".code_graph_cache",
    "htmlcov",
    "build",
    "dist",
}
SKIP_NAMES = {".coverage"}
TEXT_SUFFIXES = {"", ".md", ".py", ".toml", ".yml", ".yaml", ".txt", ".sh", ".json", ".plist", ".template"}
BINARY_SUFFIXES = {
    ".pt",
    ".pth",
    ".onnx",
    ".safetensors",
    ".gguf",
    ".bin",
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".aac",
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".crt",
    ".cer",
}
GLOBAL_PATTERNS = {
    "absolute macOS user path": re.compile("/" + r"Users/[^/\s]+/"),
    "legacy public env prefix": re.compile(r"\b" + "W" + r"F_[A-Z0-9_]+\b"),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "private or impersonated voice/person reference": re.compile(
        r"(?<!\.)\b(?:"
        + "|".join(
            re.escape(word)
            for word in (
                "Pr" + "aut",
                "Don" + "util",
                "Ri" + "ck",
                "Ros" + "omak",
                "No" + "vas",
                "No" + "vac",
                "Eleven" + "Labs",
                "Co" + "dex",
            )
        )
        + r")\b",
        re.IGNORECASE,
    ),
}
SOURCE_PATTERNS = {
    "named end user": re.compile(r"\bMartin(?:a|ovi|ův|ovo|em)?\b", re.IGNORECASE),
    "old personal data directory": re.compile("Whisper" + "FlowLogs", re.IGNORECASE),
    "voice cloning API parameter": re.compile(
        r"\b(?:" + "ref_" + r"audio|" + "ref_" + r"text)\b"
    ),
}
TRANSLATIONS = (
    "en",
    "uk",
    "be",
    "pl",
    "sk",
    "de",
    "hu",
    "bg",
    "ro",
    "et",
    "lv",
    "lt",
    "ka",
    "hy",
    "az",
    "kk",
    "ky",
    "tg",
    "tk",
    "uz",
)
DOC_MARKERS = (
    "install",
    "first-run",
    "permissions",
    "configuration",
    "controls",
    "privacy",
    "troubleshooting",
    "uninstall",
    "warning",
)


def files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in SKIP_NAMES
        and not any(
            part in SKIP_PARTS or part.endswith(".egg-info") for part in path.relative_to(ROOT).parts
        )
    )


def scan() -> list[str]:
    errors: list[str] = []
    for path in files():
        relative = path.relative_to(ROOT)
        if path.suffix.casefold() in BINARY_SUFFIXES:
            errors.append(f"binary/media/model/certificate forbidden: {relative}")
            continue
        if path.is_symlink():
            errors.append(f"symlink forbidden in public snapshot: {relative}")
            continue
        if path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 text or binary file: {relative}")
            continue
        for label, pattern in GLOBAL_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {relative}")
        if relative.parts and relative.parts[0] in {"src", "scripts", "tests"}:
            for label, pattern in SOURCE_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"{label}: {relative}")
    guides = [ROOT / "README.md", *(ROOT / "docs" / "translations" / f"README.{code}.md" for code in TRANSLATIONS)]
    for guide in guides:
        if not guide.exists():
            errors.append(f"missing language guide: {guide.relative_to(ROOT)}")
            continue
        text = guide.read_text(encoding="utf-8")
        for marker in DOC_MARKERS:
            if f"<!-- mike-doc:{marker} -->" not in text:
                errors.append(f"missing {marker} section: {guide.relative_to(ROOT)}")
    russian = ROOT / "docs" / "translations" / "README.ru.md"
    if russian.exists():
        errors.append("Russian translation is intentionally out of scope: docs/translations/README.ru.md")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    errors = scan()
    if errors:
        print("Public repository gate failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not args.quiet:
        guide_count = 1 + len(TRANSLATIONS)
        print(
            f"Public repository gate passed: {len(files())} files, "
            f"{guide_count} complete language guides."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
