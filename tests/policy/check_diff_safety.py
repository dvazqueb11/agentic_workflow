from __future__ import annotations

import argparse
import subprocess
import sys

from healing_rules import detect_test_weakening


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    diff = subprocess.run(
        ["git", "diff", "--name-status", args.base, args.head],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    patch = subprocess.run(
        ["git", "diff", args.base, args.head],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    findings = detect_test_weakening(diff + "\n" + patch)
    if findings:
        print("Validation failed. Found test weakening indicators:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
