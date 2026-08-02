from __future__ import annotations

import socket
from urllib.parse import quote

import pytest
from conftest import FakeResponse

from mike.errors import FeatureDisabledError, PolicyError
from mike.research import ResearchClient, extract_query
from mike.security import is_loopback_host, validate_public_https_url


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "localhost", "LOCALHOST."])
def test_loopback_hosts(host):
    assert is_loopback_host(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.0.1", "example.com", "testclient"])
def test_non_loopback_hosts(host):
    assert not is_loopback_host(host)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "ftp://example.com/file",
        "https://user:secret@invalid",
        "https://localhost/a",
        "https://service.local/a",
        "https://127.0.0.1/a",
        "https://10.0.0.1/a",
        "https://169.254.1.1/a",
        "https://[::1]/a",
    ],
)
def test_research_url_rejects_unsafe_targets(url):
    with pytest.raises(PolicyError):
        validate_public_https_url(url)


def test_research_url_accepts_public_dns(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
    )
    assert validate_public_https_url("https://example.com/article") == "https://example.com/article"


def test_research_url_rejects_dns_to_private_ip(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.4", 443))],
    )
    with pytest.raises(PolicyError):
        validate_public_https_url("https://example.com/article")


def test_research_url_rejects_unresolvable_domain(monkeypatch):
    def fail(*_args, **_kwargs):
        raise socket.gaierror("nope")

    monkeypatch.setattr(socket, "getaddrinfo", fail)
    with pytest.raises(PolicyError, match="přeložit"):
        validate_public_https_url("https://example.invalid/article")


@pytest.mark.parametrize(
    ("text", "query"),
    [
        ("Majku, vyhledej na internetu cenu zlata", "cenu zlata"),
        ("ověř na webu nové vydání", "nové vydání"),
        ("udělej research online bezpečnost", "bezpečnost"),
        ("najdi online dokumentaci", "dokumentaci"),
        ("řekni mi cenu zlata", None),
    ],
)
def test_extract_research_query(text, query):
    assert extract_query(text) == query


def test_research_disabled_by_default():
    with pytest.raises(FeatureDisabledError):
        ResearchClient(enabled=False).search("dotaz")


def test_research_searches_and_fetches_public_sources(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
    )
    result_url = "https://example.com/article"
    html = (
        "<html><a class='result__a' href='https://duckduckgo.com/l/?uddg="
        + quote(result_url, safe="")
        + "'>Veřejný zdroj</a></html>"
    )
    responses = iter([FakeResponse(html), FakeResponse("<article>Ověřený obsah zdroje.</article>")])
    client = ResearchClient(enabled=True, opener=lambda *_args, **_kwargs: next(responses))
    result = client.search("test")
    assert result.sources[0].url == result_url
    assert "Ověřený obsah" in result.sources[0].excerpt


def test_research_skips_non_html_page(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
    )
    html = "<a class='result__a' href='https://example.com/file'>Soubor</a>"
    responses = iter([FakeResponse(html), FakeResponse("binary", content_type="application/octet-stream")])
    client = ResearchClient(enabled=True, opener=lambda *_args, **_kwargs: next(responses))
    result = client.search("test")
    assert result.sources[0].excerpt == ""
