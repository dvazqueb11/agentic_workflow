from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from healing_rules import validate_handoff_shape


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-output", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.agent_output.open("r", encoding="utf-8") as f:
        agent_output: dict[str, Any] = json.load(f)

    items = [
        item
        for item in agent_output.get("items", [])
        if item.get("type") == "publish_handoff"
    ]
    if len(items) != 1:
        print(f"ERROR: expected exactly one publish_handoff item, found {len(items)}")
        return 1

    raw_payload = items[0].get("payload")
    if not isinstance(raw_payload, str):
        print("ERROR: publish_handoff payload must be a JSON string")
        return 1

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        print(f"ERROR: publish_handoff payload is not valid JSON: {error}")
        return 1

    if not isinstance(payload, dict):
        print("ERROR: publish_handoff payload must decode to an object")
        return 1

    problems = validate_handoff_shape(payload)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Published validated {payload['handoff_type']} handoff to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
