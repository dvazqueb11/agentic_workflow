from __future__ import annotations

import argparse
from pathlib import Path

from healing_rules import load_json, validate_handoff_shape


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--expected-type", required=True)
    parser.add_argument("--source-run-id", type=int)
    parser.add_argument("--source-sha")
    parser.add_argument("--source-repository")
    parser.add_argument("--source-run-url")
    args = parser.parse_args()

    payload = load_json(args.input)
    problems = validate_handoff_shape(payload)

    if payload.get("handoff_type") != args.expected_type:
        problems.append(
            f"handoff-type:{payload.get('handoff_type')}!=expected:{args.expected_type}"
        )
    if (
        args.source_run_id is not None
        and payload.get("source_workflow_run_id") != args.source_run_id
    ):
        problems.append(
            "source-run-id:"
            f"{payload.get('source_workflow_run_id')}!=expected:{args.source_run_id}"
        )
    if args.source_sha is not None and payload.get("source_commit_sha") != args.source_sha:
        problems.append(
            f"source-sha:{payload.get('source_commit_sha')}!=expected:{args.source_sha}"
        )
    if (
        args.source_repository is not None
        and payload.get("source_repository") != args.source_repository
    ):
        problems.append(
            "source-repository:"
            f"{payload.get('source_repository')}!=expected:{args.source_repository}"
        )
    if (
        args.source_run_url is not None
        and payload.get("source_workflow_run_url") != args.source_run_url
    ):
        problems.append(
            "source-run-url:"
            f"{payload.get('source_workflow_run_url')}!=expected:{args.source_run_url}"
        )

    if problems:
        for problem in sorted(set(problems)):
            print(f"ERROR: {problem}")
        return 1

    print(
        f"Validated {args.expected_type} handoff for "
        f"run {payload['source_workflow_run_id']} at {payload['source_commit_sha']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
