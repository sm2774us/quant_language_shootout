"""NumPy-backed, zero-allocation-after-init fixed-capacity ring buffer.

Google Python Style Guide compliant. Capacity must be a power of two so
that index wraparound can use a bitwise AND mask instead of the modulo
operator, which is materially faster on the CPython interpreter loop.
"""
from __future__ import annotations

import numpy as np


class RingBuffer:
    """Fixed-capacity, power-of-two ring buffer over a contiguous ndarray."""

    __slots__ = ("_buf", "_head", "_count", "_n")

    def __init__(self, n: int, dtype: type = np.float64) -> None:
        """Initializes the ring buffer.

        Args:
            n: Capacity; must be a positive power of two.
            dtype: NumPy scalar dtype for the backing store.

        Raises:
            ValueError: If `n` is not a positive power of two.
        """
        if n <= 0 or (n & (n - 1)) != 0:
            raise ValueError("RingBuffer capacity n must be a positive power of 2")
        self._buf: np.ndarray = np.zeros(n, dtype=dtype)
        self._head: int = 0
        self._count: int = 0
        self._n: int = n

    def push(self, v: float) -> None:
        """Pushes a value, overwriting the oldest entry once full."""
        idx = (self._head + self._count) & (self._n - 1)
        self._buf[idx] = v
        if self._count < self._n:
            self._count += 1
        else:
            self._head = (self._head + 1) & (self._n - 1)

    def __getitem__(self, i: int) -> float:
        if i < 0 or i >= self._count:
            raise IndexError("RingBuffer index out of range")
        idx = (self._head + i) & (self._n - 1)
        return float(self._buf[idx])

    def __len__(self) -> int:
        return self._count

    @property
    def capacity(self) -> int:
        return self._n

    def clear(self) -> None:
        self._head = 0
        self._count = 0
        self._buf.fill(0)
