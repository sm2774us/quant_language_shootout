//! Monte Carlo GBM terminal price simulation (portable CPU implementation).
//!
//! A GPU-kernel variant with identical math is documented in
//! COMPARISON.md section 2.6; this CPU path is what CI builds/runs so the
//! pipeline stays green on runners without CUDA hardware.

use rand::SeedableRng;
use rand_distr::{Distribution, Normal};

/// Simulates `n_paths` independent GBM trajectories of `n_steps` each and
/// returns the terminal price for every path.
///
/// `S_{t+1} = S_t * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)`, `Z ~ N(0,1)`
pub fn mc_terminal_prices(
    s0: f64,
    mu: f64,
    sigma: f64,
    dt: f64,
    n_steps: u32,
    n_paths: u32,
    seed: u64,
) -> Vec<f64> {
    let drift = (mu - 0.5 * sigma * sigma) * dt;
    let vol = sigma * dt.sqrt();
    let normal = Normal::new(0.0_f64, 1.0).expect("valid standard normal parameters");

    let mut rng = rand::rngs::StdRng::seed_from_u64(seed);
    let mut out = Vec::with_capacity(n_paths as usize);

    for _ in 0..n_paths {
        let mut log_s = s0.ln();
        for _ in 0..n_steps {
            log_s += drift + vol * normal.sample(&mut rng);
        }
        out.push(log_s.exp());
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn produces_positive_correctly_sized_output() {
        let prices = mc_terminal_prices(100.0, 0.05, 0.20, 1.0 / 252.0, 252, 1_000, 12345);
        assert_eq!(prices.len(), 1_000);
        assert!(prices.iter().all(|&p| p > 0.0));
    }
}
