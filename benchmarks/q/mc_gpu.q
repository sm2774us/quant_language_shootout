/ mc_gpu.q — Monte Carlo GBM terminal price simulation (pure-q CPU path).
/ A PyKX/CuPy RawKernel GPU variant with identical math is documented in
/ COMPARISON.md section 2.6. This CPU-only path needs no GPU/PyKX runtime.
/ Requires a licensed kdb+ 4.0 binary; not executed in CI (see benchmark.yml).

mcTerminalPrices:{[s0; mu; sigma; dt; nSteps; nPaths]
    drift: (mu - 0.5 * sigma * sigma) * dt;
    vol: sigma * sqrt dt;
    / nPaths x nSteps matrix of standard normal draws via Box-Muller
    u1: nPaths cut (nPaths * nSteps)?1.0f;
    u2: nPaths cut (nPaths * nSteps)?1.0f;
    z: sqrt[-2f * log u1] * cos[2f * 3.14159265358979 * u2];
    logReturns: drift + vol * z;
    s0 * exp sum each logReturns
 };
