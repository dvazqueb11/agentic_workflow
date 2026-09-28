# Healing Policy

## Allowed (for this demo)

- Correct an invalid Conan dependency reference.
- Add a missing include.
- Correct a small source defect demonstrated by a failing unit test.
- Add or improve a regression test.
- Correct a bounded formatting or linting problem.
- Correct a bounded C/C++ static-analysis defect.

## Diagnosis-only (must abstain from code changes)

- Credentials, signing, or authentication failures.
- Missing access to private package registries.
- NFS and storage failures.
- Runner offline, disk-full, queue, or capacity failures.
- LSF permissions or infrastructure tags.
- External-system outages.
- Ambiguous failures without sufficient evidence.

## Blocked

- Any secrets or credential changes.
- Direct default-branch pushes.
- Automatic merge.
- Deleting or weakening tests.
- Disabling quality or security checks.
- Branch-protection changes.
- Workflow permission broadening.
- Force pushes.
- Unbounded retries.
- Broad refactors unrelated to failure.

## Audit report requirements

Each healing attempt must record:

- source workflow run
- source pull request or commit
- failed job and command
- relevant log references
- failure classification
- diagnosis
- confidence
- policy decision
- proposed change
- tests and validation performed
- outcome
- abstention reason when applicable
- human approver requirement

## Multi-agent handoff requirements

- Every handoff must match `docs/handoff-contracts.json`.
- Every handoff must include the source repository, workflow run, commit SHA, and pull request number when available.
- A custom safe-output job must validate the handoff before publishing it as an artifact.
- A downstream workflow must validate the artifact again before its coding agent runs.
- The policy decision must be independent from the diagnosis.
- Remediation must not run for `abstain_and_escalate`.
- Escalation must not create a branch, commit, or pull request.
- A validator may report readiness but must not approve or merge.
- Missing, malformed, stale, or mismatched provenance requires abstention.
