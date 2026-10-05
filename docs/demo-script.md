# Demo Script

## Opening

1. Show a healthy `main` CI run.
2. Show the custom-agent profiles in `.github/agents/`.
3. Show the five agentic workflow sources and explain that their `.lock.yml` files are compiled GitHub Actions.
4. Open `docs/architecture.md` and identify parent coding agents, native subagents, deterministic gates, and safe outputs.

## Path A: dependency bounded self-healing

1. Create a demo branch and change `conanfile.py` from `gtest/1.14.0` to `gtest/99.99.99`.
2. Open a pull request.
3. Open the failed `CI` run and show the exact error in `conan-install.log`.
4. Open `Sample Diagnose`:
   - show the source run correlation
   - show log-analysis and diff-analysis subagent delegation
   - download the validated diagnosis artifact
5. Open `Sample Policy Gate`:
   - show independent provenance and policy checks
   - show `allow_remediation`
6. Open `Sample Remediate`:
   - show the deterministic routing job
   - show the test-planner subagent
   - open the generated `agentic-self-heal` pull request
7. If `GH_AW_CI_TRIGGER_TOKEN` is not configured, use GitHub's **Approve workflows to run** control and explain why bot-created PR events are gated.
8. Show unchanged `Healing PR Validation`:
   - same build and test commands
   - deleted-test and weakening checks
   - protected configuration check
9. Submit the required non-author approval; the review event reruns validation.
10. Open `Sample Healing Review` and show the independent readiness comment.
11. Emphasize that no agent merges; a human makes the final decision.

## Path B: coverage bounded self-healing

1. Add one branch in `src/risk_classifier.cpp` without adding tests.
2. Open a pull request and show `CI` coverage-gate failure.
3. Open `build/coverage/coverage-gate.json` artifact and call out:
   - overall threshold
   - changed-line threshold or not-measurable status
   - uncovered evidence references
4. Follow Diagnose -> Policy Gate -> Remediate and open the generated healing PR.
5. Show that the healing PR adds meaningful tests (not threshold changes) and that unchanged validation now passes.

## Path C: performance bounded self-healing

1. Route `CountUniqueCommonTokens` to the slow path in `src/performance_demo.cpp`.
2. Open a pull request and show performance-gate failure.
3. Open `build/performance/performance-gate.json` and call out:
   - failed metric
   - observed value
   - configured budget
   - runner metadata
4. Follow Diagnose -> Policy Gate -> Remediate and inspect the optimization-focused healing PR.
5. Show that functional tests and performance gate both pass on the healing PR.

## Path D: infrastructure abstention

1. Dispatch `Sample Diagnose` with `sample-lsf-infrastructure-diagnosis`.
2. Show evidence for LSF authorization denial and unavailable NFS release storage.
3. Observe the automatically triggered `Sample Policy Gate`.
4. Show `abstain_and_escalate` and the controlling policy references.
5. Open the automatically triggered `Sample Escalate`:
   - show that the Remediator agent was skipped
   - show the escalation issue
   - show recommended owner `platform-infrastructure`
   - show the next diagnostic action
   - confirm that no branch or pull request was created

## Customer mapping

Relate the simulation to the real environment:

- affected-module detection maps to core/backend/frontend/agentic selective builds
- Conan evidence maps to internal dependency and JFrog flows
- deterministic validation maps to build, regression, packaging, and Coverity gates
- LSF/NFS failures demonstrate safe boundaries around self-hosted runners and external infrastructure
- escalation artifacts can later connect to JIRA through a separately governed safe output

## Close

The value is not unrestricted automatic repair. The value is evidence-first diagnosis, specialized agent delegation, deterministic policy enforcement, minimal change proposals, explicit abstention, and a complete GitHub audit trail.
