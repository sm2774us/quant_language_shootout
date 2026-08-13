"""Correctness tests for the Python benchmark modules (pytest)."""
import numpy as np
import pytest

from ewma import ewma_vol
from mc_gpu import mc_terminal_prices
from ring_buffer import RingBuffer
from vwap import rolling_notional, rolling_vwap


def test_ring_buffer_overwrite() -> None:
    rb = RingBuffer(4)
    for v in (10.0, 20.0, 30.0, 40.0, 50.0):
        rb.push(v)
    assert len(rb) == 4
    assert [rb[i] for i in range(4)] == [20.0, 30.0, 40.0, 50.0]


def test_ring_buffer_rejects_non_power_of_two() -> None:
    with pytest.raises(ValueError):
        RingBuffer(3)


def test_rolling_notional_matches_manual_cumsum() -> None:
    px = np.array([100.0, 101.5, 99.0, 102.0, 100.5])
    qty = np.array([10.0, 20.0, 50.0, 15.0, 30.0])
    expected = np.cumsum(px * qty)
    np.testing.assert_allclose(rolling_notional(px, qty), expected)


def test_rolling_vwap_matches_definition() -> None:
    px = np.array([100.0, 101.5, 99.0, 102.0, 100.5])
    qty = np.array([10.0, 20.0, 50.0, 15.0, 30.0])
    vwap = rolling_vwap(px, qty)
    assert vwap[-1] == pytest.approx(np.sum(px * qty) / np.sum(qty))


def test_ewma_vol_matches_recurrence() -> None:
    ret = np.array([0.01, -0.015, 0.02, 0.005])
    lam = 0.94
    out = ewma_vol(ret, lam)
    expected = ret[0] ** 2
    assert out[0] == pytest.approx(expected)
    expected = lam * expected + (1 - lam) * ret[1] ** 2
    assert out[1] == pytest.approx(expected)


def test_mc_terminal_prices_shape_and_positivity() -> None:
    prices = mc_terminal_prices(100.0, 0.05, 0.20, 1.0 / 252.0, 252, 1_000)
    assert prices.shape == (1_000,)
    assert np.all(prices > 0.0)
