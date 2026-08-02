from __future__ import annotations

import json

import pytest

from mike.database import Database
from mike.paths import permission_bits


@pytest.fixture
def database(app_paths):
    db = Database(app_paths.database)
    db.initialize()
    return db


def test_database_is_private(database):
    assert permission_bits(database.path) == 0o600
    assert permission_bits(database.path.parent) == 0o700


def test_add_and_read_turns_in_order(database):
    database.add_turn("user", "první")
    database.add_turn("assistant", "druhá")
    assert [row["text"] for row in database.recent_turns()] == ["první", "druhá"]


def test_recent_turns_is_bounded(database):
    for index in range(120):
        database.add_turn("user", str(index))
    assert len(database.recent_turns(1000)) == 100


def test_search_turns_uses_fts(database):
    database.add_turn("user", "Hledáme modrou velrybu v oceánu")
    database.add_turn("user", "Jiná věta")
    hits = database.search_turns("modrou velrybu")
    assert hits[0]["text"].startswith("Hledáme")


def test_short_search_is_ignored(database):
    assert database.search_turns("a k") == []


def test_explicit_fact_is_stored(database):
    database.remember("oblíbená barva", "zelená")
    assert database.facts()[0]["value"] == "zelená"


def test_explicit_fact_can_be_corrected(database):
    database.remember("barva", "zelená")
    database.remember("barva", "modrá")
    assert database.facts()[0]["value"] == "modrá"


def test_automatic_fact_cannot_overwrite_explicit(database):
    database.remember("barva", "modrá", source="explicit")
    database.remember("barva", "červená", source="automatic")
    assert database.facts()[0]["value"] == "modrá"
    assert database.facts()[0]["source"] == "explicit"


def test_explicit_fact_overwrites_automatic(database):
    database.remember("barva", "červená", source="automatic")
    database.remember("barva", "modrá", source="explicit")
    assert database.facts()[0]["value"] == "modrá"


def test_forget_deactivates_fact(database):
    database.remember("barva", "modrá")
    assert database.forget("barva")
    assert database.facts() == []


def test_forget_unknown_fact_returns_false(database):
    assert not database.forget("není")


def test_evaluation_summary(database):
    turn = database.add_turn("assistant", "odpověď")
    database.add_evaluation(turn, 5, 4, 3, "dobré")
    summary = database.evaluation_summary()
    assert summary["count"] == 1
    assert summary["average"] == 4


def test_evaluation_scores_are_clamped(database):
    turn = database.add_turn("assistant", "odpověď")
    database.add_evaluation(turn, 50, -2, 4)
    assert database.evaluation_summary()["average"] == 3


def test_prompt_candidate_stays_proposed(database):
    candidate = database.propose_prompt("důvod", "dodatek")
    with database.connect(readonly=True) as connection:
        row = connection.execute("SELECT * FROM prompt_candidates WHERE id=?", (candidate,)).fetchone()
    assert row["status"] == "proposed"


def test_redacted_status_contains_no_transcript(database):
    database.add_turn("user", "citlivý text")
    payload = json.loads(database.export_redacted_status())
    assert "citlivý text" not in json.dumps(payload)
    assert payload["turns"] == 1
