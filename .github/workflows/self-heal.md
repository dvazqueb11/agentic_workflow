---
name: Self-Healing Agentic Workflow
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
  workflow_dispatch:
    inputs:
      run_id:
        description: "Failed CI run ID to investigate"
        required: false
      pull_request_number:
        description: "Pull request number to investigate"
        required: false
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
network: defaults
safe-outputs:
  create-pull-request:
    max: 1
    labels: [agentic-self-heal]
    title-prefix: "[self-heal] "
  create-issue:
    max: 1
    labels: [agentic-self-heal, abstention]
---

# Self-Heal Agentic Workflow

## Purpose

Investigate failed CI runs and, when policy permits and evidence is sufficient, propose the smallest safe remediation via a pull request.

Only proceed when either:
- Trigger is `workflow_dispatch`, or
- Trigger is `workflow_run` for workflow `CI` with failed conclusion.
If no failed CI context is present, abstain and produce a diagnosis-only issue.

## Triggers

- `workflow_run` completion for workflow named `CI` where `conclusion == failure`.
- `workflow_dispatch` with:
  - `run_id` (optional)
  - `pull_request_number` (optional)

## Permissions and safety envelope

- Read-only repository and Actions access by default.
- Minimum write access only for creating a healing branch and pull request.
- No direct writes to default branch.
- No automatic merge.
- Bounded AI-credit budget.
- GitHub Copilot is the default engine.

## Required operating procedure

1. Locate the failed CI run and associated pull request or commit.
2. Inspect only relevant failed logs and artifacts first.
3. Read the triggering diff before unrelated repository files.
4. Classify failure as exactly one:
   - BUILD_DEPENDENCY
   - SOURCE_COMPILE
   - UNIT_TEST
   - STATIC_ANALYSIS
   - RUNNER_OR_EXTERNAL_SYSTEM
   - UNKNOWN
5. Quote concrete evidence from logs/artifacts.
6. Distinguish triggering defect from secondary noise.
7. Assign confidence and explain uncertainty.
8. Check remediation policy before editing.
9. If safely remediable, create the smallest patch.
10. Add/update a regression test when appropriate.
11. Never delete, quarantine, skip, or weaken failing tests.
12. Never disable/reduce build, test, security, static-analysis, or quality checks.
13. Never modify credentials, secrets, branch protections, permissions, runner config, or external infrastructure.
14. Never introduce unbounded retries.
15. Never push to default branch.
16. Run documented local build and test commands.
17. Open a pull request labeled `agentic-self-heal`.
18. Include in PR:
    - failed workflow and job
    - failure classification
    - likely root cause
    - exact supporting evidence
    - files changed
    - why change is minimal
    - tests added/updated
    - validation executed
    - confidence
    - limitations
    - explicit human approval requirement
19. If evidence is insufficient or issue is out of policy, abstain.
20. On abstention, produce missing evidence, recommended owner, and next diagnostic step.

## Required outputs

- Audit artifact in JSON + Markdown format under `artifacts/healing-reports/`.
- Pull request body using `.github/pull_request_template.md`.

## Compilation note

This Markdown workflow must be compiled with the official `gh-aw` extension to generate `self-heal.lock.yml`.
