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

Diagnostika: `mike doctor`, `mike status`,
`./scripts/omnivoice_service.sh status`, potom privátní runtime a OmniVoice logy.
Restart aplikace: `mike restart`; restart OmniVoice služby: helperem `stop` a
`install`. Rollback: zastavit obě namespaced služby, checkoutnout poslední známý release v
novém worktree, vytvořit nové venv, `mike install`, `mike start`. Databázi před
migrací zálohovat jako celek při zastavené službě. Obnova a smazání dat jsou
ruční lidské kroky; agent nesmí mazat MIKE home bez explicitního schválení.
