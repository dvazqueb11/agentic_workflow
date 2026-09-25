cmake_minimum_required(VERSION 3.20)
project(project_boost_self_healing_ci LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

enable_testing()

add_library(project_boost_calculator src/calculator.cpp)
target_include_directories(project_boost_calculator PUBLIC include)

find_package(GTest REQUIRED)

add_executable(project_boost_tests tests/calculator_test.cpp)
target_link_libraries(project_boost_tests PRIVATE project_boost_calculator GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(project_boost_tests)
