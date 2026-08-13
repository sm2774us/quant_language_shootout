//! Rolling VWAP: cumulative notional (price * qty) scan and true VWAP.
//!
//! Implemented as a plain sequential scan over stable Rust: LLVM
//! auto-vectorizes the independent `price[i] * qty[i]` multiply under
//! `-O3`/`lto`, while the running-sum carry is an inherent sequential
//! dependency. This avoids any nightly-only SIMD intrinsics, keeping the
//! crate buildable on stable `rustc` in CI.

/// Writes the running cumulative notional (`price[i] * qty[i]`) into `out`.
pub fn rolling_notional(price: &[f64], qty: &[f64], out: &mut [f64]) {
    assert_eq!(price.len(), qty.len(), "price/qty length mismatch");
    assert_eq!(price.len(), out.len(), "output length mismatch");

    let mut running_sum = 0.0_f64;
    for i in 0..price.len() {
        running_sum += price[i] * qty[i];
        out[i] = running_sum;
    }
}

/// Writes the true rolling VWAP (`notional / cumulative quantity`) into `out`.
pub fn rolling_vwap(price: &[f64], qty: &[f64], out: &mut [f64]) {
    assert_eq!(price.len(), qty.len(), "price/qty length mismatch");
    assert_eq!(price.len(), out.len(), "output length mismatch");

    let mut running_notional = 0.0_f64;
    let mut running_qty = 0.0_f64;
    for i in 0..price.len() {
        running_notional += price[i] * qty[i];
        running_qty += qty[i];
        out[i] = running_notional / running_qty;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_manual_accumulation() {
        let px = [100.0, 101.5, 99.0, 102.0, 100.5];
        let qty = [10.0, 20.0, 50.0, 15.0, 30.0];
        let mut out = [0.0; 5];
        rolling_notional(&px, &qty, &mut out);

        let mut expected = 0.0;
        for i in 0..px.len() {
            expected += px[i] * qty[i];
            assert!((out[i] - expected).abs() < 1e-9);
        }
    }
}
