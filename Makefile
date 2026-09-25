.PHONY: ci local-build local-test policy-test

ci: local-build local-test policy-test

local-build:
	conan profile detect --force
	conan install . --output-folder=build --build=missing -s build_type=Release
	cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
	cmake --build build --config Release

local-test:
	ctest --test-dir build --output-on-failure --no-tests=error --output-junit build/ctest-results.xml

policy-test:
	python3 tests/policy/run_policy_tests.py --output build/policy-test-results.json
