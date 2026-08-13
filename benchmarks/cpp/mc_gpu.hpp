// Monte Carlo GBM terminal price simulation (portable CPU implementation).
// A CUDA kernel variant with identical math is documented in
// COMPARISON.md section 2.6 for GPU-equipped deployment targets; the CPU
// path here is what CI actually builds and runs, guaranteeing a
// hardware-independent green build.
#ifndef QUANT_LANG_SHOOTOUT_MC_GPU_HPP_
#define QUANT_LANG_SHOOTOUT_MC_GPU_HPP_

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <random>
#include <vector>

namespace quant {

// Simulates `n_paths` independent GBM trajectories of `n_steps` each and
// returns the terminal price for every path.
// S_{t+1} = S_t * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z), Z ~ N(0,1)
inline std::vector<double> McTerminalPrices(double s0, double mu,
                                             double sigma, double dt,
                                             int n_steps, int n_paths,
                                             std::uint64_t seed = 12345) {
  std::vector<double> out(static_cast<std::size_t>(n_paths));
  const double drift = (mu - 0.5 * sigma * sigma) * dt;
  const double vol = sigma * std::sqrt(dt);

  std::mt19937_64 rng(seed);
  std::normal_distribution<double> normal(0.0, 1.0);

  for (int p = 0; p < n_paths; ++p) {
    double log_s = std::log(s0);
    for (int t = 0; t < n_steps; ++t) {
      log_s += drift + vol * normal(rng);
    }
    out[static_cast<std::size_t>(p)] = std::exp(log_s);
  }
  return out;
}

}  // namespace quant

#endif  // QUANT_LANG_SHOOTOUT_MC_GPU_HPP_
