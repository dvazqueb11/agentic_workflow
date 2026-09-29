---
name: Sample Escalate
description: Escalate infrastructure and out-of-policy failures without changing code
intent: Route non-code failures to the correct owner with actionable evidence
on:
  workflow_run:
    workflows: ["Sample Policy Gate"]
    types: [completed]
    conclusion: success
    branches: ["**"]
permissions:
  contents: read
  actions: read
  issues: read
engine:
  id: copilot
  agent: sample-escalation
imports:
  - shared/publish-handoff.md
network: defaults
timeout-minutes: 15
max-ai-credits: 200
safe-outputs:
  report-failure-as-issue: false
  create-issue:
    max: 1
    labels: [agentic-self-heal, abstention]
    title-prefix: "[self-heal escalation] "
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
    if: needs.route.outputs.decision == 'abstain_and_escalate'
steps:
  - name: Download policy handoff for escalation
    uses: actions/download-artifact@v8
    with:
      name: agent-handoff
      path: build/handoff
      github-token: ${{ github.token }}
      run-id: ${{ github.event.workflow_run.id }}

  - name: Validate abstention policy handoff
    run: |
      set -euo pipefail
      python3 tests/policy/validate_handoff.py \
        --input build/handoff/handoff.json \
        --expected-type policy_decision
      test "$(jq -r .decision build/handoff/handoff.json)" = "abstain_and_escalate"
---

# Infrastructure and out-of-policy escalation

Read `build/handoff/handoff.json` and inspect the original failed-run evidence it identifies.

Use `create-issue` exactly once to publish:

- source run, commit, and pull request
- bounded evidence excerpts
- why code remediation is prohibited
- recommended owner
- next diagnostic action
- explicit confirmation that no code change was created

Also call `publish-handoff` exactly once with an `escalation_result` JSON string matching `docs/handoff-contracts.json`. Set `code_change_created` to `false`.
Preserve the original source provenance and set `policy_workflow_run_id` to `${{ github.event.workflow_run.id }}`.
