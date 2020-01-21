#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/nic \
    --stats-file=DerivO3CPU_acl-fw.maglev.monitoring_4MB_4_stats.txt \
    configs/example/se_nic.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c "acl-fw;maglev;monitoring" \
    --cpu-type=DerivO3CPU --cpu-clock=2.4GHz --asic-clock=0.56GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=4MB --l2_assoc=16 \
    --mem-size=128GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
    --fast-forward=1308843841 \
    --maxinsts=5549785729 \
    --abs-max-tick=4000000000000 \
    > /users/yangzhou/gem5/sgx_nic/results/nic/stdout_DerivO3CPU_acl-fw.maglev.monitoring_4MB_4.out \
    2> /users/yangzhou/gem5/sgx_nic/stderr/nic/stderr_DerivO3CPU_acl-fw.maglev.monitoring_4MB_4.out
