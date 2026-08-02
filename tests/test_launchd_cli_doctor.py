from __future__ import annotations

import json
import plistlib
from dataclasses import replace
from types import SimpleNamespace

import pytest

import mike.doctor as doctor
import mike.launchd as launchd
from mike.cli import parser
from mike.doctor import Check, as_json
from mike.errors import CollisionError
from mike.ollama import OllamaError
from mike.paths import permission_bits


def test_label_is_stable():
    assert launchd.LABEL == "io.github.emperorkundis.mike"


def test_render_plist_has_only_own_runtime(config):
    payload = plistlib.loads(launchd.render_plist(config, executable="/venv/python"))
    assert payload["Label"] == launchd.LABEL
    assert payload["ProgramArguments"] == ["/venv/python", "-m", "mike.cli", "_run"]
    assert payload["EnvironmentVariables"] == {"MIKE_HOME": str(config.paths.root)}
    text = launchd.render_plist(config).decode("utf-8")
    assert "pkill" not in text
    assert "bootout" not in text


@pytest.mark.parametrize(
    "line",
    [
        "123 python tools/mike_app.py",
        "124 python tools/mic_logger.py",
        "125 whisperflow-miclogger.command",
        "126 MAJKA old-runtime",
    ],
)
def test_legacy_process_detection(line):
    assert launchd.legacy_processes(line) == [line]


def test_unrelated_process_is_ignored():
    assert launchd.legacy_processes("123 python normal_app.py") == []


def test_process_listing_is_empty_when_ps_is_forbidden(monkeypatch):
    def denied(*_args, **_kwargs):
        raise PermissionError("sandbox")

    monkeypatch.setattr(launchd.subprocess, "run", denied)
    assert launchd.process_listing() == ""


def test_collision_preflight_explains_legacy_process(config, monkeypatch):
    monkeypatch.setattr(launchd, "port_available", lambda *_args: True)
    with pytest.raises(CollisionError, match="nebude zastavovat ani mazat"):
        launchd.collision_preflight(config, listing="123 python tools/mike_app.py")


def test_collision_preflight_explains_busy_port(config, monkeypatch):
    monkeypatch.setattr(launchd, "port_available", lambda *_args: False)
    with pytest.raises(CollisionError, match="obsazen"):
        launchd.collision_preflight(config, listing="")


def test_collision_preflight_accepts_clean_host(config, monkeypatch):
    monkeypatch.setattr(launchd, "port_available", lambda *_args: True)
    launchd.collision_preflight(config, listing="")


def test_install_writes_only_own_private_plist(config, monkeypatch, tmp_path):
    monkeypatch.setattr(launchd, "collision_preflight", lambda *_args, **_kwargs: None)
    env = {"MIKE_LAUNCH_AGENTS_DIR": str(tmp_path / "agents")}
    target = launchd.install(config, env=env)
    assert target.name == f"{launchd.LABEL}.plist"
    assert permission_bits(target) == 0o600
    assert list(target.parent.iterdir()) == [target]


def test_start_bootstraps_and_kickstarts_own_label(config, monkeypatch, tmp_path):
    env = {"MIKE_LAUNCH_AGENTS_DIR": str(tmp_path / "agents")}
    target = launchd.plist_path(env)
    target.parent.mkdir()
    target.write_text("plist", encoding="utf-8")
    calls = []
    monkeypatch.setattr(launchd, "is_loaded", lambda: False)
    monkeypatch.setattr(launchd, "collision_preflight", lambda *_args: None)

    def fake_launchctl(*args):
        calls.append(args)
        return SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(launchd, "_launchctl", fake_launchctl)
    launchd.start(config, env=env)
    assert calls[0][0] == "bootstrap"
    assert calls[1] == ("kickstart", "-k", f"gui/{launchd.os.getuid()}/{launchd.LABEL}")


def test_stop_does_not_touch_any_other_label(monkeypatch):
    calls = []
    monkeypatch.setattr(launchd, "is_loaded", lambda: True)
    monkeypatch.setattr(
        launchd,
        "_launchctl",
        lambda *args: calls.append(args) or SimpleNamespace(returncode=0, stderr="", stdout=""),
    )
    assert launchd.stop()
    assert calls == [("bootout", f"gui/{launchd.os.getuid()}/{launchd.LABEL}")]


