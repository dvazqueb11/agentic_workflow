---
name: Sample Remediate
description: Create one minimal healing pull request for a policy-approved diagnosis
intent: Repair only bounded source or build defects while preserving all quality controls
on:
  workflow_run:
    workflows: ["Sample Policy Gate"]
    types: [completed]
    conclusion: success
    branches: ["**"]
permissions:
  contents: read
  actions: read
  pull-requests: read
engine:
  id: copilot
  agent: sample-remediator
network: defaults
timeout-minutes: 25
max-ai-credits: 500
safe-outputs:
  create-pull-request:
    max: 1
    labels: [agentic-self-heal]
    title-prefix: "[self-heal] "
jobs:
  route:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: read
    outputs:
      decision: ${{ steps.policy.outputs.decision }}
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Download policy handoff
        uses: actions/download-artifact@v8
        with:
          name: agent-handoff
          path: build/handoff
          github-token: ${{ github.token }}
          run-id: ${{ github.event.workflow_run.id }}

      - name: Validate and route policy handoff
        id: policy
        run: |
          set -euo pipefail
          python3 tests/policy/validate_handoff.py \
            --input build/handoff/handoff.json \
            --expected-type policy_decision
          echo "decision=$(jq -r .decision build/handoff/handoff.json)" >> "$GITHUB_OUTPUT"

  agent:
    needs: [route]
    if: needs.route.outputs.decision == 'allow_remediation'
steps:
  - name: Align workspace to failing commit
    if: github.event_name == 'workflow_run'
    env:
      SOURCE_SHA: ${{ github.event.workflow_run.head_sha }}
    run: |
      set -euo pipefail
      git fetch --no-tags origin "${SOURCE_SHA}"
      git checkout --detach "${SOURCE_SHA}"

  - name: Download policy handoff for remediation
    uses: actions/download-artifact@v8
    with:
      name: agent-handoff
      path: build/handoff
      github-token: ${{ github.token }}
      run-id: ${{ github.event.workflow_run.id }}

  - name: Validate approved policy handoff
    run: |
      set -euo pipefail
      python3 tests/policy/validate_handoff.py \
        --input build/handoff/handoff.json \
        --expected-type policy_decision
      test "$(jq -r .decision build/handoff/handoff.json)" = "allow_remediation"
---

# Policy-approved remediation

Read `build/handoff/handoff.json`. Reinspect the source failed run and triggering diff identified by that handoff before making any edit.
For `workflow_run` events, treat `${{ github.event.workflow_run.head_sha }}` as the source revision and ensure your edits are based on that revision, not default branch state.

Ask the `sample-test-planner` subagent which existing test most directly detects the defect and whether a new regression test is necessary. Make the smallest policy-approved change, run the documented CI commands, and use `create-pull-request` exactly once.

The pull-request body must include the original run, diagnosis, policy decision, evidence, changed files, validation performed, confidence, limitations, and an explicit statement that a human must decide whether to merge.

Do not use a memorized dependency-version replacement. Determine any dependency correction from repository evidence and available package metadata.

## agent: `sample-test-planner`
---
description: Identifies the smallest regression validation needed for an approved remediation
tools: ["read", "search"]
---

Inspect the approved diagnosis, relevant source, and existing tests. Return the smallest test plan that proves the defect is fixed without weakening coverage. Do not edit files.

## end agent: `sample-test-planner`
