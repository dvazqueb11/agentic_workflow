#ifndef PROJECT_BOOST_CALCULATOR_H
#define PROJECT_BOOST_CALCULATOR_H

#include <stdexcept>

namespace project_boost {

class Calculator {
 public:
  int Add(int left, int right) const;
  int Subtract(int left, int right) const;
  int Divide(int numerator, int denominator) const;
};

}  // namespace project_boost

#endif
