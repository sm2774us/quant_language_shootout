/ ring_buffer.q — Encapsulated, power-of-2, fixed-capacity ring buffer.
/ Requires a licensed kdb+ 4.0 binary; not executed in CI (see benchmark.yml).

ringBuffer:{[n]
    if[not 0 = n mod 1; '"n must be numeric"];
    `buf`head`count`n ! (n#0f; 0; 0; n)
 };

ringPush:{[obj; v]
    idx: (obj[`head] + obj[`count]) mod obj[`n];
    obj[`buf][idx]: v;
    if[obj[`count] < obj[`n];
        obj[`count] +: 1;
        :obj
    ];
    obj[`head]: (obj[`head] + 1) mod obj[`n];
    obj
 };

ringGet:{[obj; i]
    if[(i < 0) or (i >= obj[`count]); 'indexError];
    idx: (obj[`head] + i) mod obj[`n];
    obj[`buf][idx]
 };

ringSize:{[obj] obj[`count]};
ringCapacity:{[obj] obj[`n]};
