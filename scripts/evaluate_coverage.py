from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_changed_lines(base_sha: str, head_sha: str) -> dict[str, set[int]]:
    if not base_sha or not head_sha:
        return {}

    result = subprocess.run(
        [
            "git",
            "diff",
            "--unified=0",
            "--diff-filter=AM",
            base_sha,
            head_sha,
            "--",
            "src",
            "include",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    changed: dict[str, set[int]] = {}
    current_file: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if not line.startswith("@@") or current_file is None:
            continue
        # format: @@ -a,b +c,d @@
        plus_segment = line.split(" +", maxsplit=1)[1].split(" ", maxsplit=1)[0]
        start_text, _, count_text = plus_segment.partition(",")
        start = int(start_text)
        count = int(count_text) if count_text else 1
        if count == 0:
            continue
        bucket = changed.setdefault(current_file, set())
        for number in range(start, start + count):
            bucket.add(number)
    return changed


def list_tracked_project_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "src", "include"],
        check=True,
        capture_output=True,
        text=True,
    )
    tracked: set[str] = set()
    for line in result.stdout.splitlines():
        normalized = line.strip().replace("\\", "/")
        if normalized:
            tracked.add(normalized)
    return tracked


def to_repo_candidate(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    if normalized.startswith("src/") or normalized.startswith("include/"):
        return normalized
    for anchor in ("src/", "include/"):
        marker = f"/{anchor}"
        if marker in normalized:
            return anchor + normalized.split(marker, maxsplit=1)[1]
    return normalized


def extract_line_coverage(
    gcovr_payload: dict[str, Any], tracked_files: set[str]
) -> dict[str, dict[int, int]]:
    per_file: dict[str, dict[int, int]] = {}
    files = gcovr_payload.get("files", [])
    for file_payload in files:
        file_name = file_payload.get("file")
        if not isinstance(file_name, str):
            continue
        repo_file = to_repo_candidate(file_name)
        if repo_file not in tracked_files:
            continue
        lines = file_payload.get("lines", [])
        line_hits: dict[int, int] = {}
        for line_payload in lines:
            line_number = line_payload.get("line_number")
            count = line_payload.get("count")
            if isinstance(line_number, int) and isinstance(count, int):
                line_hits[line_number] = count
        per_file[repo_file] = line_hits
    return per_file


def compute_overall_line_percent(per_file_line_hits: dict[str, dict[int, int]]) -> float:
    total_lines = 0
    covered_lines = 0
    for lines in per_file_line_hits.values():
        for count in lines.values():
            total_lines += 1
            if count > 0:
                covered_lines += 1

    if total_lines == 0:
        return 0.0
    return (covered_lines / total_lines) * 100.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-json", required=True, type=Path)
    parser.add_argument("--gates-config", required=True, type=Path)
    parser.add_argument("--report-output", required=True, type=Path)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--head-sha", default="")
    args = parser.parse_args()

    coverage_payload = load_json(args.coverage_json)
    gates = load_json(args.gates_config)

    overall_threshold = float(gates["coverage"]["overall_line_coverage_min"])
    changed_threshold = float(gates["coverage"]["changed_line_coverage_min"])

    tracked_files = list_tracked_project_files()
    per_file_line_hits = extract_line_coverage(coverage_payload, tracked_files)
    line_percent = compute_overall_line_percent(per_file_line_hits)
    overall_passed = line_percent >= overall_threshold

    changed_lines = parse_changed_lines(args.base_sha, args.head_sha)

    measurable_total = 0
    measurable_covered = 0
    raw_changed_total = 0

    for file_name, line_numbers in changed_lines.items():
        normalized_file = to_repo_candidate(file_name)
        if normalized_file not in tracked_files:
            continue
        raw_changed_total += len(line_numbers)
        coverage_map = per_file_line_hits.get(normalized_file, {})
        if not coverage_map:
            continue
        for line_number in line_numbers:
            if line_number not in coverage_map:
                continue
            measurable_total += 1
            if coverage_map[line_number] > 0:
                measurable_covered += 1

    if measurable_total > 0:
        changed_rate = (measurable_covered / measurable_total) * 100.0
        changed_status = "measured"
        changed_passed = changed_rate >= changed_threshold
    elif raw_changed_total > 0:
        changed_rate = None
        changed_status = "not_measurable"
        changed_passed = True
    else:
        changed_rate = None
        changed_status = "no_changed_lines"
        changed_passed = True

    passed = overall_passed and changed_passed
    reasons: list[str] = []
    if not overall_passed:
        reasons.append("overall_coverage_below_threshold")
    if not changed_passed:
        reasons.append("changed_line_coverage_below_threshold")
    if changed_status == "not_measurable":
        reasons.append("changed_line_coverage_not_measurable_with_current_instrumentation")

    report = {
        "classification": "insufficient_coverage" if not passed else "none",
        "passed": passed,
        "thresholds": {
            "overall_line_coverage_min": overall_threshold,
            "changed_line_coverage_min": changed_threshold,
        },
        "overall": {
            "line_percent": line_percent,
            "passed": overall_passed,
        },
        "changed_lines": {
            "status": changed_status,
            "raw_changed_lines_total": raw_changed_total,
            "measurable_lines_total": measurable_total,
            "covered_lines": measurable_covered,
            "line_percent": changed_rate,
            "passed": changed_passed,
        },
        "reasons": reasons,
    }

    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Overall line coverage: {line_percent:.2f}% (threshold {overall_threshold:.2f}%)")
    if changed_status == "measured":
        print(
            "Changed-line coverage: "
            f"{changed_rate:.2f}% ({measurable_covered}/{measurable_total}) "
            f"(threshold {changed_threshold:.2f}%)"
        )
    elif changed_status == "not_measurable":
        print("Changed-line coverage: not measurable for this diff with current instrumentation.")
    else:
        print("Changed-line coverage: no changed src/include lines to evaluate.")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
