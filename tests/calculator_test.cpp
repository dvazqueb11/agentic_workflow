#include "calculator.h"

#include <gtest/gtest.h>

namespace {

TEST(CalculatorTest, AddsValues) {
  const project_boost::Calculator calc;
  EXPECT_EQ(calc.Add(3, 4), 7);
}

TEST(CalculatorTest, SubtractsValues) {
  const project_boost::Calculator calc;
  EXPECT_EQ(calc.Subtract(10, 6), 4);
}

TEST(CalculatorTest, DividesValues) {
  const project_boost::Calculator calc;
  EXPECT_EQ(calc.Divide(20, 5), 4);
}

TEST(CalculatorTest, RejectsDivisionByZero) {
  const project_boost::Calculator calc;
  EXPECT_THROW(calc.Divide(20, 0), std::invalid_argument);
}

}  // namespace
