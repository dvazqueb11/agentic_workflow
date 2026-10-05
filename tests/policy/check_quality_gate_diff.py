from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_json_at_ref(ref: str, path: str) -> dict[str, Any]:
    blob = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(blob)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--path", default="config/quality-gates.json")
    args = parser.parse_args()

    changed = subprocess.run(
        ["git", "diff", "--name-only", args.base, args.head, "--", args.path],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not changed:
        return 0

    base = load_json_at_ref(args.base, args.path)
    head = load_json_at_ref(args.head, args.path)
    violations: list[str] = []

    if head["coverage"]["overall_line_coverage_min"] < base["coverage"]["overall_line_coverage_min"]:
        violations.append("coverage.overall_line_coverage_min was lowered")
    if head["coverage"]["changed_line_coverage_min"] < base["coverage"]["changed_line_coverage_min"]:
        violations.append("coverage.changed_line_coverage_min was lowered")
    if head["performance"]["runtime_median_ms_max"] > base["performance"]["runtime_median_ms_max"]:
        violations.append("performance.runtime_median_ms_max was increased")
    if head["performance"]["cpu_time_median_ms_max"] > base["performance"]["cpu_time_median_ms_max"]:
        violations.append("performance.cpu_time_median_ms_max was increased")
    if head["performance"]["peak_rss_kb_max"] > base["performance"]["peak_rss_kb_max"]:
        violations.append("performance.peak_rss_kb_max was increased")

    if violations:
        print("Quality-gate policy violation(s):")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Quality-gates updated without threshold relaxation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
