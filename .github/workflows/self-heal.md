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
          - sample-coverage-diagnosis
          - sample-performance-diagnosis
          - sample-lsf-infrastructure-diagnosis
        default: live-run
permissions:
  contents: read
  actions: read
  pull-requests: read
safe-outputs:
  report-failure-as-issue: false
engine:
  id: copilot
  agent: sample-diagnostician
imports:
  - shared/publish-handoff.md
tools:
  github:
    toolsets: [context, repos, pull_requests, actions]
network: defaults
timeout-minutes: 20
max-ai-credits: 300
concurrency:
  job-discriminator: ${{ github.run_id }}
steps:
  - name: Collect source run evidence
    if: github.event_name == 'workflow_run'
    env:
      GH_TOKEN: ${{ github.token }}
      SOURCE_REPOSITORY: ${{ github.repository }}
      SOURCE_RUN_ID: ${{ github.event.workflow_run.id }}
      SOURCE_SHA: ${{ github.event.workflow_run.head_sha }}
    run: |
      set -uo pipefail
      out=/tmp/gh-aw/source-run
      mkdir -p "$out"
      gh api "repos/${SOURCE_REPOSITORY}/actions/runs/${SOURCE_RUN_ID}" \
        > "$out/run.json" || echo "unavailable" > "$out/run.json"
      gh api "repos/${SOURCE_REPOSITORY}/actions/runs/${SOURCE_RUN_ID}/jobs?per_page=100" \
        > "$out/jobs.json" || echo "unavailable" > "$out/jobs.json"
      { gh run view "$SOURCE_RUN_ID" -R "$SOURCE_REPOSITORY" --log-failed || echo "unavailable"; } \
        | tail -n 300 > "$out/failed-job-log.txt"
      gh api "repos/${SOURCE_REPOSITORY}/commits/${SOURCE_SHA}/pulls" \
        > "$out/pulls.json" || echo "unavailable" > "$out/pulls.json"
      { gh api -H "Accept: application/vnd.github.diff" \
          "repos/${SOURCE_REPOSITORY}/commits/${SOURCE_SHA}" || echo "unavailable"; } \
        | head -c 200000 > "$out/commit.diff"
      gh run download "$SOURCE_RUN_ID" -R "$SOURCE_REPOSITORY" -n ci-evidence -D "$out/ci-evidence" || true
      ls -la "$out"
---

# Sample failure diagnosis

Diagnose exactly one failed CI run.

For a `workflow_run` event:

1. Use `${{ github.event.workflow_run.id }}` as the source workflow run and `${{ github.event.workflow_run.head_sha }}` as its commit SHA.
2. Read the evidence collected for that run in `/tmp/gh-aw/source-run/` (`run.json`, `jobs.json`, `failed-job-log.txt`, `pulls.json`, `commit.diff`, `ci-evidence/**`). Inspect the failed job and only the relevant logs/artifacts first. Use GitHub MCP tools only if a file is marked `unavailable`.
3. Locate the associated pull request or commit and inspect its triggering diff.

For a manual fixture other than `live-run`, read:

`fixtures/failed-runs/${{ github.event.inputs.fixture }}.json`

Treat the fixture as the complete simulated run evidence; do not query or invent customer infrastructure.

Delegate these bounded tasks:

1. Ask the `sample-log-analyst` subagent to identify the failed command, primary error, and whether the evidence indicates source/build behavior or external infrastructure.
2. Ask the `sample-diff-analyst` subagent to identify changed modules and whether the diff could plausibly cause the primary error.
3. Reconcile both reports against the repository policy yourself.

Call `publish-handoff` exactly once with a JSON string matching the `diagnosis` contract in `docs/handoff-contracts.json`. Include the real repository, run ID, run URL, commit SHA, and pull request number when available. Redact token-like values and keep evidence excerpts bounded.

Use one of these classifications when supported by evidence:

- `dependency_failure`
- `insufficient_coverage`
- `runtime_budget_exceeded`
- `memory_budget_exceeded`
- `cpu_budget_exceeded`
- `functional_test_failure`
- `unsupported_or_unsafe_remediation`
- `runner_or_external_system`
- `unknown`

The handoff is rejected unless `source_commit_sha` is the full 40-character lowercase commit SHA and `affected_modules` is a non-empty list of module names. Never use placeholders such as `unknown` for the commit SHA; if the affected modules cannot be determined, use `["unknown"]` and classify the failure as `unknown`.

Do not edit files or propose a pull request.

## agent: sample-log-analyst
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

## end agent: sample-log-analyst

## agent: sample-diff-analyst
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

## end agent: sample-diff-analyst
