#!/usr/bin/env python3
"""Inventory direct declared Python dependencies without contacting a registry."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENIED = re.compile(r"(?:^|\W)(?:AGPL|SSPL|GPL)(?:\W|$)", re.IGNORECASE)


def declared_names() -> list[str]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    requirements = list(project.get("dependencies", []))
    for values in project.get("optional-dependencies", {}).values():
        requirements.extend(values)
    names = {re.split(r"[<>=!~\[; ]", item, maxsplit=1)[0].strip() for item in requirements}
    return sorted(name for name in names if name)


def inventory() -> list[dict[str, str]]:
    rows = []
    for name in declared_names():
        try:
            metadata = importlib.metadata.metadata(name)
            license_value = metadata.get("License-Expression", "").strip() or metadata.get("License", "").strip()
            if not license_value:
                classifiers = metadata.get_all("Classifier") or []
                license_value = "; ".join(
                    item.removeprefix("License :: ") for item in classifiers if item.startswith("License ::")
                )
            rows.append({"name": name, "version": metadata.get("Version", ""), "license": license_value or "UNKNOWN"})
        except importlib.metadata.PackageNotFoundError:
            rows.append({"name": name, "version": "NOT_INSTALLED", "license": "NOT_INSTALLED"})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = inventory()
    print(
        json.dumps(rows, ensure_ascii=False, indent=2)
        if args.json
        else "\n".join(f"{row['name']} {row['version']} — {row['license']}" for row in rows)
    )
    denied = [
        row for row in rows if row["license"] not in {"UNKNOWN", "NOT_INSTALLED"} and DENIED.search(row["license"])
    ]
    unknown_installed = [row for row in rows if row["license"] == "UNKNOWN"]
    if args.check and (denied or unknown_installed):
        for row in denied + unknown_installed:
            print(f"license review required: {row['name']} — {row['license']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
