#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=m5out/nic \
    --stats-file=HPI_DDR3_1600_8x8_acl-fw_2MB_stats.txt \
    configs/example/se_nic.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c "acl-fw" \
    --cpu-type=HPI --cpu-clock=2.4GHz --asic-clock=0.56GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=2MB --l2_assoc=16 \
    --mem-size=256GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
    > /users/yangzhou/gem5/sim_nic/results/nic/stdout_HPI_DDR3_1600_8x8_acl-fw_2MB.out
