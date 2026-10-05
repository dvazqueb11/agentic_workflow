.PHONY: ci local-build local-test coverage-gate performance-gate policy-test

ci: local-build local-test coverage-gate performance-gate policy-test

local-build:
	conan profile detect --force
	conan install . --output-folder=build --build=missing -s build_type=Debug
	cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Debug -DPROJECT_BOOST_ENABLE_COVERAGE=ON
	cmake --build build --config Debug

local-test:
	ctest --test-dir build --output-on-failure --no-tests=error --output-junit build/ctest-results.xml

coverage-gate:
	gcovr --root . --object-directory build --filter '^.*/(src|include)/' --json build/coverage/coverage.json --xml-pretty build/coverage/cobertura.xml --txt build/coverage/summary.txt
	python3 scripts/evaluate_coverage.py --coverage-json build/coverage/coverage.json --gates-config config/quality-gates.json --report-output build/coverage/coverage-gate.json

performance-gate:
	ctest --test-dir build -R project_boost_performance_budget_probe --output-on-failure
	cp build/performance-results.json build/performance/performance-results.json
	python3 scripts/evaluate_performance.py --results-json build/performance/performance-results.json --gates-config config/quality-gates.json --report-output build/performance/performance-gate.json

policy-test:
	python3 tests/policy/run_policy_tests.py --output build/policy-test-results.json
