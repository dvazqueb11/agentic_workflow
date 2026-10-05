from __future__ import annotations

from pathlib import Path
from contextlib import redirect_stdout
import io
import json
import tempfile
import unittest
from unittest import mock

from extract_handoff import main as extract_handoff_main
from healing_rules import (
    detect_test_weakening,
    load_json,
    policy_decision_for,
    validate_audit_report_shape,
    validate_handoff_shape,
)
from validate_handoff_chain import validate_chain


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures" / "failed-runs"


class PolicyTests(unittest.TestCase):
    def test_reproducible_dependency_failure_fixture(self) -> None:
        fixture = load_json(FIXTURES / "dependency-failure.json")
        self.assertEqual(fixture["classification"], "BUILD_DEPENDENCY")
        self.assertIn("Package 'gtest/99.99.99' not resolved", fixture["log_excerpt"])
        self.assertEqual(fixture["expected_remediation"], "correct_invalid_conan_reference")

    def test_policy_decision_allowed(self) -> None:
        decision = policy_decision_for("BUILD_DEPENDENCY", "correct_invalid_conan_reference")
        self.assertEqual(decision, "allow")

    def test_policy_decision_allows_coverage_test_additions(self) -> None:
        decision = policy_decision_for("insufficient_coverage", "add_meaningful_tests")
        self.assertEqual(decision, "allow")

    def test_policy_decision_allows_performance_optimization(self) -> None:
        decision = policy_decision_for(
            "runtime_budget_exceeded",
            "localized_algorithmic_improvement",
        )
        self.assertEqual(decision, "allow")

    def test_policy_decision_blocks_budget_relaxation_action(self) -> None:
        decision = policy_decision_for("runtime_budget_exceeded", "raise_performance_budgets")
        self.assertEqual(decision, "abstain")

    def test_policy_decision_abstain_for_external(self) -> None:
        fixture = load_json(FIXTURES / "external-system-outage.json")
        decision = policy_decision_for(fixture["classification"], None)
        self.assertEqual(decision, "abstain")

    def test_detect_test_deletion_or_weakening(self) -> None:
        diff_text = (FIXTURES / "weakening-diff.txt").read_text(encoding="utf-8")
        findings = detect_test_weakening(diff_text)
        self.assertTrue(findings)

    def test_audit_report_schema(self) -> None:
        report = load_json(FIXTURES / "audit-report-sample.json")
        missing = validate_audit_report_shape(report)
        self.assertEqual(missing, [])

    def test_safe_sample_diagnosis_contract_and_routing(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-dependency-diagnosis.json")
        self.assertEqual(validate_handoff_shape(diagnosis), [])
        self.assertEqual(
            policy_decision_for(
                diagnosis["failure_classification"],
                diagnosis["remediation_action"],
            ),
            "allow",
        )

    def test_infrastructure_diagnosis_contract_and_routing(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-lsf-infrastructure-diagnosis.json")
        self.assertEqual(validate_handoff_shape(diagnosis), [])
        self.assertEqual(
            policy_decision_for(
                diagnosis["failure_classification"],
                diagnosis["remediation_action"],
            ),
            "abstain",
        )

    def test_coverage_diagnosis_contract_and_routing(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-coverage-diagnosis.json")
        self.assertEqual(validate_handoff_shape(diagnosis), [])
        self.assertEqual(
            policy_decision_for(
                diagnosis["failure_classification"],
                diagnosis["remediation_action"],
            ),
            "allow",
        )

    def test_performance_diagnosis_contract_and_routing(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-performance-diagnosis.json")
        self.assertEqual(validate_handoff_shape(diagnosis), [])
        self.assertEqual(
            policy_decision_for(
                diagnosis["failure_classification"],
                diagnosis["remediation_action"],
            ),
            "allow",
        )

    def test_policy_handoffs_match_expected_branches(self) -> None:
        allow = load_json(FIXTURES / "sample-policy-allow.json")
        abstain = load_json(FIXTURES / "sample-policy-abstain.json")
        self.assertEqual(validate_handoff_shape(allow), [])
        self.assertEqual(validate_handoff_shape(abstain), [])
        self.assertEqual(allow["decision"], "allow_remediation")
        self.assertEqual(abstain["decision"], "abstain_and_escalate")

    def test_handoff_rejects_mismatched_provenance(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-dependency-diagnosis.json")
        diagnosis["source_commit_sha"] = "not-a-sha"
        self.assertIn("invalid-source-commit-sha", validate_handoff_shape(diagnosis))

    def test_extract_handoff_rejects_multiple_payloads(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-dependency-diagnosis.json")
        agent_output = {
            "items": [
                {"type": "publish_handoff", "payload": json.dumps(diagnosis)},
                {"type": "publish_handoff", "payload": json.dumps(diagnosis)},
            ]
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "agent-output.json"
            destination = Path(temporary_directory) / "handoff.json"
            source.write_text(json.dumps(agent_output), encoding="utf-8")

            with (
                mock.patch(
                    "sys.argv",
                    [
                        "extract_handoff.py",
                        "--agent-output",
                        str(source),
                        "--output",
                        str(destination),
                    ],
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(extract_handoff_main(), 1)
            self.assertFalse(destination.exists())

    def test_policy_handoff_preserves_diagnosis_provenance(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-dependency-diagnosis.json")
        policy = load_json(FIXTURES / "sample-policy-allow.json")
        self.assertEqual(validate_chain(policy, diagnosis, 2001), [])

    def test_chain_rejects_source_provenance_change(self) -> None:
        diagnosis = load_json(FIXTURES / "sample-dependency-diagnosis.json")
        policy = load_json(FIXTURES / "sample-policy-allow.json")
        policy["source_commit_sha"] = "3333333333333333333333333333333333333333"
        self.assertIn(
            "source-mismatch:source_commit_sha:"
            "3333333333333333333333333333333333333333"
            "!=1111111111111111111111111111111111111111",
            validate_chain(policy, diagnosis, 2001),
        )


if __name__ == "__main__":
    unittest.main()
