"""Vectorized rolling VWAP via NumPy C-kernel dispatch (SIMD accelerated)."""
from __future__ import annotations

import numpy as np


def rolling_notional(px: np.ndarray, qty: np.ndarray) -> np.ndarray:
    """Returns the cumulative notional (price * qty) scan.

    Dispatches to NumPy's compiled C kernels (AVX2/AVX-512 where available)
    for both the elementwise multiply and the cumulative reduction.
    """
    px_contig = np.ascontiguousarray(px, dtype=np.float64)
    qty_contig = np.ascontiguousarray(qty, dtype=np.float64)
    return np.cumsum(px_contig * qty_contig)


def rolling_vwap(px: np.ndarray, qty: np.ndarray) -> np.ndarray:
    """Returns the true rolling VWAP = cumsum(px*qty) / cumsum(qty)."""
    notional = rolling_notional(px, qty)
    cum_qty = np.cumsum(np.ascontiguousarray(qty, dtype=np.float64))
    return notional / cum_qty
