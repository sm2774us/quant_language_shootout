# Orchestrates all four language benchmarks locally and aggregates results.
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path "$RootDir/results" | Out-Null

Write-Host "=== [1/4] Python ==="
if (Get-Command python -ErrorAction SilentlyContinue) {
    Push-Location "$RootDir/benchmarks/python"
    python -m pip install --quiet -e .
    python bench.py
    Pop-Location
} else {
    Write-Host "python not found; skipping."
}

Write-Host "=== [2/4] C++ ==="
if (Get-Command cmake -ErrorAction SilentlyContinue) {
    cmake -S "$RootDir/benchmarks/cpp" -B "$RootDir/benchmarks/cpp/build" -DCMAKE_BUILD_TYPE=Release
    cmake --build "$RootDir/benchmarks/cpp/build" --config Release --parallel
    & "$RootDir/benchmarks/cpp/build/test_benchmarks"
    & "$RootDir/benchmarks/cpp/build/bench_main"
} else {
    Write-Host "cmake not found; skipping."
}

Write-Host "=== [3/4] Rust ==="
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Push-Location "$RootDir/benchmarks/rust"
    cargo test --release --quiet
    cargo run --release --quiet --bin bench
    Pop-Location
} else {
    Write-Host "cargo not found; skipping."
}

Write-Host "=== [4/4] Q (kdb+) ==="
if (Get-Command q -ErrorAction SilentlyContinue) {
    Push-Location "$RootDir/benchmarks/q"
    q bench.q
    Pop-Location
} else {
    Write-Host "q (kdb+) binary not found on PATH; skipping (requires a license)."
}

Write-Host "=== Aggregating results ==="
python "$RootDir/scripts/aggregate_results.py"

Write-Host "Done. See $RootDir/results/combined.csv"
