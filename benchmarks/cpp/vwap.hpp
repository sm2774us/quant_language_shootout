// Rolling VWAP: cumulative notional (price * qty) scan and true VWAP.
#ifndef QUANT_LANG_SHOOTOUT_VWAP_HPP_
#define QUANT_LANG_SHOOTOUT_VWAP_HPP_

#include <cstddef>
#include <span>

namespace quant {

// Writes the running cumulative sum of price[i] * qty[i] into `out`.
// Auto-vectorizes cleanly under -O3 -march=native; no external threading
// runtime (e.g. TBB) is required, keeping the build hermetic in CI.
inline void RollingNotional(std::span<const double> price,
                             std::span<const double> qty,
                             std::span<double> out) noexcept {
  const std::size_t n = price.size();
  double running_sum = 0.0;
  for (std::size_t i = 0; i < n; ++i) {
    running_sum += price[i] * qty[i];
    out[i] = running_sum;
  }
}

// Writes the true rolling VWAP (notional / cumulative quantity) into `out`.
inline void RollingVwap(std::span<const double> price,
                         std::span<const double> qty,
                         std::span<double> out) noexcept {
  const std::size_t n = price.size();
  double running_notional = 0.0;
  double running_qty = 0.0;
  for (std::size_t i = 0; i < n; ++i) {
    running_notional += price[i] * qty[i];
    running_qty += qty[i];
    out[i] = running_notional / running_qty;
  }
}

}  // namespace quant

#endif  // QUANT_LANG_SHOOTOUT_VWAP_HPP_
