#!/usr/bin/env bash
# Orchestrates all four language benchmarks locally and aggregates results.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "${ROOT_DIR}/results"

echo "=== [1/4] Python ==="
if command -v python3 >/dev/null 2>&1; then
    pushd "${ROOT_DIR}/benchmarks/python" >/dev/null
    python3 -m pip install --quiet --break-system-packages -e . 2>/dev/null || \
        python3 -m pip install --quiet -e .
    python3 bench.py
    popd >/dev/null
else
    echo "python3 not found; skipping."
fi

echo "=== [2/4] C++ ==="
if command -v cmake >/dev/null 2>&1; then
    cmake -S "${ROOT_DIR}/benchmarks/cpp" -B "${ROOT_DIR}/benchmarks/cpp/build" \
        -DCMAKE_BUILD_TYPE=Release
    cmake --build "${ROOT_DIR}/benchmarks/cpp/build" --parallel
    "${ROOT_DIR}/benchmarks/cpp/build/test_benchmarks"
    "${ROOT_DIR}/benchmarks/cpp/build/bench_main"
else
    echo "cmake not found; skipping."
fi

echo "=== [3/4] Rust ==="
if command -v cargo >/dev/null 2>&1; then
    pushd "${ROOT_DIR}/benchmarks/rust" >/dev/null
    cargo test --release --quiet
    cargo run --release --quiet --bin bench
    popd >/dev/null
else
    echo "cargo not found; skipping."
fi

echo "=== [4/4] Q (kdb+) ==="
if command -v q >/dev/null 2>&1; then
    pushd "${ROOT_DIR}/benchmarks/q" >/dev/null
    q bench.q
    popd >/dev/null
else
    echo "q (kdb+) binary not found on PATH; skipping (requires a license)."
fi

echo "=== Aggregating results ==="
python3 "${ROOT_DIR}/scripts/aggregate_results.py"

echo "Done. See ${ROOT_DIR}/results/combined.csv"
