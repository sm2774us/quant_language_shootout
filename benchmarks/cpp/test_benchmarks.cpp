// Lightweight, dependency-free correctness tests (no external test
// framework required, keeping the CI build hermetic).
#include <cassert>
#include <cmath>
#include <cstdio>
#include <vector>

#include "ewma.hpp"
#include "mc_gpu.hpp"
#include "ring_buffer.hpp"
#include "vwap.hpp"

namespace {

void TestRingBufferOverwrite() {
  RingBuffer<double, 4> rb;
  for (double v : {10.0, 20.0, 30.0, 40.0, 50.0}) {
    rb.Push(v);
  }
  assert(rb.size() == 4);
  assert(rb[0] == 20.0);
  assert(rb[1] == 30.0);
  assert(rb[2] == 40.0);
  assert(rb[3] == 50.0);
  std::puts("[PASS] RingBuffer overwrite semantics");
}

void TestVwap() {
  const std::vector<double> px = {100.0, 101.5, 99.0, 102.0, 100.5};
  const std::vector<double> qty = {10.0, 20.0, 50.0, 15.0, 30.0};
  std::vector<double> out(px.size());
  quant::RollingNotional(px, qty, out);

  double expected = 0.0;
  for (std::size_t i = 0; i < px.size(); ++i) {
    expected += px[i] * qty[i];
    assert(std::abs(out[i] - expected) < 1e-9);
  }
  std::puts("[PASS] RollingNotional matches manual accumulation");
}

void TestEwma() {
  const std::vector<double> ret = {0.01, -0.015, 0.02, 0.005};
  const double lambda = 0.94;
  std::vector<double> out(ret.size());
  quant::EwmaVol(ret, lambda, out);

  const double v0 = ret[0] * ret[0];
  assert(std::abs(out[0] - v0) < 1e-12);
  [[maybe_unused]] const double v1 =
      lambda * v0 + (1.0 - lambda) * ret[1] * ret[1];
  assert(std::abs(out[1] - v1) < 1e-12);
  std::puts("[PASS] EwmaVol matches recurrence definition");
}

void TestMonteCarloPositivity() {
  const auto prices =
      quant::McTerminalPrices(100.0, 0.05, 0.20, 1.0 / 252.0, 252, 1000);
  assert(prices.size() == 1000);
  for ([[maybe_unused]] double p : prices) {
    assert(p > 0.0);
  }
  std::puts("[PASS] McTerminalPrices produces positive, correctly-sized output");
}

}  // namespace

int main() {
  TestRingBufferOverwrite();
  TestVwap();
  TestEwma();
  TestMonteCarloPositivity();
  std::puts("All C++ tests passed.");
  return 0;
}
