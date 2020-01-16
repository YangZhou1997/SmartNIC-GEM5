# ./build/MIPS/gem5.opt ./configs/example/se.py \
#     --interp-dir /usr/mipsel-linux-gnu \
#     --redirects /lib=/usr/mipsel-linux-gnu/lib \
#     -c ./test/testfs

./build/X86/gem5.opt ./configs/example/se.py \
    --interp-dir /usr/mipsel-linux-gnu \
    --redirects /lib=/usr/mipsel-linux-gnu/lib \
    -c ~/NetBricks-GEM5/target/mipsel-unknown-linux-gnu/debug/spmc \
    -n 33 --mem-size=10240000000