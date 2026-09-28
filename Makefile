.PHONY: ci local-build local-test policy-test

ci: local-build local-test policy-test

local-build:
	conan profile detect --force
	conan install . --output-folder=build --build=missing -s build_type=Release
	cmake --preset conan-release
	cmake --build --preset conan-release

local-test:
	ctest --preset conan-release --output-on-failure --no-tests=error --output-junit build/ctest-results.xml

policy-test:
	python3 tests/policy/run_policy_tests.py --output build/policy-test-results.json