def test_stop_is_noop_when_not_loaded(monkeypatch):
    monkeypatch.setattr(launchd, "is_loaded", lambda: False)
    assert not launchd.stop()


def test_uninstall_preserves_data(config, monkeypatch, tmp_path):
    env = {"MIKE_LAUNCH_AGENTS_DIR": str(tmp_path / "agents")}
    target = launchd.plist_path(env)
    target.parent.mkdir()
    target.write_text("plist", encoding="utf-8")
    config.paths.ensure()
    marker = config.paths.data / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(launchd, "stop", lambda: False)
    assert launchd.uninstall(env=env)
    assert not target.exists()
    assert marker.exists()


def test_cli_has_requested_public_commands():
    choices = parser()._subparsers._group_actions[0].choices
    public = set(choices) - {"_run"}
    assert public == {"install", "start", "stop", "restart", "status", "doctor", "uninstall"}


def test_doctor_json_shape():
    payload = json.loads(as_json([Check("one", "OK", "fine"), Check("two", "WARN", "note")]))
    assert payload["ok"] is True
    assert payload["checks"][1]["status"] == "WARN"


def test_doctor_json_fails_on_fail():
    payload = json.loads(as_json([Check("one", "FAIL", "bad")]))
    assert payload["ok"] is False


def test_doctor_full_happy_path(config, monkeypatch):
    monkeypatch.setattr(doctor.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(doctor.platform, "machine", lambda: "arm64")
    monkeypatch.setattr(doctor.platform, "platform", lambda: "macOS-test")
    monkeypatch.setattr(doctor.platform, "python_version", lambda: "3.12.7")
    monkeypatch.setattr(doctor.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(doctor, "microphone_permission", lambda: ("OK", "povoleno"))
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda _name: object())
    monkeypatch.setattr(doctor, "port_available", lambda *_args: True)
    monkeypatch.setattr(doctor, "legacy_processes", lambda: [])

    class HealthyOllama:
        def __init__(self, *_args, **_kwargs):
            pass

        def health(self):
            return {"model_installed": True}

    monkeypatch.setattr(doctor, "OllamaClient", HealthyOllama)
    checks = doctor.run_checks(config)
    assert not any(check.status == "FAIL" for check in checks)
    assert {check.name for check in checks} >= {"macOS", "Apple Silicon", "Ollama model", "port"}


def test_doctor_reports_ollama_failure(config, monkeypatch):
    monkeypatch.setattr(doctor, "microphone_permission", lambda: ("WARN", "neznámé"))
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda _name: None)
    monkeypatch.setattr(doctor, "port_available", lambda *_args: False)
    monkeypatch.setattr(doctor, "legacy_processes", lambda: ["legacy"])

    class BrokenOllama:
        def __init__(self, *_args, **_kwargs):
            pass

        def health(self):
            raise OllamaError("offline")

    monkeypatch.setattr(doctor, "OllamaClient", BrokenOllama)
    checks = doctor.run_checks(config)
    assert any(check.name == "Ollama" and check.status == "FAIL" for check in checks)
    assert any(check.name == "stará instalace" and check.status == "WARN" for check in checks)


def test_doctor_accepts_explicitly_disabled_stt(config, monkeypatch):
    config = replace(config, stt=replace(config.stt, enabled=False))
    monkeypatch.setattr(doctor, "microphone_permission", lambda: ("WARN", "neznámé"))
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda _name: None)
    monkeypatch.setattr(doctor, "port_available", lambda *_args: True)
    monkeypatch.setattr(doctor, "legacy_processes", lambda: [])

    class HealthyOllama:
        def __init__(self, *_args, **_kwargs):
            pass

        def health(self):
            return {"model_installed": True}

    monkeypatch.setattr(doctor, "OllamaClient", HealthyOllama)
    checks = doctor.run_checks(config)
    assert any(check.name == "STT" and check.status == "OK" for check in checks)
    assert not any(check.name.startswith("STT ") and check.status == "FAIL" for check in checks)
