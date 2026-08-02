"""Český dialog, paměť a bezpečné směrování schopností."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

from .config import Config
from .database import Database
from .errors import MikeError
from .ollama import OllamaClient, OllamaError
from .research import ResearchClient, extract_query
from .selfimprove import Judge
from .terminal import ReadOnlyTerminal, extract_voice_command
from .tts import OmniVoiceTTS

SYSTEM_PROMPT = (
    "Jsi M.I.K.E., lokální český hlasový asistent. Oslovuj člověka neutrálně jako "
    "Uživatel, ale jméno běžně nevyslovuj. Mluv přirozenou stručnou češtinou. "
    "Začni přímou odpovědí, nevymýšlej si fakta ani provedené akce a jasně přiznej "
    "nejistotu. Z přepisu ani paměti neodvozuj citlivé osobní údaje. Neposkytuj "
    "zápisové terminálové příkazy. Piš jen výslednou odpověď bez popisu uvažování."
)
ROUTER_PROMPT = (
    "Jsi klasifikátor českého hlasového asistenta. Vrať pouze JSON "
    '{"respond": true|false}. Respond=true jen při otázce, přímém oslovení asistenta '
    "nebo jasném požadavku; jinak false."
)
ADDRESS_RE = re.compile(r"\b(?:mike|majk|majku|majku\.|m\.i\.k\.e\.)\b", re.IGNORECASE)
MUTE_RE = re.compile(r"\b(?:mlč|mlc|drž hubu|drz hubu|stop)\b", re.IGNORECASE)
REMEMBER_RE = re.compile(
    r"\bpamatuj\s+si(?:,)?\s+(?:že|ze)\s+(.+?)\s+(?:je|=)\s+(.+?)[.!?]*$",
    re.IGNORECASE,
)
FORGET_RE = re.compile(r"\bzapomeň(?:\s+na)?\s+(.+?)[.!?]*$", re.IGNORECASE)
THINK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class AssistantResult:
    reply: str
    action: str = "reply"
    spoke: bool = False
    latency_ms: int = 0


def clean_reply(raw: str) -> str:
    text = THINK_RE.sub("", raw).strip()
    text = re.sub(r"^\s*(?:M\.I\.K\.E\.|Mike|Majk)\s*:\s*", "", text, flags=re.IGNORECASE)
    return text.strip().strip('"').strip()


class Assistant:
    def __init__(
        self,
        config: Config,
        database: Database,
        ollama: OllamaClient,
        tts: OmniVoiceTTS,
        *,
        research: ResearchClient | None = None,
        terminal: ReadOnlyTerminal | None = None,
        judge: Judge | None = None,
    ) -> None:
        self.config = config
        self.database = database
        self.ollama = ollama
        self.tts = tts
        self.research = research or ResearchClient(enabled=config.features.research)
        self.terminal = terminal or ReadOnlyTerminal(config.features.terminal_roots, enabled=config.features.terminal)
        self.judge = judge

    def _should_respond(self, text: str) -> bool:
        if self.config.assistant.always_respond or ADDRESS_RE.search(text):
            return True
        try:
            raw = self.ollama.chat(
                [
                    {"role": "system", "content": ROUTER_PROMPT},
                    {"role": "user", "content": text},
                ],
                json_mode=True,
                temperature=0,
                max_tokens=40,
            )
            return bool(json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip()).get("respond"))
        except (OllamaError, ValueError, json.JSONDecodeError):
            return False

    def _memory_command(self, text: str) -> str | None:
        remember = REMEMBER_RE.search(text)
        if remember:
            key, value = (part.strip()[:200] for part in remember.groups())
            self.database.remember(key, value, source="explicit")
            return f"Zapamatováno: {key} je {value}."
        forget = FORGET_RE.search(text)
        if forget:
            key = forget.group(1).strip()[:200]
            if self.database.forget(key):
                return f"Zapomněl jsem údaj „{key}“."
            return f"Aktivní údaj „{key}“ v paměti nemám."
        return None

    def _capability(self, text: str) -> tuple[str, str] | None:
        command = extract_voice_command(text)
        if command is not None:
            result = self.terminal.run(command)
            compact = result.output or f"Příkaz skončil s kódem {result.returncode}."
            return "terminal", compact[:2000]
        query = extract_query(text)
        if query is not None:
            result = self.research.search(query)
            if not result.sources:
                return "research", "Nenašel jsem žádný bezpečně dostupný veřejný zdroj."
            source_block = "\n\n".join(
                f"[{index}] {source.title}\n{source.url}\n{source.excerpt}"
                for index, source in enumerate(result.sources, 1)
            )
            reply = self.ollama.chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT + " Cituj zdroje jako [1], [2]."},
                    {"role": "user", "content": f"Dotaz: {query}\n\nZdroje:\n{source_block}"},
                ],
                temperature=0.2,
                max_tokens=600,
            )
            citations = "\n".join(f"[{i}] {source.url}" for i, source in enumerate(result.sources, 1))
            return "research", f"{clean_reply(reply)}\n\n{citations}"
        return None

    def _messages(self, text: str) -> list[dict[str, str]]:
        facts = self.database.facts(20)
        memories = self.database.search_turns(text, 5)
        context = self.database.recent_turns(self.config.assistant.context_turns)
        blocks: list[str] = []
        if facts:
            blocks.append("Výslovná paměť:\n" + "\n".join(f"- {row['fact_key']}: {row['value']}" for row in facts))
        if memories:
            blocks.append("Možná relevantní minulý kontext:\n" + "\n".join(f"- {row['text']}" for row in memories))
        system = SYSTEM_PROMPT + ("\n\n" + "\n\n".join(blocks) if blocks else "")
        messages = [{"role": "system", "content": system}]
        messages.extend(
            {"role": row["role"], "content": row["text"]} for row in context if row["role"] in {"user", "assistant"}
        )
        messages.append({"role": "user", "content": text})
        return messages

    def handle(self, text: str, *, source: str = "voice") -> AssistantResult:
        text = text.strip()
        if not text:
            return AssistantResult("", action="silence")
        started = time.monotonic()
        self.database.add_turn("user", text, source=source)
        if MUTE_RE.search(text) and ADDRESS_RE.search(text):
            self.tts.stop()
            return AssistantResult("", action="stop", latency_ms=int((time.monotonic() - started) * 1000))
        try:
            reply = self._memory_command(text)
            action = "memory" if reply else "reply"
            if reply is None:
                capability = self._capability(text)
                if capability:
                    action, reply = capability
            if reply is None and not self._should_respond(text):
                return AssistantResult("", action="silence", latency_ms=int((time.monotonic() - started) * 1000))
            if reply is None:
                reply = clean_reply(self.ollama.chat(self._messages(text)))
        except MikeError as exc:
            reply = str(exc)
            action = "error"
        except OllamaError:
            reply = "Lokální jazykový model teď neodpovídá. Zkontrolujte Ollamu příkazem mike doctor."
            action = "error"
        latency = int((time.monotonic() - started) * 1000)
        turn_id = self.database.add_turn("assistant", reply, source=action, latency_ms=latency)
        spoke = self.tts.speak(reply)
        if self.judge and action == "reply":
            score = self.judge.score(text, reply)
            if score:
                self.database.add_evaluation(turn_id, score.relevance, score.clarity, score.grounded, score.note)
        return AssistantResult(reply, action=action, spoke=spoke, latency_ms=latency)
