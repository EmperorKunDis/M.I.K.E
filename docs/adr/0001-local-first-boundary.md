---
status: accepted
agent_use: task-scoped
area: security
verified_against_commit: "initial-public-snapshot"
last_verified: "2026-08-02"
related_spec: "docs/specs/public-v0.1.md"
related_plan: "docs/plans/public-v0.1.md"
---

# ADR 0001: Local-first boundary

## Rozhodnutí

Dashboard a Ollama jsou pouze loopback. Telemetrie a audio jsou vypnuté.
Internetový research, terminál a hlasový otisk vyžadují explicitní opt-in.
Terminál je jen read-only, bez shellu. Tuner vytváří pouze neaktivní kandidát.

## Důsledky

Vzdálený model, LAN dashboard a hlasové zápisové akce nejsou v0.1 dostupné.
Bezpečný default má přednost před pohodlím. Změna tohoto ADR vyžaduje threat
model, test migrace, aktualizaci privacy dokumentace a lidské schválení.
