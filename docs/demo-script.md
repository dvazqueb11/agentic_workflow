# Demo Script

1. Show healthy `main`:
   - Open latest successful CI run for `main`.
2. Open deliberately broken dependency PR:
   - Edit `conanfile.py` and set `requires = "gtest/99.99.99"`.
3. Show genuine CI failure:
   - Navigate to failed `CI` run and open `conan-install.log`.
4. Start or observe self-healing workflow:
   - Automatic from failed `CI`, or manual `workflow_dispatch` using run ID / PR number.
5. Show investigation evidence:
   - Display evidence references in healing report artifact and PR body.
6. Show generated healing PR and regression validation:
   - Confirm `agentic-self-heal` label and validation workflow output.
7. Show unchanged CI succeeding:
   - Same build and test commands pass on healing PR.
8. Show policy and review findings:
   - Review `docs/healing-policy.md` checks and anti-weakening results.
9. Approve as developer:
   - Approver is not the PR author.
10. Explain production path:
   - Start bounded to dependency failures, then expand based on measured evidence.
