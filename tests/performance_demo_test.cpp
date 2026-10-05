#include "performance_demo.h"

#include <gtest/gtest.h>

namespace {

TEST(PerformanceDemoTest, SlowAndFastImplementationsMatch) {
  const std::vector<std::string> left = {
      "azure", "copilot", "agent", "ci", "coverage", "azure", "policy"};
  const std::vector<std::string> right = {
      "policy", "runtime", "azure", "ci", "agent", "agent"};

  const std::size_t slow =
      project_boost::CountUniqueCommonTokensSlow(left, right);
  const std::size_t fast =
      project_boost::CountUniqueCommonTokensFast(left, right);
  const std::size_t selected = project_boost::CountUniqueCommonTokens(left, right);

  EXPECT_EQ(slow, 4U);
  EXPECT_EQ(fast, slow);
  EXPECT_EQ(selected, slow);
}

TEST(PerformanceDemoTest, HandlesNoOverlap) {
  const std::vector<std::string> left = {"alpha", "beta"};
  const std::vector<std::string> right = {"gamma", "delta"};
  EXPECT_EQ(project_boost::CountUniqueCommonTokens(left, right), 0U);
}

}  // namespace
