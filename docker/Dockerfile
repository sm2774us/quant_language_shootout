# Multi-stage image: Python + gcc-14 + rustc, running the full benchmark
# suite reproducibly. Q/kdb+ is intentionally excluded — it requires a
# licensed binary that cannot be redistributed in a public image.

FROM ubuntu:24.04 AS toolchain

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        gcc-14 g++-14 \
        curl \
        ca-certificates \
        python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-14 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-14 100

# Install Rust (stable) via rustup.
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal

WORKDIR /app
COPY . .

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        -e benchmarks/python -e benchmarks/python[dev]

RUN cmake -S benchmarks/cpp -B benchmarks/cpp/build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build benchmarks/cpp/build --parallel

RUN cd benchmarks/rust && cargo build --release

RUN chmod +x scripts/run_all.sh

ENTRYPOINT ["bash", "-c", "scripts/run_all.sh && python3 report/generate_report.py"]
