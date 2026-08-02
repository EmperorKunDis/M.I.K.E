from __future__ import annotations

import pytest

from mike.config import DEFAULT_CONFIG, ConfigError, ensure_default_config, load_config
from mike.paths import AppPaths, permission_bits, secure_file


def replace_config(paths: AppPaths, old: str, new: str) -> None:
    ensure_default_config(paths)
    text = paths.config.read_text(encoding="utf-8").replace(old, new)
    paths.config.write_text(text, encoding="utf-8")


def test_default_paths_are_under_application_support(monkeypatch):
    monkeypatch.delenv("MIKE_HOME", raising=False)
    paths = AppPaths.from_env()
    assert paths.root.name == "MIKE"
    assert paths.root.parent.name == "Application Support"


def test_mike_home_override_is_supported(tmp_path):
    paths = AppPaths.from_env({"MIKE_HOME": str(tmp_path / "isolated")})
    assert paths.root == tmp_path / "isolated"


def test_mike_config_override_is_supported(tmp_path):
    paths = AppPaths.from_env({"MIKE_HOME": str(tmp_path / "home"), "MIKE_CONFIG": str(tmp_path / "custom.toml")})
    assert paths.config == tmp_path / "custom.toml"


def test_paths_are_private(app_paths):
    app_paths.ensure()
    for path in (app_paths.root, app_paths.data, app_paths.logs):
        assert permission_bits(path) == 0o700


def test_config_is_created_with_mode_600(app_paths):
    ensure_default_config(app_paths)
    assert permission_bits(app_paths.config) == 0o600


def test_secure_file_repairs_mode(app_paths):
    app_paths.ensure()
    app_paths.config.write_text("x", encoding="utf-8")
    app_paths.config.chmod(0o644)
    secure_file(app_paths.config)
    assert permission_bits(app_paths.config) == 0o600


def test_existing_config_is_not_overwritten(app_paths):
    app_paths.ensure()
    app_paths.config.write_text("[assistant]\nmodel='custom'\n", encoding="utf-8")
    ensure_default_config(app_paths)
    assert "custom" in app_paths.config.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "needle",
    [
        "telemetry = false",
        "save_raw_audio = false",
        'host = "127.0.0.1"',
        "research = false",
        "terminal = false",
        "voiceprint = false",
        "[assistant]",
        "[stt]",
        "[tts]",
        "[server]",
        "[features]",
        "[privacy]",
    ],
)
def test_default_config_contains_safe_setting(needle):
    assert needle in DEFAULT_CONFIG


def test_load_defaults(config):
    assert config.server.host == "127.0.0.1"
    assert config.server.port == 8140
    assert config.stt.language == "cs"
    assert config.tts.omnivoice_url == "http://127.0.0.1:8130"
    assert config.tts.model == "k2-fsa/OmniVoice"
    assert not config.features.research
    assert not config.privacy.save_raw_audio


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.5", "example.com", "localhost"])
def test_dashboard_rejects_non_literal_loopback(app_paths, host):
    replace_config(app_paths, 'host = "127.0.0.1"', f'host = "{host}"')
    with pytest.raises(ConfigError, match="server.host"):
        load_config(app_paths)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com:11434",
        "http://192.168.1.2:11434",
        "ftp://127.0.0.1:11434",
        "http://user:pass@127.0.0.1:11434",
        "http://127.0.0.1:11434/?token=x",
    ],
)
def test_ollama_must_be_local_and_credential_free(app_paths, url):
    replace_config(app_paths, "http://127.0.0.1:11434", url)
    with pytest.raises(ConfigError, match="ollama_url"):
        load_config(app_paths)


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:8130",
        "http://localhost:8130",
        "http://192.168.1.2:8130",
        "http://127.0.0.1",
        "http://127.0.0.1:notaport",
        "http://user:pass@127.0.0.1:8130",
        "http://127.0.0.1:8130/speak",
        "http://127.0.0.1:8130?token=x",
    ],
)
def test_omnivoice_must_be_literal_loopback_and_credential_free(app_paths, url):
    replace_config(app_paths, "http://127.0.0.1:8130", url)
    with pytest.raises(ConfigError, match="tts.omnivoice_url"):
        load_config(app_paths)


@pytest.mark.parametrize("backend", ["cuda", "remote", "", "mlx-whisper"])
def test_unknown_stt_backend_is_rejected(app_paths, backend):
    replace_config(app_paths, 'backend = "mlx"', f'backend = "{backend}"')
    with pytest.raises(ConfigError, match="stt.backend"):
        load_config(app_paths)


@pytest.mark.parametrize(("old", "new", "message"), [
    ('model = "k2-fsa/OmniVoice"', 'model = ""', "tts.model"),
    ('instruct = "male, middle-aged, low pitch"', 'instruct = ""', "tts.instruct"),
])
def test_omnivoice_text_settings_cannot_be_empty(app_paths, old, new, message):
    replace_config(app_paths, old, new)
    with pytest.raises(ConfigError, match=message):
        load_config(app_paths)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("port = 8140", "port = 80", "server.port"),
        ("num_steps = 32", "num_steps = 2", "tts.num_steps"),
        ("speed = 1.0", "speed = 4.0", "tts.speed"),
        ("context_turns = 8", "context_turns = 0", "assistant.context_turns"),
        ("silence_ms = 650", "silence_ms = 10", "stt.silence_ms"),
        ("max_utterance_ms = 30000", "max_utterance_ms = 500", "stt.max_utterance_ms"),
    ],
)
def test_numeric_bounds(app_paths, old, new, message):
    replace_config(app_paths, old, new)
    with pytest.raises(ConfigError, match=message):
        load_config(app_paths)


def test_telemetry_cannot_be_enabled(app_paths):
    replace_config(app_paths, "telemetry = false", "telemetry = true")
    with pytest.raises(ConfigError, match="Telemetrie"):
        load_config(app_paths)


def test_mike_environment_overrides(app_paths):
    config = load_config(
        app_paths,
        env={
            "MIKE_HOME": str(app_paths.root),
            "MIKE_MODEL": "local:test",
            "MIKE_PORT": "9123",
            "MIKE_HOST": "::1",
            "MIKE_OLLAMA_URL": "http://localhost:11434",
            "MIKE_OMNIVOICE_URL": "http://127.0.0.1:9130",
        },
    )
    assert config.assistant.model == "local:test"
    assert config.server.port == 9123
    assert config.server.host == "::1"
    assert config.tts.omnivoice_url == "http://127.0.0.1:9130"


def test_no_legacy_environment_prefix_in_default_config():
    assert ("W" + "F_") not in DEFAULT_CONFIG


def test_terminal_roots_are_resolved(app_paths, tmp_path):
    root = tmp_path / "allowed"
    root.mkdir()
    replace_config(app_paths, "terminal_roots = []", f'terminal_roots = ["{root}"]')
    config = load_config(app_paths)
    assert config.features.terminal_roots == (root.resolve(),)
