# quant-lang-shootout

Systematic-trading-grade language shootout — **Python 3.12+ · C++20/26 · Q
(kdb+ 4.0) · Rust (stable)** — comparing identical algorithms (ring buffer,
rolling VWAP, EWMA volatility, Monte Carlo GBM) across all four languages so
timing deltas are attributable to language/runtime, not algorithmic drift.

Full internals comparison, syntax matrices, and use-case guidance:
**[COMPARISON.md](./COMPARISON.md)**.

## Project layout

```
quant-lang-shootout/
├── README.md
├── COMPARISON.md
├── LICENSE
├── .github/workflows/benchmark.yml   # CI: build + test + bench + report
├── benchmarks/
│   ├── python/   # pyproject.toml, ring_buffer.py, vwap.py, ewma.py, mc_gpu.py, bench.py
│   ├── cpp/      # CMakeLists.txt, ring_buffer.hpp, vwap.hpp, ewma.hpp, mc_gpu.hpp, bench_main.cpp
│   ├── rust/     # Cargo.toml, src/{ring_buffer,vwap,ewma,mc_gpu,bench,lib}.rs
│   └── q/        # ring_buffer.q, vwap.q, ewma.q, mc_gpu.q, bench.q (requires licensed kdb+)
├── scripts/
│   ├── run_all.sh
│   ├── run_all.ps1
│   └── aggregate_results.py
├── report/
│   └── generate_report.py            # Plotly dark-theme HTML tearsheet
├── docker/
│   └── Dockerfile
└── results/                          # gitignored locally; CI artifacts land here
```

## Quick start

### Local (bare metal)

```bash
./scripts/run_all.sh              # runs every available benchmark, writes results/*.json
python report/generate_report.py  # builds results/report.html
```

Windows: `./scripts/run_all.ps1`.

### Docker (reproducible; Python + C++ + Rust — Q excluded, needs a licensed binary)

```bash
docker build -t quant-lang-shootout -f docker/Dockerfile .
docker run --rm -v "$(pwd)/results:/app/results" quant-lang-shootout
```

### GitHub Actions

Push to `main`, open a PR, or trigger manually from the Actions tab
("Language Shootout Benchmark" → *Run workflow*). A nightly cron run is
also configured. Download the `benchmark-report` artifact
(`report.html` + `combined.csv`) from the completed run.

## Design notes

- **Portability over exotic intrinsics.** The C++ and Rust code intentionally
  avoids `std::execution::par_unseq` / `std::experimental::simd` and nightly
  `#![feature(portable_simd)]` / heavy `rayon` fan-out present in the
  exploratory snippets in `COMPARISON.md`. Production CI runners don't
  reliably ship TBB or nightly Rust, so the benchmark implementations here
  use straight-line, auto-vectorization-friendly loops under `-O3` /
  `lto = true` instead — same asymptotic complexity, hermetic build.
- **GPU Monte Carlo.** `mc_gpu.{py,hpp,rs,q}` implement the CPU-portable GBM
  path-simulation math so CI stays green without CUDA hardware. The CUDA
  `RawKernel` / GPU variant with identical math is documented in
  `COMPARISON.md` §2.6 for GPU-equipped deployment targets.
- **Q/kdb+.** Requires a commercially licensed binary that cannot be
  provisioned on public GitHub-hosted runners, so `benchmarks/q/` is built
  and reviewed as source but not executed in CI (see the `q_lint` job in
  `.github/workflows/benchmark.yml`). Run it locally or on a self-hosted
  runner with a valid license via `q benchmarks/q/bench.q`.

## License

MIT — see [LICENSE](./LICENSE).
