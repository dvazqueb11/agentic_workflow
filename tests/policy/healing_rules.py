from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_REMEDIATIONS = {
    "BUILD_DEPENDENCY": {
        "correct_invalid_conan_reference",
    },
    "SOURCE_COMPILE": {
        "add_missing_include",
        "small_source_defect_fix",
    },
    "UNIT_TEST": {
        "small_source_defect_fix",
        "add_regression_test",
    },
    "STATIC_ANALYSIS": {
        "bounded_lint_or_static_analysis_fix",
    },
}

DIAGNOSIS_ONLY = {
    "RUNNER_OR_EXTERNAL_SYSTEM",
    "UNKNOWN",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_audit_report_shape(report: dict[str, Any]) -> list[str]:
    required = {
        "source_workflow_run",
        "source_pull_request_or_commit",
        "failed_job",
        "failed_command",
        "relevant_log_references",
        "failure_classification",
        "diagnosis",
        "confidence",
        "policy_decision",
        "proposed_change",
        "tests_and_validation_performed",
        "outcome",
        "human_approver_required",
    }
    return sorted(required.difference(report.keys()))


def policy_decision_for(classification: str, remediation_action: str | None) -> str:
    if classification in DIAGNOSIS_ONLY:
        return "abstain"
    if classification not in ALLOWED_REMEDIATIONS:
        return "abstain"
    if remediation_action in ALLOWED_REMEDIATIONS[classification]:
        return "allow"
    return "abstain"


def detect_test_weakening(diff_text: str) -> list[str]:
    problems: list[str] = []
    deleted_tests = re.findall(r"^D\s+(tests/.*)$", diff_text, flags=re.MULTILINE)
    if deleted_tests:
        problems.append(f"deleted-test-files:{','.join(deleted_tests)}")

    weakened_patterns = [
        r"^\+\s*GTEST_SKIP\(",
        r"^\+\s*DISABLED_",
        r"^\+\s*@pytest\.mark\.skip",
        r"^-.*EXPECT_",
        r"^-.*ASSERT_",
    ]
    for pattern in weakened_patterns:
        if re.search(pattern, diff_text, flags=re.MULTILINE):
            problems.append(f"pattern-match:{pattern}")
    return problems
