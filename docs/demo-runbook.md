# Demo runbook

## Prerequisites

- GitHub Actions enabled for the repo.
- Copilot Agentic Workflows configured.
- Labels present: `agentic-self-heal`, `abstention`.
- `gh aw validate` and `gh aw compile` available for workflow source changes.

## A. Healthy state

1. Open a normal PR with no regressions.
2. Confirm CI passes:
   - build + tests
   - coverage gate
   - performance gate
   - policy tests

Expected classification artifact:

```json
{ "classification": "none" }
```

## B. Coverage failure state

1. Add an extra branch in `src/risk_classifier.cpp` without tests.
2. Push and open PR.
3. Observe:
   - coverage gate failure
   - `build/coverage/coverage-gate.json` machine-readable reason(s)
   - CI classification `insufficient_coverage`
4. Follow Diagnose → Policy Gate → Remediate → Healing PR Validation.
5. Human reviewer approves/rejects merge.

## C. Performance failure state

1. Route `CountUniqueCommonTokens` to `CountUniqueCommonTokensSlow` in `src/performance_demo.cpp`.
2. Push and open PR.
3. Observe:
   - performance gate failure
   - `build/performance/performance-gate.json` failing metric with budget/observed values
   - CI classification `runtime_budget_exceeded` (or CPU/memory equivalent)
4. Follow Diagnose → Policy Gate → Remediate → Healing PR Validation.
5. Human reviewer approves/rejects merge.

## Security + governance checkpoints

- Healing remediation is PR-only and labeled.
- Validation blocks test weakening and threshold relaxation.
- Agent never merges; human reviewer decides.

## Reset/Cleanup

```bash
rm -rf build
git restore .
```
