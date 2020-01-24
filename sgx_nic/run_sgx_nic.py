#!/usr/bin/python3.7

import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
import threading

gem5home = os.getcwd()

scriptgen_dir = gem5home + "/scriptgen"
results_dir = gem5home + "/results"
stdout_dir = gem5home + "/stdout"
stderr_dir = gem5home + "/stderr"

nfinvoke = ['acl-fw', 'dpi-queue', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']

# Available BaseCPU classes:
#         O3_ARM_v7a_3
#         AtomicSimpleCPU
#                 Simple CPU model executing a configurable number of instructions per
#                 cycle. This model uses the simplified 'atomic' memory mode.
#         ex5_big
#         DerivO3CPU
#         MinorCPU
#         HPI
#                 The High-Performance In-order (HPI) CPU timing model is tuned to be
#                 representative of a modern in-order ARMv8-A implementation. The HPI
#                 core and its supporting simulation scripts, namely starter_se.py and
#                 starter_fs.py (under /configs/example/arm/) are part of the ARM
#                 Research Starter Kit on System Modeling. More information can be
#                 found at: http://www.arm.com/ResearchEnablement/SystemModeling
#         ex5_LITTLE
#         NonCachingSimpleCPU
#                 Simple CPU model based on the atomic CPU. Unlike the atomic CPU,
#                 this model causes the memory system to bypass caches and is
#                 therefore slightly faster in some cases. However, its main purpose
#                 is as a substitute for hardware virtualized CPUs when stress-testing
#                 the memory system.
#         TimingSimpleCPU
cpus = ['TimingSimpleCPU', 'DerivO3CPU']

# Available AbstractMemory classes:
#         HBM_1000_4H_1x128
#         DRAMCtrl
#         DDR3_2133_8x8
#         HBM_1000_4H_1x64
#         GDDR5_4000_2x32
#         HMC_2500_1x32
#         LPDDR3_1600_1x32
#         WideIO_200_1x128
#         QoSMemSinkCtrl
#         DDR4_2400_8x8
#         DDR3_1600_8x8
#         DDR4_2400_4x16
#         DDR4_2400_16x4
#         SimpleMemory
#         LPDDR2_S4_1066_1x32
# memctrls = ['DDR3_1600_8x8']

# Workload Characterization
# Cache insensitive: astar, libquantum
# Large gain beyond half cache: bzip2 mcf xalan soplex
# Small gain beyond half cache: gcc h264ref gobmk hmmer sjeng

mem_size = '128GB'

million = 1000000000
trillion = 1000000000000
# 1 million: the number of ins spent on loading traces
# once any nf reaches this number of ins, gem5 will enter real simulation. 
fast_forward_ins = 2 * million

# 5 * trillion: the benchmarking time.
final_ticks = 3 * trillion


singleprog = nfinvoke
multiprog = []
for i in range(1, 1 << 6):
    prog_set = []
    for j in range(6):
        if (i >> j) & 1 == 1:
            prog_set.append(nfinvoke[j])
    multiprog.append(prog_set)
multiprog = list(filter(lambda x: len(x) > 1, multiprog))
# print(multiprog, len(multiprog))

def prog_set_to_cmd(prog_set):
    ret = ''
    num_prog = len(prog_set)
    for i in range(num_prog - 1):
        ret += prog_set[i] + ';'
    ret += prog_set[-1]
    return ret

if not os.path.exists(scriptgen_dir):
    os.makedirs(scriptgen_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

if not os.path.exists(stdout_dir):
    os.makedirs(stdout_dir)

if not os.path.exists(stderr_dir):
    os.makedirs(stderr_dir)

l2_size = ['4MB', '2MB', '1MB', '512kB', '256kB', '128kB', '64kB', '32kB', '16kB', '8kB', '4kB']

all_commands = []

def cache_partition():
    for cpu in cpus:
        for nf in singleprog:
            cmd = nf
            for l2 in l2_size:
                filename = f'{cpu}_{cmd}_{l2}'
                temp = filename.replace(';', '.')
                bash_filename = f'{scriptgen_dir}/run_{temp}.sh'
                script = open(bash_filename, "w")
                command = "#!/bin/bash\n"
                command += "build/ARM/gem5.opt \\\n"
                command += "    --remote-gdb-port=0 \\\n"
                command += "    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/" + temp + " \\\n"
                command += "    --stats-file=" + temp + "_stats.txt \\\n"
                command += "    configs/example/se_nic.py \\\n"
                command += "    --interp-dir /usr/aarch64-linux-gnu \\\n"
                command += "    --redirects /lib=/usr/aarch64-linux-gnu/lib \\\n"
                command += "    -c \"" + cmd + "\" \\\n"
                command += "    --cpu-type=" + cpu + " --cpu-clock=2.4GHz --asic-clock=0.56GHz \\\n"
                command += "    --cacheline_size=128 \\\n"
                command += "    --caches --l2cache \\\n"
                command += "    --l2_size=" + l2 + " --l2_assoc=16 \\\n"
                command += "    --mem-size=" + mem_size + " --mem-type=DDR3_1600_8x8" + " --mem-channels=2 --mem-ranks=2 \\\n"
                command += "    --fast-forward=" + str(fast_forward_ins) + " \\\n"    
                command += "    --rel-max-tick=" + str(final_ticks) + " \\\n"
                command += "    > " + results_dir + "/stdout_" + temp + ".out \\\n"
                command += "    2> " + stderr_dir + "/stderr_" + temp + ".out"

                script.write(f'{command}\n')
                script.close()

                os.system(f'chmod +x {bash_filename}')
                # os.system(f'bash {bash_filename}')
                all_commands.append(f'cd .. && bash {bash_filename}')

def bus_arbitor():
    for cpu in cpus:
        for nf_set in multiprog:
            cmd = prog_set_to_cmd(nf_set)
            filename = f'{cpu}_{cmd}_4MB'
            temp = filename.replace(';', '.')
            bash_filename = f'{scriptgen_dir}/run_{temp}.sh'
            script = open(bash_filename, "w")
            command = "#!/bin/bash\n"
            command += "build/ARM/gem5.opt \\\n"
            command += "    --remote-gdb-port=0 \\\n"
            command += "    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/" + temp + " \\\n"
            command += "    --stats-file=" + temp + "_stats.txt \\\n"
            command += "    configs/example/se_nic.py \\\n"
            command += "    --interp-dir /usr/aarch64-linux-gnu \\\n"
            command += "    --redirects /lib=/usr/aarch64-linux-gnu/lib \\\n"
            command += "    -c \"" + cmd + "\" \\\n"
            command += "    --cpu-type=" + cpu + " --cpu-clock=2.4GHz --asic-clock=0.56GHz \\\n"
            command += "    --cacheline_size=128 \\\n"
            command += "    --caches --l2cache \\\n"
            command += "    --l2_size=4MB --l2_assoc=16 \\\n"
            command += "    --mem-size=" + mem_size + " --mem-type=DDR3_1600_8x8" + " --mem-channels=2 --mem-ranks=2 \\\n"
            command += "    --fast-forward=" + str(fast_forward_ins) + " \\\n"
            command += "    --rel-max-tick=" + str(final_ticks) + " \\\n"
            command += "    > " + results_dir + "/stdout_" + temp + ".out \\\n"
            command += "    2> " + stderr_dir + "/stderr_" + temp + ".out"

            script.write(f'{command}\n')
            script.close()

            os.system(f'chmod +x {bash_filename}')
            # os.system(f'bash {bash_filename}')
            all_commands.append(f'cd .. && bash {bash_filename}')

def exe_gem5_sim(cmd_line):
    try:
        print(f'{threading.currentThread().getName()} running: {cmd_line}', flush=True)
        os.popen(cmd_line).read()
        print(f'{threading.currentThread().getName()} okay: {cmd_line}', flush=True)
        return f'okay: {cmd_line}'
    except Exception:
        print(f'{threading.currentThread().getName()} fails: {cmd_line}', flush=True)
        return f'fails: {cmd_line}'

def run_gem5_sim(commands):
    # 1 thread is left.
    pool = ThreadPool(55)
    results = pool.map(exe_gem5_sim, commands)
    pool.close()
    pool.join()
    for res in results:
        print(res)

if __name__ == "__main__":
    cache_partition()
    bus_arbitor()
    num_cmd = len(all_commands)
    print(f'The number of gem5 simulations is {num_cmd}')
    num_par = int(num_cmd / 6) + 1
    run_gem5_sim(all_commands[0:num_par])
    # run_gem5_sim(all_commands[num_par:num_par * 2])
    # run_gem5_sim(all_commands[num_par * 2:num_par * 3])
    # run_gem5_sim(all_commands[num_par * 3:num_par * 4])
    # run_gem5_sim(all_commands[num_par * 4:num_par * 5])
    # run_gem5_sim(all_commands[num_par * 5:])