/ vwap.q — Rolling notional / VWAP via primitive composition.
/ Requires a licensed kdb+ 4.0 binary; not executed in CI (see benchmark.yml).

rollingNotional:{[px; qty]
    sums px * qty
 };

rollingVwap:{[px; qty]
    rollingNotional[px; qty] % sums qty
 };
