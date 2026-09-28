---
name: Sample Diagnose
description: Diagnose failed CI with independent log and diff analysis
intent: Produce a provenance-bound diagnosis before any remediation is considered
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    conclusion: failure
    branches: ["**"]
  workflow_dispatch:
    inputs:
      fixture:
        description: Optional simulated Sample failure
        required: false
        type: choice
        options:
          - live-run
          - sample-dependency-diagnosis
          - sample-lsf-infrastructure-diagnosis
        default: live-run
permissions:
  contents: read
  actions: read
  pull-requests: read
engine:
  id: copilot
  agent: sample-diagnostician
imports:
  - shared/publish-handoff.md
network: defaults
timeout-minutes: 20
max-ai-credits: 300
concurrency:
  job-discriminator: ${{ github.run_id }}
---

# Sample failure diagnosis

Diagnose exactly one failed CI run.

For a `workflow_run` event:

1. Use `${{ github.event.workflow_run.id }}` as the source workflow run.
2. Inspect the failed job and only the relevant logs/artifacts first.
3. Locate the associated pull request or commit and inspect its triggering diff.

For a manual fixture other than `live-run`, read:

`fixtures/failed-runs/${{ github.event.inputs.fixture }}.json`

Treat the fixture as the complete simulated run evidence; do not query or invent customer infrastructure.

Delegate these bounded tasks:

1. Ask the `sample-log-analyst` subagent to identify the failed command, primary error, and whether the evidence indicates source/build behavior or external infrastructure.
2. Ask the `sample-diff-analyst` subagent to identify changed modules and whether the diff could plausibly cause the primary error.
3. Reconcile both reports against the repository policy yourself.

Call `publish-handoff` exactly once with a JSON string matching the `diagnosis` contract in `docs/handoff-contracts.json`. Include the real repository, run ID, run URL, commit SHA, and pull request number when available. Redact token-like values and keep evidence excerpts bounded.

Do not edit files or propose a pull request.

## agent: `sample-log-analyst`
---
description: Extracts bounded failure evidence from CI logs without proposing changes
tools: ["read", "search"]
---

Read only the relevant failed job logs and artifacts. Return:

- failed job and command
- primary error excerpt and its source reference
- likely failure classification
- any secondary noise that should not drive remediation
- confidence and missing evidence

Do not suggest a fix and do not inspect unrelated repository content.

## end agent: `sample-log-analyst`

## agent: `sample-diff-analyst`
---
description: Correlates a triggering diff with Sample-shaped modules and failure evidence
tools: ["read", "search"]
---

Inspect the triggering pull-request or commit diff. Return:

- changed files and affected modules: core, backend, frontend, agentic, packaging, or unknown
- whether the diff could plausibly cause the reported failure
- exact diff references supporting the conclusion
- confidence and any ambiguity

Do not propose edits.

## end agent: `sample-diff-analyst`
