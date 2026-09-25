# Copilot Instructions for Self-Healing CI

- Treat every healing task as diagnosis-first.
- Do not apply static replacement mappings for known invalid versions.
- Investigate the failed run, pull request/commit, and triggering diff before edits.
- Produce concrete evidence references for any diagnosis.
- Follow `docs/healing-policy.md` and `docs/healing-policy.json`.
- If a condition is out of scope, abstain and provide an escalation report.
- Never reduce test, security, static-analysis, or quality coverage.
- Never modify secrets, credentials, permissions, branch protection, or external infrastructure.
- Never push to default branch.
- Always create a pull request labeled `agentic-self-heal` for any code proposal.
