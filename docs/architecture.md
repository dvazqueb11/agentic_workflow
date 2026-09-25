# Architecture

```mermaid
sequenceDiagram
    participant Dev as Developer PR
    participant CI as CI Workflow
    participant FR as Failed Run
    participant SH as Self-Healing Agentic Workflow
    participant HPR as Healing Pull Request
    participant V as Unchanged CI Validation
    participant AR as Automated Review
    participant DA as Developer Approval
    participant M as Merge

    Dev->>CI: Open PR with invalid Conan dependency
    CI->>FR: Build/install fails with evidence logs
    FR->>SH: Trigger self-heal workflow
    SH->>HPR: Create minimal fix PR (agentic-self-heal)
    HPR->>V: Run same CI commands
    V->>AR: Run anti-weakening and policy checks
    AR->>DA: Require non-self approval
    DA->>M: Approve and merge when checks pass
```

## Deterministic vs agentic behavior

- Deterministic GitHub Actions:
  - `.github/workflows/ci.yml`
  - `.github/workflows/healing-pr-validation.yml`
- Contextual agent reasoning:
  - `.github/workflows/self-heal.md` (compiled with `gh-aw`)
