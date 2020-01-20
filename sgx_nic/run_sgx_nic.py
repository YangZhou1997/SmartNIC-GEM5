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

nfinvoke = ['acl-fw', 'dpi', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']

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

if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = "nic"

if not os.path.exists("m5out/" + folder):
    os.makedirs("m5out/" + folder)

if not os.path.exists("results/" + folder):
    os.makedirs("results/" + folder)

if not os.path.exists("stdout/" + folder):
    os.makedirs("stdout/" + folder)

if not os.path.exists("stderr/" + folder):
    os.makedirs("stderr/" + folder)

l2_size = ['4MB', '2MB', '1MB', '512kB', '256kB']

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
                    command += "build/ARM/gem5.fast \\\n"
                    command += "    --remote-gdb-port=0 \\\n"
                    command += "    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/" + folder + " \\\n"
                    command += "    --stats-file=" + filename + "_stats.txt \\\n"
                    command += "    configs/example/se_nic.py \\\n"
                    command += "    --interp-dir /usr/aarch64-linux-gnu \\\n"
                    command += "    --redirects /lib=/usr/aarch64-linux-gnu/lib \\\n"
                    command += "    -c \"" + cmd + "\" \\\n"
                    command += "    --cpu-type=" + cpu + " --cpu-clock=2.4GHz --asic-clock=0.56GHz \\\n"
                    command += "    --cacheline_size=128 \\\n"
                    command += "    --caches --l2cache \\\n"
                    command += "    --l2_size=" + l2 + " --l2_assoc=16 \\\n"
                    command += "    --mem-size=" + mem_size + " --mem-type=DDR3_1600_8x8" + " --mem-channels=2 --mem-ranks=2 \\\n"
                    command += "    > " + results_dir + "/" + folder + "/stdout_" + filename + ".out \\\n"
                    command += "    2> " + stderr_dir + "/" + folder + "/stderr_" + filename + ".out"
        
                    script.write(f'{command}\n')
                    script.close()

                    os.system(f'chmod +x {bash_filename}')
                    # os.system(f'bash {bash_filename}')
                    all_commands.append(f'bash {bash_filename}')

def bus_arbitor():
    for cpu in cpus:
            for nf_set in multiprog:
                cmd = prog_set_to_cmd(nf_set)
                filename = f'{cpu}_{cmd}'        
                temp = filename.replace(';', '.')            
                bash_filename = f'{scriptgen_dir}/run_{temp}.sh'                    
                script = open(bash_filename, "w")
                command = "#!/bin/bash\n"
                command += "build/ARM/gem5.fast \\\n"
                command += "    --remote-gdb-port=0 \\\n"
                command += "    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/" + folder + " \\\n"
                command += "    --stats-file=" + filename + "_stats.txt \\\n"
                command += "    configs/example/se_nic.py \\\n"
                command += "    --interp-dir /usr/aarch64-linux-gnu \\\n"
                command += "    --redirects /lib=/usr/aarch64-linux-gnu/lib \\\n"
                command += "    -c \"" + cmd + "\" \\\n"
                command += "    --cpu-type=" + cpu + " --cpu-clock=2.4GHz --asic-clock=0.56GHz \\\n"
                command += "    --cacheline_size=128 \\\n"
                command += "    --caches --l2cache \\\n"
                command += "    --l2_size=4MB --l2_assoc=16 \\\n"
                command += "    --mem-size=" + mem_size + " --mem-type=DDR3_1600_8x8" + " --mem-channels=2 --mem-ranks=2 \\\n"
                command += "    > " + results_dir + "/" + folder + "/stdout_" + filename + ".out"
                command += "    2> " + stderr_dir + "/" + folder + "/stderr_" + filename + ".out"
    
                script.write(f'{command}\n')
                script.close()

                os.system(f'chmod +x {bash_filename}')
                # os.system(f'bash {bash_filename}')
                all_commands.append(f'bash {bash_filename}')

def exe_gem5_sim(cmd_line):
    print(threading.currentThread().getName())
    print(cmd_line)
    try:
        os.system(cmd_line)
        return cmd_line + " ok"
    except Exception:
        return cmd_line + " fails"

def run_gem5_sim():    
    # 1 thread is left. 
    pool = ThreadPool(55)
    results = pool.map(exe_gem5_sim, all_commands)
    pool.close()
    pool.join()
    for res in results:
        print(res)

if __name__ == "__main__":
    cache_partition()
    bus_arbitor()
    print(f'The number of gem5 simulations is {len(all_commands)}')

    