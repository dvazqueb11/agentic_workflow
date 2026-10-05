from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
AGENTS = ROOT / ".github" / "agents"


class AgenticTopologyTests(unittest.TestCase):
    def test_every_workflow_selects_an_existing_custom_agent(self) -> None:
        workflow_agents = {
            "self-heal.md": "sample-diagnostician",
            "self-heal-policy.md": "sample-policy-gate",
            "self-heal-remediate.md": "sample-remediator",
            "self-heal-escalate.md": "sample-escalation",
            "self-heal-validate.md": "sample-validator",
        }
        for workflow_name, agent_id in workflow_agents.items():
            with self.subTest(workflow=workflow_name):
                workflow = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
                self.assertIn(f"agent: {agent_id}", workflow)
                self.assertTrue((AGENTS / f"{agent_id}.agent.md").is_file())

    def test_native_subagents_are_declared_and_invoked(self) -> None:
        expected_subagents = {
            "self-heal.md": ["sample-log-analyst", "sample-diff-analyst"],
            "self-heal-policy.md": ["sample-provenance-auditor"],
            "self-heal-remediate.md": ["sample-test-planner"],
            "self-heal-validate.md": ["sample-regression-auditor"],
        }
        for workflow_name, subagents in expected_subagents.items():
            workflow = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
            for subagent in subagents:
                with self.subTest(workflow=workflow_name, subagent=subagent):
                    self.assertIn(f"## agent: {subagent}", workflow)
                    self.assertIn(f"`{subagent}` subagent", workflow)

    def test_diagnosis_receives_source_run_evidence(self) -> None:
        workflow = (WORKFLOWS / "self-heal.md").read_text(encoding="utf-8")
        lock = (WORKFLOWS / "self-heal.lock.yml").read_text(encoding="utf-8")
        self.assertIn("${{ github.event.workflow_run.head_sha }}", workflow)
        self.assertIn("/tmp/gh-aw/source-run", workflow)
        self.assertIn("name: Collect source run evidence", lock)
        self.assertRegex(lock, r'"GITHUB_TOOLSETS": "[^"]*\bactions\b')

    def test_parent_profiles_allow_subagent_invocation(self) -> None:
        parent_agents = [
            "sample-diagnostician",
            "sample-policy-gate",
            "sample-remediator",
            "sample-validator",
        ]
        for agent_id in parent_agents:
            with self.subTest(agent=agent_id):
                profile = (AGENTS / f"{agent_id}.agent.md").read_text(encoding="utf-8")
                self.assertRegex(profile, r"tools: \[[^\n]*\"agent\"")

    def test_profiles_allow_only_their_declared_safe_outputs(self) -> None:
        safe_outputs = {
            "sample-diagnostician": ["publish_handoff"],
            "sample-policy-gate": ["publish_handoff"],
            "sample-remediator": ["create_pull_request"],
            "sample-escalation": ["create_issue", "publish_handoff"],
            "sample-validator": ["add_comment"],
        }
        for agent_id, expected_tools in safe_outputs.items():
            profile = (AGENTS / f"{agent_id}.agent.md").read_text(encoding="utf-8")
            self.assertIn('"github/*"', profile)
            for tool in expected_tools:
                with self.subTest(agent=agent_id, tool=tool):
                    self.assertIn(f'"safeoutputs/{tool}"', profile)

    def test_only_remediator_can_create_a_pull_request(self) -> None:
        agentic_sources = list(WORKFLOWS.glob("self-heal*.md"))
        pull_request_writers = [
            path.name
            for path in agentic_sources
            if "create-pull-request:" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(pull_request_writers, ["self-heal-remediate.md"])

    def test_no_agentic_workflow_can_merge(self) -> None:
        for workflow in WORKFLOWS.glob("self-heal*.md"):
            with self.subTest(workflow=workflow.name):
                self.assertNotIn(
                    "merge-pull-request:",
                    workflow.read_text(encoding="utf-8"),
                )

    def test_outcome_workflows_have_opposite_policy_gates(self) -> None:
        remediation = (WORKFLOWS / "self-heal-remediate.md").read_text(encoding="utf-8")
        escalation = (WORKFLOWS / "self-heal-escalate.md").read_text(encoding="utf-8")
        self.assertIn(
            "needs.route.outputs.decision == 'allow_remediation'",
            remediation,
        )
        self.assertIn(
            "needs.route.outputs.decision == 'abstain_and_escalate'",
            escalation,
        )


if __name__ == "__main__":
    unittest.main()
