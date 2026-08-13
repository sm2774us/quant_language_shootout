"""Numba LLVM-JIT compiled EWMA volatility recurrence.

sigma^2_t = lambda * sigma^2_{t-1} + (1 - lambda) * r_t^2
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True, fastmath=True)
def ewma_vol(ret: np.ndarray, lambda_: float) -> np.ndarray:
    """Computes the RiskMetrics-style EWMA variance recurrence.

    Args:
        ret: 1-D array of log returns.
        lambda_: Decay factor in (0, 1); 0.94 is the RiskMetrics default.

    Returns:
        1-D array of the same length holding the running EWMA variance.
    """
    n = ret.shape[0]
    out = np.empty(n, dtype=np.float64)
    if n == 0:
        return out

    one_minus_lambda = 1.0 - lambda_
    prev_var = ret[0] * ret[0]
    out[0] = prev_var

    for i in range(1, n):
        r_sq = ret[i] * ret[i]
        prev_var = lambda_ * prev_var + one_minus_lambda * r_sq
        out[i] = prev_var

    return out
