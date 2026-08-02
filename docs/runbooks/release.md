---
status: implemented
agent_use: task-scoped
area: release
verified_against_commit: "initial-public-snapshot"
last_verified: "2026-08-02"
related_spec: "docs/specs/public-v0.1.md"
related_plan: "docs/plans/public-v0.1.md"
---

# Runbook: source release

1. Čisté venv, `./scripts/verify.sh`, lokální Gitleaks nad soubory i historií.
2. Ověřit jediný očekávaný commit, veřejný remote a vzdálený SHA.
3. Vyžadovat zelené `test` a `gitleaks`, secret scanning a ochranu `main`.
4. Tag `v0.1.0` a GitHub Release pouze z automatického source archivu.
5. Nepřikládat binárky, modely, média a nic nepublikovat na PyPI.

Publikace, změna ochrany větve a release jsou externí akce vyžadující explicitní
schválení v rámci konkrétního release úkolu.
