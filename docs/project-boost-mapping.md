# Project Boost Mapping for Expansion

This demo starts with one bounded failure family (invalid Conan dependency).

## Next target families for safe expansion

- Missing includes and source files:
  - Detect `fatal error: <header>: No such file or directory`.
  - Remediation: minimal include/source fix plus regression test.
- Linker errors:
  - Detect undefined references.
  - Remediation: bounded CMake target/link fix when evidence is explicit.
- Conan recipe/version/package failures:
  - Detect not-found/incompatible package references.
  - Remediation: minimal dependency correction.
- Unit-test defects:
  - Detect deterministic failing tests with clear root cause.
  - Remediation: smallest code fix plus test.
- Coverity C/C++ defects:
  - Detect bounded high-confidence findings.
  - Remediation: narrow, test-covered change.

## Conditions that should remain diagnosis/escalation early on

- Runner, NFS, LSF, permission, queue, disk, and capacity failures.
- External system outages or flaky connectivity.
- Any credentials/authentication/signing problems.

These categories should default to abstention until dedicated controls and evidence quality are proven in production.
