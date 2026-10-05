#ifndef PROJECT_BOOST_PERFORMANCE_DEMO_H
#define PROJECT_BOOST_PERFORMANCE_DEMO_H

#include <string>
#include <vector>

namespace project_boost {

std::size_t CountUniqueCommonTokensSlow(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right);

std::size_t CountUniqueCommonTokensFast(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right);

std::size_t CountUniqueCommonTokens(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right);

}  // namespace project_boost

#endif
