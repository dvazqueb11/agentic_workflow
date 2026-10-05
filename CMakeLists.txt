cmake_minimum_required(VERSION 3.20)
project(project_boost_self_healing_ci LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(PROJECT_BOOST_ENABLE_COVERAGE "Build with line coverage instrumentation." OFF)

if(PROJECT_BOOST_ENABLE_COVERAGE)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-O0 -g --coverage)
    add_link_options(--coverage)
  else()
    message(FATAL_ERROR "Coverage instrumentation requires GCC or Clang.")
  endif()
endif()

enable_testing()

add_library(project_boost_core
  src/calculator.cpp
  src/risk_classifier.cpp
  src/performance_demo.cpp
)
target_include_directories(project_boost_core PUBLIC include)

find_package(GTest REQUIRED)

add_executable(project_boost_tests
  tests/calculator_test.cpp
  tests/risk_classifier_test.cpp
  tests/performance_demo_test.cpp
)
target_link_libraries(project_boost_tests PRIVATE project_boost_core GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(project_boost_tests)

add_executable(project_boost_perf tests/performance_budget_test.cpp)
target_link_libraries(project_boost_perf PRIVATE project_boost_core)

add_test(
  NAME project_boost_performance_budget_probe
  COMMAND project_boost_perf
    --output-json ${CMAKE_BINARY_DIR}/performance-results.json
)
