from __future__ import annotations

import json
import subprocess
import urllib.error
from types import SimpleNamespace

import pytest

from mike.errors import FeatureDisabledError, PolicyError
from mike.terminal import ReadOnlyTerminal, extract_voice_command
from mike.tts import OmniVoiceError, OmniVoiceTTS


class JsonResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_omnivoice_speak_posts_only_text_to_loopback():
    calls = []

    def opener(request, **kwargs):
        calls.append((request, kwargs))
        return JsonResponse({"queued": True, "pending": 1})

    tts = OmniVoiceTTS("http://127.0.0.1:8130", opener=opener)
    assert tts.speak("Ahoj")
    request, kwargs = calls[0]
    assert request.full_url == "http://127.0.0.1:8130/speak"
    assert request.get_method() == "POST"
    assert json.loads(request.data) == {"text": "Ahoj"}
    assert kwargs["timeout"] == 5.0


def test_disabled_or_empty_tts_does_not_call_service():
    called = []

    def opener(*args, **kwargs):
        called.append((args, kwargs))

    assert not OmniVoiceTTS("http://127.0.0.1:8130", enabled=False, opener=opener).speak("Ahoj")
    assert not OmniVoiceTTS("http://127.0.0.1:8130", opener=opener).speak("  ")
    assert called == []


def test_omnivoice_text_is_bounded():
    requests = []

    def opener(request, **_kwargs):
        requests.append(request)
        return JsonResponse({"queued": True})

    assert OmniVoiceTTS("http://127.0.0.1:8130", opener=opener).speak("x" * 5000)
    assert len(json.loads(requests[0].data)["text"]) == 4000


def test_omnivoice_stop_uses_local_api():
    requests = []

    def opener(request, **_kwargs):
        requests.append(request)
        return JsonResponse({"stopped": True})

    tts = OmniVoiceTTS("http://127.0.0.1:8130", opener=opener)
    assert tts.stop()
    assert requests[0].full_url.endswith("/stop")
    assert json.loads(requests[0].data) == {}


def test_omnivoice_health_and_speaking_cache():
    calls = []
    now = [1.0]

    def opener(request, **_kwargs):
        calls.append(request)
        return JsonResponse({"ok": True, "speaking": True, "pending": 0})

    tts = OmniVoiceTTS("http://127.0.0.1:8130", opener=opener, clock=lambda: now[0])
    assert tts.health()["ok"]
    assert tts.is_speaking
    assert len(calls) == 1
    now[0] += 0.3
    assert tts.is_speaking
    assert len(calls) == 2


def test_omnivoice_failure_keeps_reply_text_only():
    def offline(*_args, **_kwargs):
        raise urllib.error.URLError("offline")

    tts = OmniVoiceTTS("http://127.0.0.1:8130", opener=offline)
    assert not tts.speak("Ahoj")
    assert not tts.stop()
    assert not tts.is_speaking
    with pytest.raises(OmniVoiceError, match="neodpovídá"):
        tts.health()


def test_omnivoice_rejects_unready_health():
    tts = OmniVoiceTTS("http://127.0.0.1:8130", opener=lambda *_args, **_kwargs: JsonResponse({"ok": False}))
    with pytest.raises(OmniVoiceError, match="není připravený"):
        tts.health()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Majku, v terminálu spusť git status", "git status"),
        ("v terminálu proveď pwd", "pwd"),
        ("V TERMINÁLU UKAŽ ls -la", "ls -la"),
        ("Majku napiš odpověď", None),
    ],
)
def test_extract_voice_terminal_command(text, expected):
    assert extract_voice_command(text) == expected


@pytest.fixture
def terminal(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    return ReadOnlyTerminal((root,), enabled=True), root


@pytest.mark.parametrize(
    "command",
    [
        "pwd",
        "ls -la",
        "rg chyba src",
        "head -20 README.md",
        "tail -5 log.txt",
        "wc -l README.md",
        "stat README.md",
        "file README.md",
        "du -sh .",
        "df -h",
        "uname -a",
        "sw_vers",
        "git status --short",
        "git log -5",
        "git diff --stat",
        "git show HEAD",
        "git branch --list",
        "git rev-parse HEAD",
        "git remote -v",
        "ollama list",
        "find . -maxdepth 2 -type f",
    ],
)
def test_read_only_allowlist_accepts(command, terminal):
    policy, _root = terminal
    assert policy._validate(command)


@pytest.mark.parametrize(
    "command",
    [
        "rm file",
        "touch file",
        "python script.py",
        "bash -c pwd",
        "git add .",
        "git commit -m x",
        "git push",
        "git remote add origin x",
        "ollama pull model",
        "find . -delete",
        "find . -exec echo {} ;",
        "rg --pre helper pattern",
        "pwd | tee out",
        "pwd > out",
        "pwd && whoami",
        "$(whoami)",
        "echo `whoami`",
        "echo ${HOME}",
        "echo\nwhoami",
    ],
)
def test_write_or_shell_commands_are_rejected(command, terminal):
    policy, _root = terminal
    with pytest.raises(PolicyError):
        policy._validate(command)


def test_terminal_must_be_enabled(tmp_path):
    terminal = ReadOnlyTerminal((tmp_path,), enabled=False)
    with pytest.raises(FeatureDisabledError):
        terminal.run("pwd")


def test_terminal_requires_root():
    terminal = ReadOnlyTerminal((), enabled=True)
    with pytest.raises(PolicyError, match="terminal_roots"):
        terminal.run("pwd")


def test_absolute_path_outside_root_is_rejected(terminal):
    policy, _root = terminal
    with pytest.raises(PolicyError, match="mimo"):
        policy._validate("ls /private/tmp/outside")


def test_terminal_executes_without_shell(monkeypatch, terminal):
    policy, root = terminal
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="čistý výstup")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = policy.run("git status --short", cwd=root)
    assert result.command == ("git", "status", "--short")
    assert calls[0][1]["cwd"] == root
    assert "shell" not in calls[0][1]


def test_terminal_output_is_bounded(monkeypatch, terminal):
    policy, root = terminal
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="x" * 100),
    )
    result = policy.run("pwd", cwd=root, max_chars=20)
    assert result.truncated
    assert "zkrácen" in result.output
