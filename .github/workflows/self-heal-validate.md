---
name: Sample Healing Review
description: Independently review a healing pull request after deterministic validation
intent: Give a human a provenance-backed readiness assessment without auto-approval or merge
on:
  workflow_run:
    workflows: ["Healing PR Validation"]
    types: [completed]
    branches: ["**"]
permissions:
  contents: read
  actions: read
  pull-requests: read
engine:
  id: copilot
  agent: sample-validator
network: defaults
timeout-minutes: 15
max-ai-credits: 250
safe-outputs:
  add-comment:
    max: 1
    target: "*"
    footer: true
---

# Independent healing pull-request review

Inspect deterministic validation run `${{ github.event.workflow_run.id }}` and identify its associated pull request. If it is not labeled `agentic-self-heal`, finish with no write.

Correlate the pull request body and diff with the original failed run, diagnosis, and policy decision. Ask the `sample-regression-auditor` subagent to inspect whether tests or quality controls were weakened. Then post one pull-request comment with:

- deterministic validation conclusion and failed checks, if any
- source-run and commit correlation
- policy consistency
- anti-weakening assessment
- `ready_for_human_review` or `not_ready`
- explicit statement that this agent does not approve or merge

Treat missing provenance, failed deterministic validation, or ambiguous policy evidence as `not_ready`.

## agent: `sample-regression-auditor`
---
description: Reviews a healing pull-request diff for test deletion, skipped checks, and weakened assertions
tools: ["read", "search"]
---

Inspect only the healing pull-request diff and validation evidence. Report deleted tests, new skips, removed assertions, disabled checks, workflow permission changes, or protected configuration changes. Cite exact files and evidence. Do not edit or approve.

## end agent: `sample-regression-auditor`
