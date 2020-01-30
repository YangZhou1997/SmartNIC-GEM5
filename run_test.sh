#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/gem5/m5out/test1 \
    --stats-file=arm32.txt \
    configs/example/se.py \
    -c /users/yangzhou/NF-GEM5/m5threads/tests/test___thread \
    --options="2" \
    --cpu-type=TimingSimpleCPU --cpu-clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=4MB --l2_assoc=16 \
    --mem-size=128GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
    -n 3 \
    # --fast-forward=2000000000 \
    # --rel-max-tick=5000000000000 \
    # > /users/yangzhou/gem5/sgx_nic/results/stdout_TimingSimpleCPU_dpi_4MB.out \
    # 2> /users/yangzhou/gem5/sgx_nic/stderr/stderr_TimingSimpleCPU_dpi_4MB.out
