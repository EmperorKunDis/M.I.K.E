"""Bezpečné hodnocení a návrhy promptu bez automatických změn kódu."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .database import Database, now_iso
from .ollama import OllamaClient, OllamaError
from .paths import secure_file


@dataclass(frozen=True)
class Score:
    relevance: int
    clarity: int
    grounded: int
    note: str = ""


class Judge:
    SYSTEM = (
        "Jsi přísný hodnotitel českého hlasového asistenta. Posuď jen relevanci, "
        "srozumitelnost a oporu ve vstupu. Vrať pouze JSON s celými čísly 0 až 5 "
        "v klíčích relevance, clarity, grounded a krátkým note."
    )

    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    def score(self, user_text: str, reply: str) -> Score | None:
        try:
            raw = self.client.chat(
                [
                    {"role": "system", "content": self.SYSTEM},
                    {"role": "user", "content": f"Vstup:\n{user_text}\n\nOdpověď:\n{reply}"},
                ],
                json_mode=True,
                temperature=0.0,
                max_tokens=140,
            )
            payload = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
            return Score(
                relevance=max(0, min(int(payload["relevance"]), 5)),
                clarity=max(0, min(int(payload["clarity"]), 5)),
                grounded=max(0, min(int(payload["grounded"]), 5)),
                note=str(payload.get("note", ""))[:500],
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OllamaError):
            return None


class SafeTuner:
    """Vytvoří pouze auditovatelný kandidát; nikdy jej sám neaktivuje."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def propose_if_needed(self, minimum_samples: int = 10) -> int | None:
        summary = self.database.evaluation_summary(50)
        count = int(summary.get("count") or 0)
        average = summary.get("average")
        if count < minimum_samples or average is None or float(average) >= 4.0:
            return None
        rationale = f"Posledních {count} hodnocení má průměr {float(average):.2f}/5."
        addendum = (
            "Začni přímou odpovědí, odděl ověřené skutečnosti od nejistoty a "
            "nepřidávej kroky, o které Uživatel nežádal."
        )
        candidate_id = self.database.propose_prompt(rationale, addendum)
        payload = {
            "id": candidate_id,
            "created_at": now_iso(),
            "status": "proposed",
            "rationale": rationale,
            "addendum": addendum,
            "applied": False,
        }
        path = self.database.path.parent / "prompt-candidate.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        secure_file(path)
        return candidate_id
