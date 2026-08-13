//! Zero-overhead, power-of-two, fixed-capacity ring buffer.

use std::mem::MaybeUninit;

/// Fixed-capacity ring buffer over `N` slots (`N` must be a power of two).
pub struct RingBuffer<T, const N: usize> {
    buf: [MaybeUninit<T>; N],
    head: usize,
    count: usize,
}

impl<T, const N: usize> RingBuffer<T, N> {
    /// Creates an empty ring buffer.
    ///
    /// # Panics
    /// Panics if `N` is zero or not a power of two.
    pub fn new() -> Self {
        assert!(
            N > 0 && (N & (N - 1)) == 0,
            "RingBuffer capacity N must be a power of 2"
        );
        Self {
            // Safety: an array of `MaybeUninit<T>` does not require
            // initialization of the inner `T`, so `assume_init` here only
            // asserts that the *outer* array itself is initialized.
            buf: unsafe { MaybeUninit::uninit().assume_init() },
            head: 0,
            count: 0,
        }
    }

    /// Pushes a value, overwriting the oldest entry once at capacity.
    pub fn push(&mut self, v: T) {
        let idx = (self.head + self.count) & (N - 1);
        if self.count < N {
            self.buf[idx] = MaybeUninit::new(v);
            self.count += 1;
        } else {
            // Safety: `idx` always holds a live, previously-initialized `T`
            // once the buffer is full, so it is valid to drop and replace.
            unsafe {
                let ptr = self.buf[idx].as_mut_ptr();
                std::ptr::drop_in_place(ptr);
                ptr.write(v);
            }
            self.head = (self.head + 1) & (N - 1);
        }
    }

    /// Returns the logical `i`-th element (0 = oldest), or `None` if out of range.
    pub fn get(&self, i: usize) -> Option<&T> {
        if i >= self.count {
            return None;
        }
        let idx = (self.head + i) & (N - 1);
        // Safety: `idx` is within the initialized window [0, count).
        Some(unsafe { &*self.buf[idx].as_ptr() })
    }

    pub fn len(&self) -> usize {
        self.count
    }

    pub fn is_empty(&self) -> bool {
        self.count == 0
    }

    pub fn is_full(&self) -> bool {
        self.count == N
    }

    pub fn capacity(&self) -> usize {
        N
    }
}

impl<T, const N: usize> Default for RingBuffer<T, N> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T, const N: usize> Drop for RingBuffer<T, N> {
    fn drop(&mut self) {
        for i in 0..self.count {
            let idx = (self.head + i) & (N - 1);
            // Safety: every slot within the logical window is initialized.
            unsafe {
                std::ptr::drop_in_place(self.buf[idx].as_mut_ptr());
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn overwrite_semantics() {
        let mut rb: RingBuffer<i32, 4> = RingBuffer::new();
        for v in [10, 20, 30, 40, 50] {
            rb.push(v);
        }
        assert_eq!(rb.len(), 4);
        assert_eq!(rb.get(0), Some(&20));
        assert_eq!(rb.get(3), Some(&50));
    }

    #[test]
    #[should_panic]
    fn rejects_non_power_of_two() {
        let _rb: RingBuffer<i32, 3> = RingBuffer::new();
    }
}
