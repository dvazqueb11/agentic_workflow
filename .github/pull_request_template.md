## Healing PR Summary

### Failed workflow and job
- Workflow:
- Job:
- Failed run URL:

### Failure classification
- One of: BUILD_DEPENDENCY / SOURCE_COMPILE / UNIT_TEST / STATIC_ANALYSIS / RUNNER_OR_EXTERNAL_SYSTEM / UNKNOWN

### Likely root cause

### Exact supporting evidence
- Log excerpt or artifact references:

### Files changed

### Why this change is minimal

### Tests added or updated

### Validation executed
- `conan profile detect --force`
- `conan install . --output-folder=build --build=missing -s build_type=Release`
- `cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release`
- `cmake --build build --config Release`
- `ctest --test-dir build --output-on-failure --no-tests=error --output-junit build/ctest-results.xml`
- `python3 tests/policy/run_policy_tests.py --output build/policy-test-results.json`

### Confidence

### Limitations

### Human approval requirement
- [ ] I confirm this PR requires explicit human approval before merge.
