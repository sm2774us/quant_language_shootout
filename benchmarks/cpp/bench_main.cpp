// Benchmark harness for the C++ leg of the language shootout.
// Writes results/cpp.json for scripts/aggregate_results.py to merge.
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <functional>
#include <limits>
#include <random>
#include <vector>

#include "ewma.hpp"
#include "mc_gpu.hpp"
#include "ring_buffer.hpp"
#include "vwap.hpp"

namespace {

namespace fs = std::filesystem;

// Prevents the optimizer from proving a value is dead and eliding the very
// work being measured (analogous to Rust's std::hint::black_box).
template <typename T>
void DoNotOptimize(const T& value) {
  asm volatile("" : : "g"(value) : "memory");
}

double TimeIt(const std::function<void()>& fn, int iterations = 5) {
  double best = std::numeric_limits<double>::infinity();
  for (int i = 0; i < iterations; ++i) {
    const auto start = std::chrono::steady_clock::now();
    fn();
    const auto end = std::chrono::steady_clock::now();
    const double elapsed = std::chrono::duration<double>(end - start).count();
    best = std::min(best, elapsed);
  }
  return best;
}

double BenchRingBuffer(int n_push = 1'000'000) {
  static RingBuffer<double, 1 << 16> rb;
  return TimeIt(
      [&] {
        for (int i = 0; i < n_push; ++i) {
          rb.Push(static_cast<double>(i));
        }
        DoNotOptimize(rb);
      },
      3);
}

double BenchVwap(std::size_t n = 1'000'000) {
  std::mt19937_64 rng(0);
  std::normal_distribution<double> normal(0.0, 1.0);
  std::uniform_real_distribution<double> uniform(1.0, 100.0);

  std::vector<double> px(n), qty(n), out(n);
  double level = 100.0;
  for (std::size_t i = 0; i < n; ++i) {
    level += normal(rng) * 0.01;
    px[i] = level;
    qty[i] = uniform(rng);
  }

  return TimeIt([&] {
    quant::RollingVwap(px, qty, out);
    DoNotOptimize(out);
  });
}

double BenchEwma(std::size_t n = 1'000'000) {
  std::mt19937_64 rng(0);
  std::normal_distribution<double> normal(0.0, 0.01);
  std::vector<double> ret(n), out(n);
  for (std::size_t i = 0; i < n; ++i) {
    ret[i] = normal(rng);
  }
  return TimeIt([&] {
    quant::EwmaVol(ret, 0.94, out);
    DoNotOptimize(out);
  });
}

double BenchMonteCarlo(int n_paths = 100'000, int n_steps = 252) {
  return TimeIt(
      [&] {
        auto out = quant::McTerminalPrices(100.0, 0.05, 0.20, 1.0 / 252.0,
                                            n_steps, n_paths);
        DoNotOptimize(out);
      },
      3);
}

}  // namespace

int main() {
  const double ring_buffer_s = BenchRingBuffer();
  const double vwap_s = BenchVwap();
  const double ewma_s = BenchEwma();
  const double mc_s = BenchMonteCarlo();

  const fs::path results_dir =
      fs::path(__FILE__).parent_path().parent_path().parent_path() /
      "results";
  fs::create_directories(results_dir);

  std::ofstream out(results_dir / "cpp.json");
  out << "{\n"
      << "  \"language\": \"cpp\",\n"
      << "  \"benchmarks\": {\n"
      << "    \"ring_buffer_push_1e6\": " << ring_buffer_s << ",\n"
      << "    \"vwap_1e6\": " << vwap_s << ",\n"
      << "    \"ewma_1e6\": " << ewma_s << ",\n"
      << "    \"monte_carlo_gbm_1e5x252\": " << mc_s << "\n"
      << "  }\n"
      << "}\n";

  std::printf("ring_buffer_push_1e6=%.6f vwap_1e6=%.6f ewma_1e6=%.6f mc=%.6f\n",
              ring_buffer_s, vwap_s, ewma_s, mc_s);
  return 0;
}
