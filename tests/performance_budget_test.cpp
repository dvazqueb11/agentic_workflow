#include "performance_demo.h"

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

#if defined(__linux__)
#include <sys/resource.h>
#endif

namespace {

struct SampleMetrics {
  double wall_ms;
  double cpu_ms;
  long peak_rss_kb;
};

double Median(std::vector<double> values) {
  if (values.empty()) {
    return 0.0;
  }
  std::sort(values.begin(), values.end());
  const std::size_t midpoint = values.size() / 2;
  if ((values.size() % 2U) == 0U) {
    return (values[midpoint - 1] + values[midpoint]) / 2.0;
  }
  return values[midpoint];
}

long ReadPeakRssKb() {
#if defined(__linux__)
  struct rusage usage {};
  if (getrusage(RUSAGE_SELF, &usage) != 0) {
    return -1;
  }
  return usage.ru_maxrss;
#else
  return -1;
#endif
}

SampleMetrics RunSample(
    const std::vector<std::string>& left,
    const std::vector<std::string>& right,
    int loops_per_sample) {
  const auto wall_start = std::chrono::steady_clock::now();
  const std::clock_t cpu_start = std::clock();

  std::size_t guard = 0;
  for (int i = 0; i < loops_per_sample; ++i) {
    guard += project_boost::CountUniqueCommonTokens(left, right);
  }

  const std::clock_t cpu_end = std::clock();
  const auto wall_end = std::chrono::steady_clock::now();

  if (guard == 0) {
    std::cerr << "Unexpected benchmark guard state.\n";
    std::exit(2);
  }

  const std::chrono::duration<double, std::milli> wall_duration = wall_end - wall_start;
  const double cpu_ms =
      static_cast<double>(cpu_end - cpu_start) * 1000.0 / static_cast<double>(CLOCKS_PER_SEC);
  SampleMetrics metrics{};
  metrics.wall_ms = wall_duration.count();
  metrics.cpu_ms = cpu_ms;
  metrics.peak_rss_kb = ReadPeakRssKb();
  return metrics;
}

std::string BuildJson(
    const std::vector<double>& runtime_samples,
    const std::vector<double>& cpu_samples,
    const std::vector<long>& rss_samples,
    const int warmup_samples,
    const int measured_samples,
    const int loops_per_sample) {
  std::ostringstream out;
  out << std::fixed << std::setprecision(3);
  out << "{\n";
  out << "  \"test_name\": \"common_tokens_budget\",\n";
  out << "  \"warmup_samples\": " << warmup_samples << ",\n";
  out << "  \"measured_samples\": " << measured_samples << ",\n";
  out << "  \"loops_per_sample\": " << loops_per_sample << ",\n";
  out << "  \"runner\": {\n";
  out << "    \"os\": \"" << (std::getenv("RUNNER_OS") ? std::getenv("RUNNER_OS") : "unknown")
      << "\",\n";
  out << "    \"arch\": \"" << (std::getenv("RUNNER_ARCH") ? std::getenv("RUNNER_ARCH") : "unknown")
      << "\"\n";
  out << "  },\n";

  out << "  \"runtime_ms\": {\n";
  out << "    \"samples\": [";
  for (std::size_t i = 0; i < runtime_samples.size(); ++i) {
    out << runtime_samples[i];
    if (i + 1 < runtime_samples.size()) {
      out << ", ";
    }
  }
  out << "],\n";
  out << "    \"median\": " << Median(runtime_samples) << "\n";
  out << "  },\n";

  out << "  \"cpu_time_ms\": {\n";
  out << "    \"samples\": [";
  for (std::size_t i = 0; i < cpu_samples.size(); ++i) {
    out << cpu_samples[i];
    if (i + 1 < cpu_samples.size()) {
      out << ", ";
    }
  }
  out << "],\n";
  out << "    \"median\": " << Median(cpu_samples) << "\n";
  out << "  },\n";

  long max_rss = -1;
  if (!rss_samples.empty()) {
    max_rss = *std::max_element(rss_samples.begin(), rss_samples.end());
  }

  out << "  \"peak_rss_kb\": {\n";
  out << "    \"samples\": [";
  for (std::size_t i = 0; i < rss_samples.size(); ++i) {
    out << rss_samples[i];
    if (i + 1 < rss_samples.size()) {
      out << ", ";
    }
  }
  out << "],\n";
  out << "    \"max\": " << max_rss << "\n";
  out << "  }\n";
  out << "}\n";
  return out.str();
}

std::vector<std::string> BuildTokens(const std::string& prefix, const int count, const int modulo) {
  std::vector<std::string> values;
  values.reserve(static_cast<std::size_t>(count));
  for (int i = 0; i < count; ++i) {
    values.push_back(prefix + "-" + std::to_string(i % modulo));
  }
  return values;
}

}  // namespace

int main(int argc, char** argv) {
  std::string output_path = "performance-results.json";
  for (int i = 1; i < argc; ++i) {
    const std::string current = argv[i];
    if (current == "--output-json" && i + 1 < argc) {
      output_path = argv[++i];
    }
  }

  const int warmup_samples = 2;
  const int measured_samples = 7;
  const int loops_per_sample = 20;

  const std::vector<std::string> left = BuildTokens("left", 7000, 4500);
  const std::vector<std::string> right = BuildTokens("left", 7000, 4700);

  for (int i = 0; i < warmup_samples; ++i) {
    (void)RunSample(left, right, loops_per_sample / 2);
  }

  std::vector<double> runtime_samples;
  runtime_samples.reserve(static_cast<std::size_t>(measured_samples));
  std::vector<double> cpu_samples;
  cpu_samples.reserve(static_cast<std::size_t>(measured_samples));
  std::vector<long> rss_samples;
  rss_samples.reserve(static_cast<std::size_t>(measured_samples));

  for (int i = 0; i < measured_samples; ++i) {
    const SampleMetrics sample = RunSample(left, right, loops_per_sample);
    runtime_samples.push_back(sample.wall_ms);
    cpu_samples.push_back(sample.cpu_ms);
    rss_samples.push_back(sample.peak_rss_kb);
  }

  std::ofstream out(output_path, std::ios::binary | std::ios::trunc);
  if (!out.is_open()) {
    std::cerr << "Unable to open output file: " << output_path << "\n";
    return 1;
  }
  out << BuildJson(
      runtime_samples,
      cpu_samples,
      rss_samples,
      warmup_samples,
      measured_samples,
      loops_per_sample);
  out.close();

  return 0;
}
