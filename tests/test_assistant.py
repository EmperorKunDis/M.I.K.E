from __future__ import annotations

from dataclasses import replace

import pytest
from conftest import FakeOllama

from mike.assistant import Assistant, clean_reply
from mike.config import FeatureConfig
from mike.database import Database
from mike.research import ResearchResult, ResearchSource
from mike.terminal import TerminalResult


@pytest.fixture
def database(app_paths):
    value = Database(app_paths.database)
    value.initialize()
    return value


def make_assistant(config, database, ollama, tts, **kwargs):
    return Assistant(config, database, ollama, tts, **kwargs)


@pytest.mark.parametrize(
    ("raw", "cleaned"),
    [
        ("<think>tajné</think> Výsledek.", "Výsledek."),
        ('Mike: "Výsledek."', "Výsledek."),
        ("M.I.K.E.: Hotovo.", "Hotovo."),
        ("  Přímá odpověď.  ", "Přímá odpověď."),
    ],
)
def test_clean_reply(raw, cleaned):
    assert clean_reply(raw) == cleaned


def test_direct_address_always_generates(config, database, fake_tts):
    ollama = FakeOllama(["Přímá odpověď."])
    result = make_assistant(config, database, ollama, fake_tts).handle("Majku, jak se máš?")
    assert result.reply == "Přímá odpověď."
    assert fake_tts.spoken == ["Přímá odpověď."]


def test_non_request_can_stay_silent(config, database, fake_tts):
    ollama = FakeOllama(['{"respond": false}'])
    result = make_assistant(config, database, ollama, fake_tts).handle("Dnes prší.")
    assert result.action == "silence"
    assert fake_tts.spoken == []


def test_router_can_choose_response(config, database, fake_tts):
    ollama = FakeOllama(['{"respond": true}', "Vezmi si deštník."])
    result = make_assistant(config, database, ollama, fake_tts).handle("Co s tím deštěm?")
    assert result.reply == "Vezmi si deštník."


def test_always_respond_skips_router(config, database, fake_tts):
    configured = replace(config, assistant=replace(config.assistant, always_respond=True))
    ollama = FakeOllama(["Odpověď."])
    make_assistant(configured, database, ollama, fake_tts).handle("Konstatování.")
    assert len(ollama.calls) == 1


def test_memory_command_persists(config, database, fake_ollama, fake_tts):
    result = make_assistant(config, database, fake_ollama, fake_tts).handle(
        "Majku, pamatuj si, že oblíbená barva je modrá."
    )
    assert result.action == "memory"
    assert database.facts()[0]["value"] == "modrá"


def test_forget_command_deactivates(config, database, fake_ollama, fake_tts):
    database.remember("oblíbená barva", "modrá")
    result = make_assistant(config, database, fake_ollama, fake_tts).handle("Majku, zapomeň na oblíbená barva.")
    assert result.action == "memory"
    assert database.facts() == []


def test_mute_is_one_shot(config, database, fake_ollama, fake_tts):
    result = make_assistant(config, database, fake_ollama, fake_tts).handle("Majku, drž hubu.")
    assert result.action == "stop"
    assert fake_tts.stopped == 1
    assert result.reply == ""


def test_terminal_disabled_returns_explanation(config, database, fake_ollama, fake_tts):
    result = make_assistant(config, database, fake_ollama, fake_tts).handle("Majku, v terminálu spusť git status")
    assert result.action == "error"
    assert "vypnutý" in result.reply


class FakeTerminal:
    def run(self, command):
        return TerminalResult(tuple(command.split()), 0, "working tree clean")


def test_terminal_output_is_returned(config, database, fake_ollama, fake_tts):
    result = make_assistant(config, database, fake_ollama, fake_tts, terminal=FakeTerminal()).handle(
        "Majku, v terminálu spusť git status"
    )
    assert result.action == "terminal"
    assert result.reply == "working tree clean"


class FakeResearch:
    def search(self, query):
        return ResearchResult(query, (ResearchSource("Zdroj", "https://example.com", "Obsah"),))


def test_research_cites_source(config, database, fake_tts):
    ollama = FakeOllama(["Shrnutí [1]."])
    assistant = make_assistant(config, database, ollama, fake_tts, research=FakeResearch())
    result = assistant.handle("Majku, ověř na internetu veřejnou informaci")
    assert result.action == "research"
    assert "https://example.com" in result.reply


def test_generated_prompt_uses_generic_user(config, database, fake_tts):
    ollama = FakeOllama(["Odpověď."])
    make_assistant(config, database, ollama, fake_tts).handle("Majku, odpověz.")
    system = ollama.calls[0][0][0]["content"]
    assert "Uživatel" in system


def test_turns_are_persisted(config, database, fake_tts):
    assistant = make_assistant(config, database, FakeOllama(["Ano."]), fake_tts)
    assistant.handle("Majku, platí to?")
    assert [row["role"] for row in database.recent_turns()] == ["user", "assistant"]


def test_empty_input_is_silent(config, database, fake_ollama, fake_tts):
    result = make_assistant(config, database, fake_ollama, fake_tts).handle("   ")
    assert result.action == "silence"
    assert database.recent_turns() == []


def test_feature_flags_default_to_disabled(config):
    assert isinstance(config.features, FeatureConfig)
    assert not config.features.research
    assert not config.features.terminal
