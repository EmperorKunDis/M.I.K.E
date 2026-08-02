from __future__ import annotations

import subprocess
import threading
from types import SimpleNamespace

import pytest

from mike.errors import FeatureDisabledError, PolicyError
from mike.terminal import ReadOnlyTerminal, extract_voice_command
from mike.tts import SayTTS


class FakeProcess:
    def __init__(self, running=True, wait_blocks=False):
        self.running = running
        self.wait_blocks = wait_blocks
        self.terminated = False
        self.killed = False
        self.done = threading.Event()

    def poll(self):
        return None if self.running else 0

    def wait(self, timeout=None):
        if self.wait_blocks and self.running:
            self.done.wait(timeout)
        self.running = False
        return 0

    def terminate(self):
        self.terminated = True
        self.running = False
        self.done.set()

    def kill(self):
        self.killed = True
        self.running = False
        self.done.set()


def test_say_command_has_no_shell():
    tts = SayTTS(voice="Zuzana", rate=200, say_path="/usr/bin/say")
    assert tts.command("Ahoj") == ["/usr/bin/say", "-r", "200", "-v", "Zuzana", "Ahoj"]


def test_say_rate_is_bounded():
    assert SayTTS(rate=1).rate == 80
    assert SayTTS(rate=999).rate == 500


def test_disabled_tts_does_not_spawn():
    called = []
    assert not SayTTS(enabled=False, popen=lambda *args, **kwargs: called.append(args)).speak("Ahoj")
    assert called == []


def test_empty_tts_does_not_spawn():
    called = []
    assert not SayTTS(popen=lambda *args, **kwargs: called.append(args)).speak("  ")
    assert called == []


def test_tts_uses_argument_list_and_devnull():
    calls = []
    process = FakeProcess()

    def popen(args, **kwargs):
        calls.append((args, kwargs))
        return process

    tts = SayTTS(say_path="fake-say", popen=popen)
    assert tts.speak("Ahoj", wait=True)
    assert calls[0][0] == ["fake-say", "-r", "190", "Ahoj"]
    assert calls[0][1]["stdin"] is subprocess.DEVNULL


def test_tts_stop_terminates_process():
    process = FakeProcess(wait_blocks=True)
    tts = SayTTS(popen=lambda *_args, **_kwargs: process)
    tts.speak("Ahoj")
    assert tts.stop()
    assert process.terminated


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
