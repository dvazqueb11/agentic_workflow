#include "calculator.h"

namespace project_boost {

int Calculator::Add(const int left, const int right) const { return left + right; }

int Calculator::Subtract(const int left, const int right) const { return left - right; }

int Calculator::Divide(const int numerator, const int denominator) const {
  if (denominator == 0) {
    throw std::invalid_argument("division by zero");
  }
  return numerator / denominator;
}

}  // namespace project_boost
