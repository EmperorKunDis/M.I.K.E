from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mike_omnivoice_server", ROOT / "scripts" / "omnivoice_server.py")
assert SPEC is not None and SPEC.loader is not None
SERVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVER)


def test_server_starts_unloaded_and_private(config):
    state = SERVER.SynthesisState(config)
    health = state.health()
    assert health == {
        "ok": False,
        "provider": "omnivoice",
        "mode": "design",
        "model_loaded": False,
        "speaking": False,
        "pending": 0,
    }
    assert config.tts.omnivoice_url == "http://127.0.0.1:8130"


def test_server_queue_is_bounded(config):
    state = SERVER.SynthesisState(config)
    for index in range(8):
        assert state.enqueue(f"věta {index}")["queued"]
    with pytest.raises(RuntimeError, match="fronta je plná"):
        state.enqueue("devátá")
    assert state.stop()
    assert state.health()["pending"] == 0


def test_server_stop_terminates_only_current_playback(config):
    class FakePlayback:
        terminated = False

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

    state = SERVER.SynthesisState(config)
    playback = FakePlayback()
    state._playback = playback
    state._speaking = True
    assert state.stop()
    assert playback.terminated


def test_public_server_has_no_voice_clone_parameters():
    source = (ROOT / "scripts" / "omnivoice_server.py").read_text(encoding="utf-8")
    assert ("ref_" + "audio") not in source
    assert ("ref_" + "text") not in source


def test_service_template_uses_only_own_label():
    template = (ROOT / "scripts" / "omnivoice_service.plist.template").read_text(encoding="utf-8")
    assert "__LABEL__" in template
    assert "WhisperFlow" not in template
    assert "MAJKA" not in template
