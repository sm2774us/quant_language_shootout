// EWMA variance recurrence: sigma^2_t = lambda*sigma^2_{t-1} + (1-lambda)*r_t^2
#ifndef QUANT_LANG_SHOOTOUT_EWMA_HPP_
#define QUANT_LANG_SHOOTOUT_EWMA_HPP_

#include <cstddef>
#include <span>

namespace quant {

// The recurrence has a strict loop-carried dependency (V_t depends on
// V_{t-1}), so full vectorization is not mathematically possible; the
// squaring of each return, however, is independent and auto-vectorizes.
inline void EwmaVol(std::span<const double> ret, double lambda,
                     std::span<double> out) noexcept {
  const std::size_t n = ret.size();
  if (n == 0) {
    return;
  }
  const double one_minus_lambda = 1.0 - lambda;
  double prev_var = ret[0] * ret[0];
  out[0] = prev_var;
  for (std::size_t i = 1; i < n; ++i) {
    const double r_sq = ret[i] * ret[i];
    prev_var = lambda * prev_var + one_minus_lambda * r_sq;
    out[i] = prev_var;
  }
}

}  // namespace quant

#endif  // QUANT_LANG_SHOOTOUT_EWMA_HPP_
