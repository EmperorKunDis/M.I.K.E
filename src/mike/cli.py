"""Veřejné příkazy ``mike`` a interní vstup runtime pro launchd."""

from __future__ import annotations

import argparse
import logging
import sys
import time

from .config import ensure_default_config, load_config
from .doctor import as_json, run_checks
from .errors import MikeError
from .launchd import install, start, status, stop, uninstall
from .paths import AppPaths
from .runtime import MikeRuntime


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="mike", description="M.I.K.E. — lokální český hlasový asistent")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="vytvoří privátní config a vlastní LaunchAgent")
    commands.add_parser("start", help="spustí nainstalovaný LaunchAgent")
    commands.add_parser("stop", help="zastaví pouze vlastní LaunchAgent")
    commands.add_parser("restart", help="bezpečně restartuje pouze vlastní LaunchAgent")
    commands.add_parser("status", help="ukáže lokální stav bez citlivých dat")
    doctor = commands.add_parser("doctor", help="zkontroluje platformu, oprávnění a lokální služby")
    doctor.add_argument("--json", action="store_true", help="strojově čitelný výstup")
    commands.add_parser("uninstall", help="odstraní LaunchAgent; data ponechá")
    commands.add_parser("_run", help=argparse.SUPPRESS)
    return root


def _print_status(config) -> int:
    current = status(config)
    print(f"Instalace: {'ano' if current.installed else 'ne'}")
    print(f"LaunchAgent: {'načten' if current.loaded else 'nenačten'}")
    print(f"Dashboard: {'zdravý' if current.healthy else 'nedostupný'}")
    print(f"PID: {current.pid or '—'}")
    print(current.detail)
    return 0 if current.healthy else 1


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    paths = AppPaths.from_env()
    try:
        if args.command == "install":
            ensure_default_config(paths)
            config = load_config(paths)
            target = install(config)
            print(f"Nainstalováno: {target}")
            print("Žádná starší instalace ani proces nebyly zastaveny nebo smazány.")
            print("Spusťte: mike start")
            return 0
        config = load_config(paths)
        if args.command == "start":
            start(config)
            print("M.I.K.E. se spouští.")
            return 0
        if args.command == "stop":
            print("M.I.K.E. zastaven." if stop() else "M.I.K.E. nebyl spuštěn.")
            return 0
        if args.command == "restart":
            stop()
            time.sleep(0.3)
            start(config)
            print("M.I.K.E. restartován.")
            return 0
        if args.command == "status":
            return _print_status(config)
        if args.command == "doctor":
            checks = run_checks(config)
            if args.json:
                print(as_json(checks))
            else:
                for check in checks:
                    print(f"[{check.status:4}] {check.name}: {check.detail}")
            return 1 if any(check.status == "FAIL" for check in checks) else 0
        if args.command == "uninstall":
            removed = uninstall()
            print("LaunchAgent odstraněn." if removed else "LaunchAgent nebyl nainstalován.")
            print(f"Soukromá data zůstala v {paths.root}")
            return 0
        if args.command == "_run":
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            )
            MikeRuntime(config).run()
            return 0
    except (MikeError, RuntimeError) as exc:
        print(f"Chyba: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
