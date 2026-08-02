from __future__ import annotations

import json
from dataclasses import replace

import pytest
from conftest import FakeOllama

from mike.database import Database
from mike.paths import permission_bits
from mike.runtime import MikeRuntime
from mike.selfimprove import Judge, SafeTuner


@pytest.fixture
def database(app_paths):
    value = Database(app_paths.database)
    value.initialize()
    return value


def test_judge_parses_bounded_scores():
    judge = Judge(FakeOllama(['{"relevance": 8, "clarity": -1, "grounded": 4, "note": "x"}']))
    score = judge.score("dotaz", "odpověď")
    assert (score.relevance, score.clarity, score.grounded) == (5, 0, 4)


@pytest.mark.parametrize("reply", ["není json", "{}", '{"relevance": "x"}'])
def test_judge_invalid_payload_is_nonfatal(reply):
    assert Judge(FakeOllama([reply])).score("dotaz", "odpověď") is None


def add_evaluations(database, count: int, score: int) -> None:
    for index in range(count):
        turn = database.add_turn("assistant", f"odpověď {index}")
        database.add_evaluation(turn, score, score, score)


def test_tuner_waits_for_minimum_samples(database):
    add_evaluations(database, 9, 1)
    assert SafeTuner(database).propose_if_needed() is None


def test_tuner_does_nothing_when_scores_are_good(database):
    add_evaluations(database, 10, 5)
    assert SafeTuner(database).propose_if_needed() is None


def test_tuner_writes_unapplied_private_candidate(database):
    add_evaluations(database, 10, 2)
    candidate = SafeTuner(database).propose_if_needed()
    path = database.path.parent / "prompt-candidate.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert candidate == payload["id"]
    assert payload["status"] == "proposed"
    assert payload["applied"] is False
    assert permission_bits(path) == 0o600


def test_runtime_initializes_private_database(config):
    runtime = MikeRuntime(config)
    assert runtime.database.path.exists()
    assert permission_bits(runtime.database.path) == 0o600


def test_runtime_raw_audio_file_is_private(config):
    configured = replace(config, privacy=replace(config.privacy, save_raw_audio=True))
    runtime = MikeRuntime(configured)
    path = runtime._save_audio(b"\0\0" * 100)
    assert path.suffix == ".wav"
    assert permission_bits(path) == 0o600
