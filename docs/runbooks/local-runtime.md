---
status: implemented
agent_use: task-scoped
area: ops
verified_against_commit: "initial-public-snapshot"
last_verified: "2026-08-02"
related_spec: "docs/specs/public-v0.1.md"
related_plan: "docs/plans/public-v0.1.md"
---

# Runbook: lokální runtime

Diagnostika: `mike doctor`, `mike status`, potom privátní runtime logy. Restart:
`mike restart`. Rollback: zastavit službu, checkoutnout poslední známý release v
novém worktree, vytvořit nové venv, `mike install`, `mike start`. Databázi před
migrací zálohovat jako celek při zastavené službě. Obnova a smazání dat jsou
ruční lidské kroky; agent nesmí mazat MIKE home bez explicitního schválení.
