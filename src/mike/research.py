"""Explicitně zapínaný internetový research s ochranou proti SSRF."""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any

from .errors import FeatureDisabledError, MikeError, PolicyError
from .security import validate_public_https_url

RESEARCH_MARKER = re.compile(
    r"\b(?:vyhledej|ověř|over|research|najdi)\s+(?:na\s+internetu|na\s+webu|online)\s+(.+)$",
    re.IGNORECASE,
)
SEARCH_URL = "https://html.duckduckgo.com/html/"


@dataclass(frozen=True)
class ResearchSource:
    title: str
    url: str
    excerpt: str


@dataclass(frozen=True)
class ResearchResult:
    query: str
    sources: tuple[ResearchSource, ...]


def extract_query(text: str) -> str | None:
    match = RESEARCH_MARKER.search(text.strip())
    return match.group(1).strip(" .?") if match else None


class _ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if "result__a" in classes:
            self._href = attributes.get("href") or ""
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            self.links.append((" ".join(self._text).strip(), self._href))
            self._href = ""
            self._text = []


def _unwrap_result_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.endswith("duckduckgo.com"):
        target = urllib.parse.parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return urllib.parse.unquote(target)
    return url


class ResearchClient:
    def __init__(self, *, enabled: bool, opener: Any | None = None, timeout: float = 12.0) -> None:
        self.enabled = enabled
        self._open = opener or urllib.request.urlopen
        self.timeout = timeout

    def _fetch(self, request: urllib.request.Request) -> str:
        try:
            with self._open(request, timeout=self.timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type not in {"text/html", "text/plain"}:
                    return ""
                return response.read(300_000).decode("utf-8", errors="replace")
        except OSError as exc:
            raise MikeError(f"Research požadavek selhal: {exc}") from exc

    def search(self, query: str, limit: int = 3) -> ResearchResult:
        if not self.enabled:
            raise FeatureDisabledError("Internetový research je vypnutý v config.toml.")
        query = query.strip()[:300]
        if not query:
            raise MikeError("Research dotaz je prázdný.")
        body = urllib.parse.urlencode({"q": query}).encode("utf-8")
        request = urllib.request.Request(
            SEARCH_URL,
            data=body,
            headers={"User-Agent": "MIKE/0.1 (+https://github.com/EmperorKunDis/M.I.K.E)"},
        )
        parser = _ResultParser()
        parser.feed(self._fetch(request))
        sources: list[ResearchSource] = []
        for title, raw_url in parser.links:
            url = _unwrap_result_url(raw_url)
            try:
                validate_public_https_url(url)
            except PolicyError:
                continue
            page_request = urllib.request.Request(  # noqa: S310 - URL passed public-HTTPS validation
                url, headers={"User-Agent": "MIKE/0.1"}
            )
            page = self._fetch(page_request)
            plain = re.sub(r"<[^>]+>", " ", page)
            plain = re.sub(r"\s+", " ", html.unescape(plain)).strip()
            sources.append(ResearchSource(title=title[:200], url=url, excerpt=plain[:1200]))
            if len(sources) >= max(1, min(limit, 5)):
                break
        return ResearchResult(query=query, sources=tuple(sources))
