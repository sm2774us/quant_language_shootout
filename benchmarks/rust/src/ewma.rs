//! EWMA variance recurrence: sigma^2_t = lambda*sigma^2_{t-1} + (1-lambda)*r_t^2

/// Computes the RiskMetrics-style EWMA variance recurrence into `out`.
///
/// The recurrence has a strict loop-carried dependency on `prev_var`, so it
/// cannot be fully vectorized; the compiler can still hoist and vectorize
/// the independent squaring of each return.
pub fn ewma_vol(ret: &[f64], lambda: f64, out: &mut [f64]) {
    assert_eq!(ret.len(), out.len(), "input/output length mismatch");
    if ret.is_empty() {
        return;
    }

    let one_minus_lambda = 1.0 - lambda;
    let mut prev_var = ret[0] * ret[0];
    out[0] = prev_var;

    for i in 1..ret.len() {
        let r_sq = ret[i] * ret[i];
        prev_var = lambda * prev_var + one_minus_lambda * r_sq;
        out[i] = prev_var;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_recurrence_definition() {
        let ret = [0.01_f64, -0.015, 0.02, 0.005];
        let lambda = 0.94;
        let mut out = [0.0; 4];
        ewma_vol(&ret, lambda, &mut out);

        let v0 = ret[0] * ret[0];
        assert!((out[0] - v0).abs() < 1e-12);
        let v1 = lambda * v0 + (1.0 - lambda) * ret[1] * ret[1];
        assert!((out[1] - v1).abs() < 1e-12);
    }
}
