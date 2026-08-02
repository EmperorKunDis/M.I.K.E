---
status: implemented
agent_use: always
area: security
verified_against_commit: "initial-public-snapshot"
last_verified: "2026-08-02"
related_spec: "docs/specs/public-v0.1.md"
related_plan: "docs/plans/public-v0.1.md"
---

# Aktuální rizika

| Priorita | Riziko | Stav / mitigace |
|---|---|---|
| P1 | Přepis a LLM mohou halucinovat | Alpha warning, žádné high-risk použití, lokální historie a feedback |
| P1 | Voiceprint není autentizace | Opt-in, lokální, žádné privilegované operace |
| P1 | Research může načíst škodlivý web | Opt-in, HTTPS, privátní IP blokace, limit odpovědi; DNS rebinding zůstává známé riziko |
| P2 | TCC oprávnění se mezi verzemi macOS liší | `mike doctor`, dokumentovaný první start, bez admin práv |
| P2 | Modelové licence a supply chain | Žádné bundlování, samostatné stažení, Dependabot/pip-audit/Gitleaks |
| P1 | Výchozí OmniVoice model je CC-BY-NC | Výslovné nekomerční upozornění, samostatné stažení, žádné váhy v MIT repozitáři |
| P1 | Hlasová syntéza může být zneužita k napodobování | Veřejný server má jen voice design, nepřijímá referenční audio, dokumentovaný zákaz zneužití |
| P2 | Alpha launchd nemá podepsaný `.app` bundle | Zdrojová instalace; podepsaná/notarizovaná aplikace je mimo v0.1 |
| P3 | AppKit overlay závisí na PyObjC | Volitelný; dashboard/runtime pokračuje bez něj |
