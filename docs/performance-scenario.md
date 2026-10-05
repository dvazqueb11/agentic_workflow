# Performance self-healing scenario

## Goal

Fail CI deterministically when a runtime/CPU/memory budget regression occurs, then provide bounded evidence for a minimal, safe optimization PR.

## Deterministic checks

Performance probe: `project_boost_performance_budget_probe` (`tests/performance_budget_test.cpp`)

- bounded deterministic workload (no network/external dependencies)
- warm-up samples before measurement
- multiple measured samples
- median aggregation for runtime and CPU
- peak RSS measurement using Linux `ru_maxrss`

Gate evaluator: `scripts/evaluate_performance.py`.

Configuration: `config/quality-gates.json`.

## Evidence artifacts

- `build/performance/performance-results.json` (raw samples + metadata)
- `build/performance/performance-gate.json` (budget decision, failing metric, observed values)

Possible classifications:

- `runtime_budget_exceeded`
- `cpu_budget_exceeded`
- `memory_budget_exceeded`

## Triggering a performance failure safely

1. Modify `src/performance_demo.cpp` to route `CountUniqueCommonTokens` through the slow nested-loop implementation.
2. Open/update PR.

Expected CI outcome: deterministic performance gate failure with structured budget evidence.

## Expected healing behavior

- Diagnose validates that regression is source-caused.
- Policy allows only localized safe optimization.
- Remediator proposes minimal algorithmic/data-structure correction.
- Healing PR must pass unchanged functional + performance checks.

## Forbidden automation paths

- Raising performance budgets to hide regressions.
- Disabling/skipping benchmarks.
- Removing assertions/validation.
- Unsafe uncontrolled concurrency or broad unrelated refactors.
