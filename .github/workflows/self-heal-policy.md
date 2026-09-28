---
name: Sample Policy Gate
description: Independently decide whether a validated diagnosis may be remediated
intent: Prevent coding agents from acting on infrastructure, ambiguous, or out-of-policy failures
on:
  workflow_run:
    workflows: ["Sample Diagnose"]
    types: [completed]
    conclusion: success
    branches: ["**"]
  workflow_dispatch:
    inputs:
      diagnosis_fixture:
        description: Diagnosis fixture for a manual policy demonstration
        required: true
        type: choice
        options:
          - sample-dependency-diagnosis
          - sample-lsf-infrastructure-diagnosis
permissions:
  contents: read
  actions: read
engine:
  id: copilot
  agent: sample-policy-gate
imports:
  - shared/publish-handoff.md
network: defaults
timeout-minutes: 15
max-ai-credits: 200
concurrency:
  job-discriminator: ${{ github.run_id }}
steps:
  - name: Download diagnosis handoff
    if: github.event_name == 'workflow_run'
    uses: actions/download-artifact@v8
    with:
      name: agent-handoff
      path: build/handoff
      github-token: ${{ github.token }}
      run-id: ${{ github.event.workflow_run.id }}

  - name: Load diagnosis fixture
    if: github.event_name == 'workflow_dispatch'
    env:
      DIAGNOSIS_FIXTURE: ${{ github.event.inputs.diagnosis_fixture }}
    run: |
      set -euo pipefail
      mkdir -p build/handoff
      cp "fixtures/failed-runs/${DIAGNOSIS_FIXTURE}.json" \
        build/handoff/handoff.json

  - name: Validate diagnosis handoff
    run: |
      set -euo pipefail
      python3 tests/policy/validate_handoff.py \
        --input build/handoff/handoff.json \
        --expected-type diagnosis
---

# Independent remediation policy decision

Read `build/handoff/handoff.json`, `docs/healing-policy.md`, and `docs/healing-policy.json`.

Verify that the diagnosis is supported by its evidence and that its remediation action exactly matches the allowed action for its classification. Ask the `sample-provenance-auditor` subagent to check correlation fields and evidence references, then make the policy decision yourself.

Call `publish-handoff` exactly once with a JSON string matching the `policy_decision` contract in `docs/handoff-contracts.json`.
Preserve all `source_*` values from the diagnosis exactly. For an automatic run, set `diagnosis_workflow_run_id` to `${{ github.event.workflow_run.id }}`.

- Use `allow_remediation` only for a bounded, explicit, policy-listed action with sufficient evidence.
- Use `abstain_and_escalate` for infrastructure, credentials, permissions, NFS, LSF, runners, external services, ambiguity, insufficient evidence, or any malformed context.

Do not edit code or create a pull request.

## agent: `sample-provenance-auditor`
---
description: Checks diagnosis provenance and evidence correlation without making the policy decision
tools: ["read", "search"]
---

Inspect the diagnosis handoff. Verify that repository, run, commit, pull request, diff summary, and evidence references are internally consistent. Report mismatches, missing evidence, and confidence. Do not decide whether remediation is allowed.

## end agent: `sample-provenance-auditor`
