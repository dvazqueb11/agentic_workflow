from __future__ import annotations

from pathlib import Path
import unittest

from healing_rules import (
    detect_test_weakening,
    load_json,
    policy_decision_for,
    validate_audit_report_shape,
)


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


if __name__ == "__main__":
    unittest.main()
