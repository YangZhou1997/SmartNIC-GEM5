#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=m5out/nic \
    --stats-file=TimingSimpleCPU_DDR4_2400_8x8_acl-fw;dpi;nat-tcp-v4;lpm_stats.txt \
    configs/example/se_nic.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c "acl-fw;dpi;nat-tcp-v4;lpm" \
    --cpu-type=TimingSimpleCPU --cpu-clock=2.4GHz --asic-clock=0.56GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=4MB --l2_assoc=16 \
    --mem-size=256GB --mem-type=DDR4_2400_8x8 --mem-channels=2 --mem-ranks=2 \
    > /users/yangzhou/gem5/sim_nic/results/nic/stdout_TimingSimpleCPU_DDR4_2400_8x8_acl-fw;dpi;nat-tcp-v4;lpm.out
