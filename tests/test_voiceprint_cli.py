from __future__ import annotations

import builtins
from pathlib import Path

import pytest

import mike.voiceprint as voiceprint


def test_voiceprint_available_reflects_file(tmp_path):
    path = tmp_path / "voiceprint.npy"
    gate = voiceprint.VoiceprintGate(path)
    assert not gate.available()
    path.write_bytes(b"placeholder")
    assert gate.available()


def test_voiceprint_dependencies_explain_missing_extra(tmp_path, monkeypatch):
    real_import = builtins.__import__

    def without_voice(name, *args, **kwargs):
        if name in {"numpy", "resemblyzer"}:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_voice)
    gate = voiceprint.VoiceprintGate(tmp_path / "voiceprint.npy")
    with pytest.raises(RuntimeError, match="sadu voice"):
        gate._dependencies()


def test_voiceprint_main_enrolls_locally(tmp_path, monkeypatch):
    home = tmp_path / "MIKE"
    audio = tmp_path / "own.wav"
    audio.write_bytes(b"RIFF")
    enrolled: list[Path] = []
    monkeypatch.setenv("MIKE_HOME", str(home))
    monkeypatch.setattr(
        voiceprint.VoiceprintGate,
        "enroll_file",
        lambda _self, path: enrolled.append(path),
    )
    assert voiceprint.main([str(audio)]) == 0
    assert enrolled == [audio]
    assert (home / "config.toml").exists()


def test_voiceprint_main_rejects_missing_file(tmp_path):
    with pytest.raises(SystemExit):
        voiceprint.main([str(tmp_path / "missing.wav")])
