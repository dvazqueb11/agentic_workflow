#include "performance_demo.h"

#include <unordered_set>

namespace project_boost {

std::size_t CountUniqueCommonTokensSlow(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right) {
  std::unordered_set<std::string> deduplicated_matches;
  for (const std::string& left_token : left) {
    for (const std::string& right_token : right) {
      if (left_token == right_token) {
        deduplicated_matches.insert(left_token);
      }
    }
  }
  return deduplicated_matches.size();
}

std::size_t CountUniqueCommonTokensFast(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right) {
  std::unordered_set<std::string> right_lookup(right.begin(), right.end());
  std::unordered_set<std::string> unique_matches;
  for (const std::string& left_token : left) {
    if (right_lookup.find(left_token) != right_lookup.end()) {
      unique_matches.insert(left_token);
    }
  }
  return unique_matches.size();
}

std::size_t CountUniqueCommonTokens(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right) {
  return CountUniqueCommonTokensSlow(left, right);
}

}  // namespace project_boost
