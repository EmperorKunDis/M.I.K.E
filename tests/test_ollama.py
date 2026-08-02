from __future__ import annotations

import json
import urllib.error

import pytest
from conftest import FakeResponse

from mike.ollama import OllamaClient, OllamaError


def test_health_lists_installed_model():
    client = OllamaClient(
        "http://127.0.0.1:11434",
        "gemma3:12b",
        opener=lambda *_args, **_kwargs: FakeResponse(
            {"models": [{"name": "gemma3:12b"}]}, content_type="application/json"
        ),
    )
    health = client.health()
    assert health["model_installed"]


def test_health_detects_missing_model():
    client = OllamaClient(
        "http://127.0.0.1:11434",
        "missing:latest",
        opener=lambda *_args, **_kwargs: FakeResponse(
            {"models": [{"name": "other:latest"}]}, content_type="application/json"
        ),
    )
    assert not client.health()["model_installed"]


def test_chat_sends_local_non_streaming_request():
    requests = []

    def opener(request, **_kwargs):
        requests.append(request)
        return FakeResponse({"message": {"content": "Ahoj"}}, content_type="application/json")

    client = OllamaClient("http://127.0.0.1:11434", "test", opener=opener)
    assert client.chat([{"role": "user", "content": "Ahoj"}]) == "Ahoj"
    payload = json.loads(requests[0].data)
    assert payload["stream"] is False
    assert payload["think"] is False
    assert requests[0].full_url == "http://127.0.0.1:11434/api/chat"


def test_chat_json_mode_requests_json():
    requests = []

    def opener(request, **_kwargs):
        requests.append(request)
        return FakeResponse({"message": {"content": "{}"}}, content_type="application/json")

    OllamaClient("http://localhost:11434", "test", opener=opener).chat([], json_mode=True)
    assert json.loads(requests[0].data)["format"] == "json"


def test_chat_retries_without_think_on_http_error():
    requests = []

    def opener(request, **_kwargs):
        requests.append(request)
        if len(requests) == 1:
            raise urllib.error.HTTPError(request.full_url, 400, "bad", {}, None)
        return FakeResponse({"message": {"content": "funguje"}}, content_type="application/json")

    client = OllamaClient("http://127.0.0.1:11434", "test", opener=opener)
    assert client.chat([]) == "funguje"
    assert "think" not in json.loads(requests[1].data)


@pytest.mark.parametrize("payload", [{}, {"message": {}}, {"message": {"content": ""}}])
def test_empty_model_reply_is_error(payload):
    client = OllamaClient(
        "http://127.0.0.1:11434",
        "test",
        opener=lambda *_args, **_kwargs: FakeResponse(payload, content_type="application/json"),
    )
    with pytest.raises(OllamaError, match="prázdnou"):
        client.chat([])


def test_network_failure_is_redacted_as_local_error():
    def opener(*_args, **_kwargs):
        raise OSError("connection refused")

    client = OllamaClient("http://127.0.0.1:11434", "test", opener=opener)
    with pytest.raises(OllamaError, match="Lokální Ollama"):
        client.health()
