# project-boost-self-healing-ci

## What this demo is

This repository demonstrates a GitHub-native self-healing CI pattern:

1. A normal CI run fails due to a deliberately introduced Conan dependency defect.
2. A GitHub Agentic Workflow investigates the run context and evidence.
3. If policy permits, it proposes the smallest fix as a pull request.
4. The same unchanged CI checks validate that healing pull request.
5. Human approval is required before merge.

## Why a pull request instead of direct default-branch changes

The pull-request model preserves branch protections, produces reviewable audit trails, and enforces explicit developer approval before production code changes.

## Deterministic vs contextual components

- Deterministic GitHub Actions:
  - `.github/workflows/ci.yml`
  - `.github/workflows/healing-pr-validation.yml`
- Contextual agent reasoning:
  - `.github/workflows/self-heal.md`

## Prerequisites

- GitHub repository with Actions enabled.
- C++17 toolchain.
- CMake 3.20+.
- Conan 2.x.
- Python 3.11+.
- GitHub CLI (`gh`) authenticated to the target repository.
- Access to GitHub Copilot Agentic Workflows (public preview eligibility may apply).

## Build and test locally

```bash
make ci
```

This executes:

- `conan profile detect --force`
- `conan install . --output-folder=build --build=missing -s build_type=Release`
- `cmake --preset conan-release`
- `cmake --build --preset conan-release`
- `ctest --preset conan-release --output-on-failure --no-tests=error --output-junit build/ctest-results.xml`
- `python3 tests/policy/run_policy_tests.py --output build/policy-test-results.json`

## Compile the agentic Markdown workflow with `gh-aw`

Install and compile with official commands (check latest docs before use):

```bash
gh extension install github/gh-aw
gh aw compile .github/workflows/self-heal.md
```

The compiler writes `.github/workflows/self-heal.lock.yml` automatically.

If compilation cannot run in your environment, keep `.github/workflows/self-heal.md` and document the blocked compilation step. Do not fabricate lock output.

## Configure Copilot access

1. Ensure your organization/repository has Copilot features enabled for agentic workflows.
2. Confirm workflow permissions follow least-privilege defaults.
3. Confirm reviewers/CODEOWNERS are configured.

## Trigger the broken scenario

1. Create a demo branch from `main`.
2. Edit `conanfile.py` and set:
   - from `requires = "gtest/1.14.0"`
   - to `requires = "gtest/99.99.99"`
3. Open a pull request.
4. Observe `CI` failure in the dependency installation step.

## Run healing workflow

- Automatic path: `self-heal` starts when `CI` fails.
- Manual path: run `workflow_dispatch` and provide run ID or pull-request number.

## Review and approve healing PR

1. Confirm label `agentic-self-heal`.
2. Check PR body includes evidence, classification, confidence, and limitations.
3. Confirm unchanged CI commands passed.
4. Confirm anti-weakening checks passed.
5. Approve with a reviewer other than the PR author.
6. Merge when required checks and approvals pass.

## Public-preview limitations

- Agentic Workflow syntax and `gh-aw` commands can change.
- Availability and quotas depend on GitHub preview/plan settings.
- Branch protection enforcement is repository setting-driven and must be configured manually.
