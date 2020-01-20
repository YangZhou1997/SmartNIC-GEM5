# Copyright (c) 2012-2013 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2006-2008 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Steve Reinhardt

# Simple test script
#
# "m5 test.py"

from __future__ import print_function
from __future__ import absolute_import

import optparse
import sys
import os

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn

addToPath('../')

from ruby import Ruby

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import ObjectList
from common import MemConfig
from common.FileSystemConfig import config_filesystem
from common.Caches import *
from common.cpu2000 import *

DPI_THREAD_NUM = 16
BASE_DIR = '/users/yangzhou/NetBricks-GEM5/target/aarch64-unknown-linux-gnu/release/'

NFS = ['acl-fw', 'dpi', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring', 'spmc', 'helloworld']

def get_processes(options):
    """Interprets provided options and returns a list of processes"""

    nf_core_mapping = {}
    multiprocesses = {}

    inputs = []
    outputs = []
    errouts = []
    pargs = []

    workloads = options.cmd.split(';')
    print(workloads)
    if options.input != "":
        inputs = options.input.split(';')
    if options.output != "":
        outputs = options.output.split(';')
    if options.errout != "":
        errouts = options.errout.split(';')
    if options.options != "":
        pargs = options.options.split(';')

    idx = 0
    for wrkld in workloads:
        process = Process(pid = 100 + idx)
        process.executable = BASE_DIR + wrkld
        process.cwd = os.getcwd()

        if options.env:
            with open(options.env, 'r') as f:
                process.env = [line.rstrip() for line in f]

        if len(pargs) > idx:
            process.cmd = [wrkld] + pargs[idx].split()
        else:
            process.cmd = [wrkld]

        if len(inputs) > idx:
            process.input = inputs[idx]
        if len(outputs) > idx:
            process.output = outputs[idx]
        if len(errouts) > idx:
            process.errout = errouts[idx]

        multiprocesses[wrkld] = process

        if wrkld == 'dpi':
            core_set = [i for i in range(idx, idx + DPI_THREAD_NUM + 1)]
            idx += DPI_THREAD_NUM + 1
        elif wrkld == 'spmc':
            core_set = [i for i in range(idx, idx + DPI_THREAD_NUM + 1)]
            idx += DPI_THREAD_NUM + 1
        else:
            core_set = [i for i in range(idx, idx + 1)]
            idx += 1
        nf_core_mapping[wrkld] = core_set

    return nf_core_mapping, multiprocesses, idx


parser = optparse.OptionParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)
parser.add_option("--asic-clock", action="store", type="string",
                      default='10GHz',
                      help = """Clock for blocks running at ASIC speed""")
parser.add_option("--arch", action="store", type="string",
                      default='arm',
                      help = """arm or x86""")

(options, args) = parser.parse_args()

options.l1d_size="32kB"
options.l1d_assoc=32
options.l1i_size="78kB"
options.l1i_assoc=39

if args:
    print("Error: script doesn't take any positional arguments")
    sys.exit(1)

if options.arch == 'x86':
    BASE_DIR = '/users/yangzhou/NetBricks-GEM5/target/x86_64-unknown-linux-musl/release/'

nf_core_mapping = {}
multiprocesses = {}
num_cores = 0

if options.cmd:
    nf_core_mapping, multiprocesses, num_cores = get_processes(options)
    print(nf_core_mapping, len(multiprocesses), num_cores)
    options.num_cpus = num_cores
else:
    print("No workload specified. Exiting!\n", file=sys.stderr)
    sys.exit(1)

(CPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(options)
CPUClass.numThreads = 1

system = System(cpu = [CPUClass(cpu_id=i) for i in range(num_cores)],
                mem_mode = test_mem_mode,
                mem_ranges = [AddrRange(options.mem_size)],
                cache_line_size = options.cacheline_size)

# Create a top-level voltage domain
system.voltage_domain = VoltageDomain(voltage = options.sys_voltage)
# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(clock =  options.sys_clock, voltage_domain = system.voltage_domain)
# Create a CPU voltage domain
system.cpu_voltage_domain = VoltageDomain()
# Create a separate clock domain for the CPUs
system.cpu_clk_domain = SrcClockDomain(clock = options.cpu_clock, voltage_domain = system.cpu_voltage_domain)
# Create a separate clock domain for the accelerators
asic_clk_domain = SrcClockDomain(clock = options.asic_clock, voltage_domain = system.cpu_voltage_domain)

for nf in NFS:
    if nf in nf_core_mapping and nf in multiprocesses:
        core_set = nf_core_mapping[nf]
        process = multiprocesses[nf]
        for i, core_id in enumerate(core_set):
            if i == 0:
                system.cpu[core_id].clk_domain = system.cpu_clk_domain
            else:
                system.cpu[core_id].clk_domain = asic_clk_domain        
            system.cpu[core_id].workload = process
            system.cpu[core_id].createThreads()

# use classic memory model. 
MemClass = Simulation.setMemClass(options)
system.membus = SystemXBar()
system.system_port = system.membus.slave
if 'dpi' in nf_core_mapping or 'spmc' in nf_core_mapping:
    temp_core_set = []
    if 'dpi' in nf_core_mapping:
        temp_core_set.extend(nf_core_mapping['dpi'][1:])
    if 'spmc' in nf_core_mapping:
        temp_core_set.extend(nf_core_mapping['spmc'][1:])
    CacheConfig.config_cache(options, system, temp_core_set)
else:
    CacheConfig.config_cache(options, system)
MemConfig.config_mem(options, system)
config_filesystem(system, options)

# reconfig the dpi hardware thread l1 dcache to make it connect to the memory bus directly;
if 'dpi' in nf_core_mapping:
    core_set = nf_core_mapping['dpi']
    for i, core_id in enumerate(core_set):
        if i == 0:
            continue
        system.cpu[core_id].icache.mem_side = system.membus.slave
        system.cpu[core_id].dcache.mem_side = system.membus.slave
        system.cpu[core_id].itb.walker.port = system.membus.slave
        system.cpu[core_id].dtb.walker.port = system.membus.slave
        # print(system.cpu[core_id].icache.mem_side, system.cpu[core_id].dcache.mem_side)
        system.cpu[core_id].dcache.size = "8kB"
        system.cpu[core_id].dcache.assoc = 1

if 'spmc' in nf_core_mapping:
    core_set = nf_core_mapping['spmc']
    for i, core_id in enumerate(core_set):
        if i == 0:
            continue
        system.cpu[core_id].icache.mem_side = system.membus.slave
        system.cpu[core_id].dcache.mem_side = system.membus.slave
        system.cpu[core_id].itb.walker.port = system.membus.slave
        system.cpu[core_id].dtb.walker.port = system.membus.slave
        # print(system.cpu[core_id].icache.mem_side, system.cpu[core_id].dcache.mem_side)
        system.cpu[core_id].dcache.size = "8kB"
        system.cpu[core_id].dcache.assoc = 1

# import sys
# sys.exit()

root = Root(full_system = False, system = system)
Simulation.run(options, root, system, FutureClass)
