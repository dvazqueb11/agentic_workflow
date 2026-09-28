from __future__ import annotations

import argparse
from pathlib import Path

from healing_rules import load_json


SOURCE_FIELDS = (
    "source_repository",
    "source_workflow_run_id",
    "source_workflow_run_url",
    "source_commit_sha",
    "source_pull_request_number",
)

PREDECESSORS = {
    "policy_decision": ("diagnosis", "diagnosis_workflow_run_id"),
    "escalation_result": ("policy_decision", "policy_workflow_run_id"),
}


def validate_chain(
    current: dict[str, object],
    upstream: dict[str, object],
    predecessor_run_id: int,
) -> list[str]:
    problems: list[str] = []
    current_type = current.get("handoff_type")
    expected = PREDECESSORS.get(current_type)
    if expected is None:
        return [f"unsupported-chained-handoff-type:{current_type}"]

    expected_upstream_type, predecessor_field = expected
    if upstream.get("handoff_type") != expected_upstream_type:
        problems.append(
            "upstream-handoff-type:"
            f"{upstream.get('handoff_type')}!=expected:{expected_upstream_type}"
        )
    if current.get(predecessor_field) != predecessor_run_id:
        problems.append(
            f"{predecessor_field}:{current.get(predecessor_field)}"
            f"!=expected:{predecessor_run_id}"
        )

    for field in SOURCE_FIELDS:
        if current.get(field) != upstream.get(field):
            problems.append(
                f"source-mismatch:{field}:{current.get(field)}!={upstream.get(field)}"
            )

    return sorted(problems)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--upstream", required=True, type=Path)
    parser.add_argument("--predecessor-run-id", required=True, type=int)
    args = parser.parse_args()

    problems = validate_chain(
        load_json(args.current),
        load_json(args.upstream),
        args.predecessor_run_id,
    )
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    print(f"Validated handoff chain from workflow run {args.predecessor_run_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
