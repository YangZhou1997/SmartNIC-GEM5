./build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=m5out/test \
    --stats-file=stats.txt \
    configs/example/se_nic.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c "dpi" \
    --arch "arm" \
    --cpu-type=TimingSimpleCPU --cpu-clock=2.4GHz --asic-clock=0.56GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=4MB --l2_assoc=16 \
    --mem-size=128GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
    # --options="1024" \
    # --fast-forward=5224493161500 \

# ./build/X86/gem5.fast \
#     --remote-gdb-port=0 \
#     --outdir=m5out/test \
#     --stats-file=stats.txt \
#     configs/example/se_nic.py \
#     -c "dpi" \
#     --arch "x86" \
#     --cpu-type=TimingSimpleCPU --cpu-clock=2.4GHz --asic-clock=0.56GHz \
#     --cacheline_size=128 \
#     --caches --l2cache \
#     --l2_size=4MB --l2_assoc=16 \
#     --mem-size=128GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
#     --options="1024" \
#     --fast-forward=5224493161500 \
