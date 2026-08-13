/ ewma.q — EWMA variance recurrence via the built-in `ema` C-kernel verb.
/ x ema y computes r[0]=y[0], r[i] = (1-x)*r[i-1] + x*y[i]; mapping x = 1-lambda
/ reproduces V_t = lambda*V_{t-1} + (1-lambda)*R_t^2.
/ Requires a licensed kdb+ 4.0 binary; not executed in CI (see benchmark.yml).

ewmaVol:{[ret; lambda]
    sqRet: ret * ret;
    (1f - lambda) ema sqRet
 };
