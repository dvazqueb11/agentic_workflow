from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-json", required=True, type=Path)
    parser.add_argument("--gates-config", required=True, type=Path)
    parser.add_argument("--report-output", required=True, type=Path)
    args = parser.parse_args()

    perf = load_json(args.results_json)
    gates = load_json(args.gates_config)["performance"]

    observed_runtime = float(perf["runtime_ms"]["median"])
    observed_cpu = float(perf["cpu_time_ms"]["median"])
    observed_peak_rss = int(perf["peak_rss_kb"]["max"])

    runtime_budget = float(gates["runtime_median_ms_max"])
    cpu_budget = float(gates["cpu_time_median_ms_max"])
    rss_budget = int(gates["peak_rss_kb_max"])

    failures: list[dict[str, Any]] = []
    if observed_runtime > runtime_budget:
        failures.append(
            {
                "classification": "runtime_budget_exceeded",
                "metric": "runtime_ms.median",
                "budget": runtime_budget,
                "observed": observed_runtime,
            }
        )
    if observed_cpu > cpu_budget:
        failures.append(
            {
                "classification": "cpu_budget_exceeded",
                "metric": "cpu_time_ms.median",
                "budget": cpu_budget,
                "observed": observed_cpu,
            }
        )
    if observed_peak_rss > rss_budget:
        failures.append(
            {
                "classification": "memory_budget_exceeded",
                "metric": "peak_rss_kb.max",
                "budget": rss_budget,
                "observed": observed_peak_rss,
            }
        )

    passed = not failures
    report = {
        "classification": failures[0]["classification"] if failures else "none",
        "passed": passed,
        "runner": perf.get("runner", {}),
        "test_name": perf.get("test_name", "unknown"),
        "thresholds": {
            "runtime_median_ms_max": runtime_budget,
            "cpu_time_median_ms_max": cpu_budget,
            "peak_rss_kb_max": rss_budget,
        },
        "observed": {
            "runtime_median_ms": observed_runtime,
            "cpu_time_median_ms": observed_cpu,
            "peak_rss_kb_max": observed_peak_rss,
        },
        "failures": failures,
        "notes": [
            "Runtime and CPU values use sample median after warm-up.",
            "Peak RSS uses ru_maxrss on Linux and reflects process peak resident memory.",
            "Budgets are CI policy gates for this demo, not universal production guarantees.",
        ],
    }

    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        "Performance observed: "
        f"runtime median {observed_runtime:.3f}ms, "
        f"cpu median {observed_cpu:.3f}ms, "
        f"peak RSS {observed_peak_rss}KB"
    )
    print(
        "Performance budgets: "
        f"runtime <= {runtime_budget:.3f}ms, "
        f"cpu <= {cpu_budget:.3f}ms, "
        f"peak RSS <= {rss_budget}KB"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
