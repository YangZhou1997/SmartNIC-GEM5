# ./build/ARM/gem5.opt ./configs/example/se.py \
#     --interp-dir /usr/aarch64-linux-gnu \
#     --redirects /lib=/usr/aarch64-linux-gnu/lib \
#     -c ./test/testfs

./build/ARM/gem5.opt ./configs/example/se.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c ~/NetBricks-GEM5/target/aarch64-unknown-linux-gnu/debug/spmc \
    -n 33 \
    --mem-size=10240000000