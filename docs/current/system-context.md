---
status: implemented
agent_use: always
area: architecture
verified_against_commit: "initial-public-snapshot"
last_verified: "2026-08-02"
related_spec: "docs/specs/public-v0.1.md"
related_plan: "docs/plans/public-v0.1.md"
---

# System context

M.I.K.E. v0.1 je per-user macOS aplikace pro Apple Silicon. Python 3.11+ běží
jako LaunchAgent `io.github.emperorkundis.mike`, zachytává mikrofon, lokálně
přepisuje češtinu a volá Ollamu na loopbacku. Odpověď vysloví `/usr/bin/say` a
zobrazí v lokálním dashboardu/volitelném AppKit overlayi.

Jediné externí runtime spojení je explicitně zapnutý research. Terminál je
read-only a bez shellu. SQLite, config, logy a voiceprint jsou privátní per-user
data. Automatické nasazení, PyPI, cloud, telemetrie a binární distribuce nejsou
součástí v0.1.
