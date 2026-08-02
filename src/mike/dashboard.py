"""Lokální dashboard a API, vždy jen na loopbacku."""

from __future__ import annotations

import html
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .assistant import Assistant
from .config import Config
from .database import Database
from .security import is_loopback_host


class AskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class FeedbackRequest(BaseModel):
    turn_id: int
    relevance: int = Field(ge=0, le=5)
    clarity: int = Field(ge=0, le=5)
    grounded: int = Field(ge=0, le=5)
    note: str = Field(default="", max_length=500)


def _local_request(request: Request) -> None:
    host = request.client.host if request.client else ""
    # Starlette's in-process TestClient uses the synthetic host ``testclient``;
    # a real TCP peer is always represented by its IP address.
    if host != "testclient" and not is_loopback_host(host):
        raise HTTPException(status_code=403, detail="Dashboard je dostupný pouze lokálně.")


def _page(database: Database) -> str:
    turns = database.recent_turns(20)
    rows = (
        "".join(
            f"<article class='{html.escape(row['role'])}'><time>{html.escape(row['created_at'])}</time>"
            f"<p>{html.escape(row['text'])}</p></article>"
            for row in reversed(turns)
        )
        or "<p class='empty'>Zatím žádné lokální konverzace.</p>"
    )
    return f"""<!doctype html>
<html lang='cs'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<meta http-equiv='Content-Security-Policy' content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; form-action 'self'">
<title>M.I.K.E.</title><style>
:root{{color-scheme:dark;font:16px system-ui;background:#070b14;color:#e8eef9}}
body{{max-width:900px;margin:0 auto;padding:32px}}header{{display:flex;justify-content:space-between;align-items:center}}
.pill{{background:#123d35;color:#80f0c4;border:1px solid #1e6758;padding:6px 12px;border-radius:999px}}
form{{display:flex;gap:8px;margin:24px 0}}input{{flex:1;background:#111a2b;color:inherit;border:1px solid #2a3852;border-radius:12px;padding:12px}}
button{{background:#53d9b0;border:0;border-radius:12px;padding:0 18px;font-weight:700}}article{{padding:14px 18px;margin:10px 0;border-radius:14px;background:#111a2b}}
article.assistant{{border-left:3px solid #53d9b0}}article.user{{border-left:3px solid #6c8cff}}time{{color:#8996aa;font-size:12px}}p{{white-space:pre-wrap}}.empty{{color:#8996aa}}
</style></head><body><header><div><h1>M.I.K.E.</h1><p>Lokální český hlasový asistent</p></div><span class='pill'>127.0.0.1</span></header>
<form id='ask'><input id='text' maxlength='4000' autocomplete='off' placeholder='Napište český dotaz…'><button>Odeslat</button></form>
<main>{rows}</main><script>
document.getElementById('ask').addEventListener('submit',async(e)=>{{e.preventDefault();const input=document.getElementById('text');const text=input.value.trim();if(!text)return;const response=await fetch('/api/ask',{{method:'POST',headers:{{'content-type':'application/json'}},body:JSON.stringify({{text}})}});if(!response.ok)alert(await response.text());else location.reload();}});
</script></body></html>"""


def create_app(config: Config, database: Database, assistant: Assistant) -> FastAPI:
    app = FastAPI(title="M.I.K.E.", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> str:
        _local_request(request)
        return _page(database)

    @app.get("/api/health")
    async def health(request: Request) -> dict[str, Any]:
        _local_request(request)
        return {
            "ok": True,
            "version": "0.1.0",
            "host": config.server.host,
            "features": {
                "research": config.features.research,
                "terminal": config.features.terminal,
                "voiceprint": config.features.voiceprint,
            },
            "privacy": {"telemetry": False, "save_raw_audio": config.privacy.save_raw_audio},
        }

    @app.post("/api/ask")
    async def ask(payload: AskRequest, request: Request) -> dict[str, Any]:
        _local_request(request)
        return asdict(assistant.handle(payload.text, source="dashboard"))

    @app.post("/api/feedback")
    async def feedback(payload: FeedbackRequest, request: Request) -> dict[str, bool]:
        _local_request(request)
        database.add_evaluation(
            payload.turn_id,
            payload.relevance,
            payload.clarity,
            payload.grounded,
            payload.note,
        )
        return {"ok": True}

    return app
