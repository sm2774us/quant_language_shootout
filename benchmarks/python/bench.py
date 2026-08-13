"""Benchmark harness for the Python leg of the language shootout.

Writes results/python.json with wall-clock timings for each benchmark so
that `scripts/aggregate_results.py` can merge all four languages into a
single comparison CSV.
"""
from __future__ import annotations

import json
import pathlib
import time
from typing import Callable

import numpy as np

from ewma import ewma_vol
from mc_gpu import mc_terminal_prices
from ring_buffer import RingBuffer
from vwap import rolling_vwap

RESULTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "results"


def _time_it(fn: Callable[[], None], iterations: int = 5) -> float:
    """Returns the best-of-`iterations` wall-clock time in seconds."""
    best = float("inf")
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def bench_ring_buffer(n_push: int = 1_000_000) -> float:
    rb = RingBuffer(1 << 16)

    def run() -> None:
        for i in range(n_push):
            rb.push(float(i))

    return _time_it(run, iterations=3)


def bench_vwap(n: int = 1_000_000) -> float:
    rng = np.random.default_rng(0)
    px = 100.0 + rng.standard_normal(n).cumsum() * 0.01
    qty = rng.uniform(1.0, 100.0, size=n)

    def run() -> None:
        rolling_vwap(px, qty)

    return _time_it(run)


def bench_ewma(n: int = 1_000_000) -> float:
    rng = np.random.default_rng(0)
    ret = rng.standard_normal(n) * 0.01
    ewma_vol(ret, 0.94)  # Warm up the Numba JIT before timing.

    def run() -> None:
        ewma_vol(ret, 0.94)

    return _time_it(run)


def bench_mc(n_paths: int = 100_000, n_steps: int = 252) -> float:
    def run() -> None:
        mc_terminal_prices(100.0, 0.05, 0.20, 1.0 / 252.0, n_steps, n_paths)

    return _time_it(run, iterations=3)


def main() -> None:
    results = {
        "language": "python",
        "benchmarks": {
            "ring_buffer_push_1e6": bench_ring_buffer(),
            "vwap_1e6": bench_vwap(),
            "ewma_1e6": bench_ewma(),
            "monte_carlo_gbm_1e5x252": bench_mc(),
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "python.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
