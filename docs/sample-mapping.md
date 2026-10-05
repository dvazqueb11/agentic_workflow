# Sample Mapping

## Customer workflow represented by the demo

| Sample concern | Demo representation |
|---|---|
| Monorepo with core, backend, frontend, and agentic components | `affected_modules` in diagnosis handoffs and diff-analysis subagent |
| Selective CI builds | Agent identifies impacted modules before remediation |
| Conan and JFrog dependencies | Reproducible invalid Conan reference scenario |
| Backend and platform regressions | Unchanged CTest and policy validation stages |
| Coverage policy governance | Overall and changed-line coverage gates with machine-readable evidence |
| Performance policy governance | Deterministic runtime/CPU/memory budgets with machine-readable evidence |
| Hosted Coverity | `STATIC_ANALYSIS` policy class and anti-weakening controls |
| LSF farm | Diagnosis-only LSF authorization fixture |
| NFS release artifacts | Diagnosis-only unavailable release-tree fixture |
| Reporting dashboards | Structured JSON/Markdown artifacts and GitHub run summaries |
| JIRA integration | Future safe-output integration; not connected in this simulation |
| sample-db database access | Future read-only MCP integration; not connected in this simulation |

## Safe expansion targets

- Missing includes and source files:
  - Detect explicit compiler evidence.
  - Remediate with a minimal include/source fix and regression coverage.
- Linker errors:
  - Detect bounded undefined references.
  - Remediate only when the target/link relationship is explicit.
- Conan recipe, version, and package failures:
  - Distinguish invalid references from registry access or outages.
  - Remediate only invalid repository-owned configuration.
- Unit-test defects:
  - Require deterministic reproduction and a source-level root cause.
  - Make the smallest code fix and preserve or improve coverage.
- Coverity C/C++ defects:
  - Start with bounded high-confidence findings.
  - Require test-covered fixes and unchanged analysis configuration.
- Read-only sample-db/Sample metadata:
  - Add a separately governed MCP server with allowlisted queries.
  - Keep credentials out of the agent and all writes disabled.

## Conditions that remain diagnosis-only

- Runner, disk, queue, and capacity failures.
- NFS or shared-storage failures.
- LSF permissions, farm tags, and scheduler availability.
- Credentials, signing, authentication, and private registry access.
- JFrog, Coverity, JIRA, sample-db, and other external-system outages.
- Ambiguous failures without sufficient evidence.

These conditions produce an escalation artifact and recommended owner. They never trigger a code-remediation agent.
