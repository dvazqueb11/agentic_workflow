# Demo Script

## Opening

1. Show a healthy `main` CI run.
2. Show the custom-agent profiles in `.github/agents/`.
3. Show the five agentic workflow sources and explain that their `.lock.yml` files are compiled GitHub Actions.
4. Open `docs/architecture.md` and identify parent coding agents, native subagents, deterministic gates, and safe outputs.

## Path A: bounded self-healing

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

## Path B: infrastructure abstention

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
