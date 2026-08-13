//! Benchmark harness for the Rust leg of the language shootout.
//! Writes results/rust.json for scripts/aggregate_results.py to merge.

use std::fs;
use std::hint::black_box;
use std::path::PathBuf;
use std::time::Instant;

use rand::SeedableRng;
use rand_distr::{Distribution, Normal, Uniform};

use quant_lang_shootout::ewma::ewma_vol;
use quant_lang_shootout::mc_gpu::mc_terminal_prices;
use quant_lang_shootout::ring_buffer::RingBuffer;
use quant_lang_shootout::vwap::rolling_vwap;

fn time_it<F: FnMut()>(mut f: F, iterations: u32) -> f64 {
    let mut best = f64::INFINITY;
    for _ in 0..iterations {
        let start = Instant::now();
        f();
        let elapsed = start.elapsed().as_secs_f64();
        if elapsed < best {
            best = elapsed;
        }
    }
    best
}

fn bench_ring_buffer(n_push: usize) -> f64 {
    let mut rb: RingBuffer<f64, 65536> = RingBuffer::new();
    time_it(
        || {
            for i in 0..n_push {
                rb.push(black_box(i as f64));
            }
            black_box(&rb);
        },
        3,
    )
}

fn bench_vwap(n: usize) -> f64 {
    let mut rng = rand::rngs::StdRng::seed_from_u64(0);
    let normal = Normal::new(0.0_f64, 1.0).unwrap();
    let uniform = Uniform::new(1.0_f64, 100.0);

    let mut px = vec![0.0; n];
    let mut qty = vec![0.0; n];
    let mut level = 100.0;
    for i in 0..n {
        level += normal.sample(&mut rng) * 0.01;
        px[i] = level;
        qty[i] = uniform.sample(&mut rng);
    }
    let mut out = vec![0.0; n];
    time_it(
        || {
            rolling_vwap(&px, &qty, &mut out);
            black_box(&out);
        },
        5,
    )
}

fn bench_ewma(n: usize) -> f64 {
    let mut rng = rand::rngs::StdRng::seed_from_u64(0);
    let normal = Normal::new(0.0_f64, 0.01).unwrap();
    let ret: Vec<f64> = (0..n).map(|_| normal.sample(&mut rng)).collect();
    let mut out = vec![0.0; n];
    time_it(
        || {
            ewma_vol(&ret, 0.94, &mut out);
            black_box(&out);
        },
        5,
    )
}

fn bench_monte_carlo(n_paths: u32, n_steps: u32) -> f64 {
    time_it(
        || {
            let out = mc_terminal_prices(100.0, 0.05, 0.20, 1.0 / 252.0, n_steps, n_paths, 12345);
            black_box(&out);
        },
        3,
    )
}

fn main() {
    let ring_buffer_s = bench_ring_buffer(1_000_000);
    let vwap_s = bench_vwap(1_000_000);
    let ewma_s = bench_ewma(1_000_000);
    let mc_s = bench_monte_carlo(100_000, 252);

    let json = format!(
        "{{\n  \"language\": \"rust\",\n  \"benchmarks\": {{\n    \"ring_buffer_push_1e6\": {ring_buffer_s},\n    \"vwap_1e6\": {vwap_s},\n    \"ewma_1e6\": {ewma_s},\n    \"monte_carlo_gbm_1e5x252\": {mc_s}\n  }}\n}}\n"
    );

    let results_dir: PathBuf = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("results");
    fs::create_dir_all(&results_dir).expect("failed to create results directory");
    fs::write(results_dir.join("rust.json"), &json).expect("failed to write results/rust.json");

    println!(
        "ring_buffer_push_1e6={ring_buffer_s:.6} vwap_1e6={vwap_s:.6} ewma_1e6={ewma_s:.6} mc={mc_s:.6}"
    );
}
