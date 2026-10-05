from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HANDOFF_CONTRACTS = ROOT / "docs" / "handoff-contracts.json"

ALLOWED_REMEDIATIONS = {
    "dependency_failure": {
        "correct_invalid_conan_reference",
    },
    "insufficient_coverage": {
        "add_meaningful_tests",
        "add_test_fixtures",
        "minimal_testability_fix",
        "update_associated_docs",
    },
    "functional_test_failure": {
        "add_missing_include",
        "small_source_defect_fix",
        "add_regression_test",
    },
    "runtime_budget_exceeded": {
        "localized_algorithmic_improvement",
        "remove_unnecessary_allocation_or_copy",
        "improve_data_structure_use",
        "bounded_safe_cache",
        "add_or_refine_deterministic_performance_test",
    },
    "memory_budget_exceeded": {
        "localized_algorithmic_improvement",
        "remove_unnecessary_allocation_or_copy",
        "improve_data_structure_use",
        "bounded_safe_cache",
        "add_or_refine_deterministic_performance_test",
    },
    "cpu_budget_exceeded": {
        "localized_algorithmic_improvement",
        "remove_unnecessary_allocation_or_copy",
        "improve_data_structure_use",
        "bounded_safe_cache",
        "add_or_refine_deterministic_performance_test",
    },
    "unsupported_or_unsafe_remediation": set(),
    "runner_or_external_system": set(),
    "unknown": set(),
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
    "runner_or_external_system",
    "unknown",
    "unsupported_or_unsafe_remediation",
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


def validate_handoff_shape(
    payload: dict[str, Any],
    contracts_path: Path = HANDOFF_CONTRACTS,
) -> list[str]:
    problems: list[str] = []
    contracts = load_json(contracts_path)
    handoff_type = payload.get("handoff_type")
    contract = contracts["contracts"].get(handoff_type)
    if contract is None:
        return [f"unsupported-handoff-type:{handoff_type}"]

    if payload.get("schema_version") != contracts["schema_version"]:
        problems.append(
            f"schema-version:{payload.get('schema_version')}!=expected:{contracts['schema_version']}"
        )

    for field in contract["required"]:
        if field not in payload:
            problems.append(f"missing:{field}")

    for field in contract.get("string_fields", []):
        value = payload.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            problems.append(f"invalid-string:{field}")

    for field in contract.get("integer_fields", []):
        value = payload.get(field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            problems.append(f"invalid-positive-integer:{field}")

    for field in contract.get("boolean_fields", []):
        value = payload.get(field)
        if value is not None and not isinstance(value, bool):
            problems.append(f"invalid-boolean:{field}")

    for field in contract.get("array_fields", []):
        value = payload.get(field)
        if value is not None and (
            not isinstance(value, list)
            or not value
            or any(not isinstance(item, str) or not item.strip() for item in value)
        ):
            problems.append(f"invalid-string-array:{field}")

    for field, allowed_values in contract.get("enums", {}).items():
        if field in payload and payload[field] not in allowed_values:
            problems.append(f"invalid-enum:{field}:{payload[field]}")

    source_sha = payload.get("source_commit_sha")
    if source_sha is not None and not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        problems.append("invalid-source-commit-sha")

    source_url = payload.get("source_workflow_run_url")
    if source_url is not None and not source_url.startswith("https://github.com/"):
        problems.append("invalid-source-workflow-run-url")

    nullable_fields = set(contract.get("nullable_fields", []))
    for field in nullable_fields:
        if field in payload and payload[field] is None:
            problems = [problem for problem in problems if not problem.endswith(f":{field}")]

    return sorted(set(problems))


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
