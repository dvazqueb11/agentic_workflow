# Coverage self-healing scenario

## Goal

Fail CI deterministically when test coverage is insufficient, then provide structured evidence for a policy-bound healing PR that adds meaningful tests.

## Deterministic checks

1. Build with coverage instrumentation (`PROJECT_BOOST_ENABLE_COVERAGE=ON`).
2. Run functional and policy tests.
3. Generate machine-readable coverage reports with `gcovr`.
4. Evaluate gates via `scripts/evaluate_coverage.py`:
   - overall line coverage threshold
   - changed-line coverage threshold when measurable

Configuration: `config/quality-gates.json`.

## Evidence artifacts

- `build/coverage/coverage.json` (raw machine-readable coverage)
- `build/coverage/cobertura.xml` (interop/report tooling)
- `build/coverage/summary.txt` (human-readable summary)
- `build/coverage/coverage-gate.json` (gate decision + reasons)

## Triggering a coverage failure safely

1. Add a meaningful new branch in `src/risk_classifier.cpp`.
2. Do **not** add matching tests.
3. Open/update PR.

Expected CI outcome: coverage gate fails and emits `insufficient_coverage` evidence.

## Expected healing behavior

- Diagnose correlates failing gate + changed code.
- Policy allows only bounded test-centric remediation.
- Remediator proposes smallest meaningful tests (and minimal testability changes only if needed).
- Healing PR reruns unchanged deterministic checks.

## Forbidden automation paths

- Lowering coverage thresholds.
- Excluding changed production files without policy justification.
- Empty/meaningless/skipped tests.
- Production logic changes made only to inflate coverage.
