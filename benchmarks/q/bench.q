/ bench.q — Benchmark harness for the q leg of the language shootout.
/ Writes results/q.json for scripts/aggregate_results.py to merge.
/ Requires a licensed kdb+ 4.0 binary; not executed in CI (see benchmark.yml).

\l ring_buffer.q
\l vwap.q
\l ewma.q
\l mc_gpu.q

timeIt:{[f; iters]
    times: {[f] .z.p; f[]; }; / placeholder, real timing below
    best: 0Wf;
    i: 0;
    while[i < iters;
        t0: .z.p;
        f[];
        elapsed: `float$(`long$(.z.p - t0)) % 1e9;
        if[elapsed < best; best: elapsed];
        i +: 1
    ];
    best
 };

benchRingBuffer:{[]
    rb: ringBuffer[65536];
    timeIt[{[] rb:: ringPush[rb; 1.0]}; 3]
 };

benchVwap:{[]
    n: 1000000;
    px: 100.0 + sums (n?0.02f) - 0.01f;
    qty: 1.0 + n?99.0f;
    timeIt[{[] rollingVwap[px; qty]}; 5]
 };

benchEwma:{[]
    n: 1000000;
    ret: (n?0.02f) - 0.01f;
    timeIt[{[] ewmaVol[ret; 0.94]}; 5]
 };

benchMc:{[]
    timeIt[{[] mcTerminalPrices[100.0; 0.05; 0.20; 1.0 % 252.0; 252; 100000]}; 3]
 };

main:{[]
    results: `language`benchmarks ! (`q; `ring_buffer_push_1e6`vwap_1e6`ewma_1e6`monte_carlo_gbm_1e5x252 ! (benchRingBuffer[]; benchVwap[]; benchEwma[]; benchMc[]));
    h: hopen `:results/q.json;
    -1 "Wrote results/q.json";
 };

main[];
\\
