from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-outcome", required=True)
    parser.add_argument("--coverage-outcome", required=True)
    parser.add_argument("--performance-outcome", required=True)
    parser.add_argument("--coverage-report", required=True, type=Path)
    parser.add_argument("--performance-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    coverage = load_optional_json(args.coverage_report)
    performance = load_optional_json(args.performance_report)

    classification = "none"
    reason = "all_quality_gates_passed"
    details: dict[str, Any] = {}

    if args.build_outcome != "success":
        classification = "functional_test_failure"
        reason = "build_or_functional_tests_failed"
    elif args.coverage_outcome != "success":
        classification = (
            coverage["classification"] if coverage and coverage.get("classification") else "insufficient_coverage"
        )
        reason = "coverage_gate_failed"
        if coverage:
            details["coverage"] = coverage
    elif args.performance_outcome != "success":
        classification = (
            performance["classification"]
            if performance and performance.get("classification")
            else "runtime_budget_exceeded"
        )
        reason = "performance_gate_failed"
        if performance:
            details["performance"] = performance

    payload = {
        "classification": classification,
        "reason": reason,
        "step_outcomes": {
            "build_outcome": args.build_outcome,
            "coverage_outcome": args.coverage_outcome,
            "performance_outcome": args.performance_outcome,
        },
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
