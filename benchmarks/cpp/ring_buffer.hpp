// Zero-allocation, cache-line-aligned, power-of-two ring buffer.
#ifndef QUANT_LANG_SHOOTOUT_RING_BUFFER_HPP_
#define QUANT_LANG_SHOOTOUT_RING_BUFFER_HPP_

#include <array>
#include <cassert>
#include <cstddef>

// A fixed 64-byte assumption is used instead of
// std::hardware_destructive_interference_size: the latter is officially
// ABI-unstable across compiler versions/tuning flags (see P0154), which is
// unacceptable for a value baked into a template's memory layout.
constexpr std::size_t kCacheLineSize = 64;

// Fixed-capacity ring buffer. Capacity `N` must be a power of two so that
// index wraparound reduces to a bitwise AND mask instead of a modulo.
template <typename T, std::size_t N>
class RingBuffer {
  static_assert((N != 0) && ((N & (N - 1)) == 0),
                "RingBuffer capacity N must be a power of 2");

 public:
  constexpr RingBuffer() noexcept = default;

  constexpr void Push(const T& value) noexcept {
    const std::size_t idx = (head_ + count_) & (N - 1);
    buf_[idx] = value;
    if (count_ < N) {
      ++count_;
    } else {
      head_ = (head_ + 1) & (N - 1);
    }
  }

  [[nodiscard]] constexpr const T& operator[](std::size_t i) const noexcept {
    assert(i < count_ && "Index out of bounds for active ring buffer window");
    return buf_[(head_ + i) & (N - 1)];
  }

  [[nodiscard]] constexpr std::size_t size() const noexcept { return count_; }
  [[nodiscard]] constexpr std::size_t capacity() const noexcept { return N; }
  [[nodiscard]] constexpr bool empty() const noexcept { return count_ == 0; }
  [[nodiscard]] constexpr bool full() const noexcept { return count_ == N; }

  constexpr void Clear() noexcept {
    head_ = 0;
    count_ = 0;
  }

 private:
  alignas(kCacheLineSize) std::array<T, N> buf_{};
  std::size_t head_ = 0;
  std::size_t count_ = 0;
};

#endif  // QUANT_LANG_SHOOTOUT_RING_BUFFER_HPP_
