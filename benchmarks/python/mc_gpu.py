"""Vectorized Monte Carlo GBM path simulation.

Runs on CPU via NumPy's vectorized RNG and exp/log kernels so that CI
runners without a CUDA device stay green. A CUDA `RawKernel` variant
(identical math) is documented in COMPARISON.md section 2.6 for
GPU-equipped deployment targets.

S_{t+1} = S_t * exp((mu - 0.5*sigma^2) * dt + sigma * sqrt(dt) * Z), Z ~ N(0, 1)
"""
from __future__ import annotations

import numpy as np


def mc_terminal_prices(
    s0: float,
    mu: float,
    sigma: float,
    dt: float,
    n_steps: int,
    n_paths: int,
    seed: int = 12345,
) -> np.ndarray:
    """Simulates terminal GBM prices for `n_paths` independent trajectories.

    Args:
        s0: Initial spot price.
        mu: Annualized drift.
        sigma: Annualized volatility.
        dt: Time step size (e.g. 1/252 for daily steps).
        n_steps: Number of simulation steps per path.
        n_paths: Number of independent Monte Carlo paths.
        seed: PRNG seed for reproducibility.

    Returns:
        1-D float64 array of length `n_paths` with terminal prices.
    """
    rng = np.random.default_rng(seed)
    drift = (mu - 0.5 * sigma * sigma) * dt
    vol = sigma * np.sqrt(dt)

    log_returns = rng.standard_normal((n_steps, n_paths)) * vol + drift
    cum_log_returns = np.cumsum(log_returns, axis=0)
    return s0 * np.exp(cum_log_returns[-1])
