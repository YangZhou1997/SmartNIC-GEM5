# ./build/ARM/gem5.opt ./configs/example/se.py \
#     --interp-dir /usr/aarch64-linux-gnu \
#     --redirects /lib=/usr/aarch64-linux-gnu/lib \
#     -c ./test/testfs

./build/ARM/gem5.opt ./configs/example/se.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -n 2 --mem-size=16GB \
    -c /users/yangzhou/NetBricks-GEM5/target/aarch64-unknown-linux-gnu/debug/dpi \
    --options="32"


# ./build/ARM/gem5.opt ./configs/example/se_nic.py \
#     --interp-dir /usr/aarch64-linux-gnu \
#     --redirects /lib=/usr/aarch64-linux-gnu/lib \
#     -c "/users/yangzhou/NetBricks-GEM5/target/aarch64-unknown-linux-gnu/debug/spmc;/users/yangzhou/NetBricks-GEM5/target/aarch64-unknown-linux-gnu/debug/macswap" \
#     -n 3 \
#     --cpu-type=TimingSimpleCPU \
#     --cacheline_size=128 \
#     --caches \
#     --l1d_size=32kB --l1d_assoc=32 \
#     --l1i_size=78kB --l1i_assoc=39 \
#     --l2cache \
#     --l2_size=4MB --l2_assoc=16 \
#     --mem-size=16GB --mem-type=DDR3_1600_8x8 \
#     --asic-clock=10GHz \
