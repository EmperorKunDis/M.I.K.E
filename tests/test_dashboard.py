from __future__ import annotations

import pytest
from conftest import FakeOllama
from fastapi import HTTPException
from starlette.testclient import TestClient

from mike.assistant import Assistant
from mike.dashboard import _local_request, create_app
from mike.database import Database


def make_client(config, app_paths, fake_tts):
    database = Database(app_paths.database)
    database.initialize()
    assistant = Assistant(config, database, FakeOllama(["Odpověď z dashboardu."]), fake_tts)
    app = create_app(config, database, assistant)
    return TestClient(app), database


def test_health_is_local_and_private(config, app_paths, fake_tts):
    client, _database = make_client(config, app_paths, fake_tts)
    payload = client.get("/api/health").json()
    assert payload["ok"]
    assert payload["host"] == "127.0.0.1"
    assert payload["privacy"]["telemetry"] is False


def test_remote_client_is_rejected(config, app_paths, fake_tts):
    request = type("Request", (), {"client": type("Client", (), {"host": "203.0.113.5"})()})()
    with pytest.raises(HTTPException) as caught:
        _local_request(request)
    assert caught.value.status_code == 403


def test_dashboard_html_has_csp(config, app_paths, fake_tts):
    client, _database = make_client(config, app_paths, fake_tts)
    text = client.get("/").text
    assert "Content-Security-Policy" in text
    assert "127.0.0.1" in text


def test_dashboard_escapes_transcript(config, app_paths, fake_tts):
    client, database = make_client(config, app_paths, fake_tts)
    database.add_turn("user", "<script>alert(1)</script>")
    text = client.get("/").text
    assert "&lt;script&gt;" in text
    assert "<script>alert(1)</script>" not in text


def test_dashboard_ask(config, app_paths, fake_tts):
    client, database = make_client(config, app_paths, fake_tts)
    response = client.post("/api/ask", json={"text": "Majku, odpověz."})
    assert response.status_code == 200
    assert response.json()["reply"] == "Odpověď z dashboardu."
    assert len(database.recent_turns()) == 2


def test_dashboard_rejects_empty_ask(config, app_paths, fake_tts):
    client, _database = make_client(config, app_paths, fake_tts)
    assert client.post("/api/ask", json={"text": ""}).status_code == 422


def test_dashboard_feedback(config, app_paths, fake_tts):
    client, database = make_client(config, app_paths, fake_tts)
    turn = database.add_turn("assistant", "odpověď")
    response = client.post(
        "/api/feedback",
        json={"turn_id": turn, "relevance": 5, "clarity": 4, "grounded": 3, "note": "ok"},
    )
    assert response.json() == {"ok": True}
    assert database.evaluation_summary()["count"] == 1


def test_openapi_is_disabled(config, app_paths, fake_tts):
    client, _database = make_client(config, app_paths, fake_tts)
    assert client.get("/openapi.json").status_code == 404
