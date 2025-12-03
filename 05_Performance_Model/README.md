# Module 05: Performance Modeling 📊

## Overview

This module analyzes the **performance impact** of memory hierarchy design choices. We cover:
- CPI (Cycles Per Instruction) analysis
- Memory access time calculations
- Cache miss penalties
- TLB miss impact
- Real-world performance examples

---

## 📚 Table of Contents

1. [CPI and Memory Hierarchy](#cpi-and-memory-hierarchy)
2. [Effective Memory Access Time (EMAT)](#effective-memory-access-time-emat)
3. [Cache Performance Metrics](#cache-performance-metrics)
4. [TLB Performance Impact](#tlb-performance-impact)
5. [Multi-Level Cache Analysis](#multi-level-cache-analysis)
6. [Performance Examples](#performance-examples)
7. [Python Tools](#python-tools)

---

## CPI and Memory Hierarchy

### Base CPI vs Effective CPI

```
Base CPI: Cycles per instruction (assuming perfect memory)
Effective CPI: Base CPI + memory stall cycles

Effective CPI = Base CPI + Memory Stalls per Instruction

Memory Stalls = Instruction Misses + Data Misses
```

### Example Calculation

```
Processor:
  Base CPI = 1.0 (ideal, no stalls)
  Clock = 3 GHz

Memory:
  L1 hit time = 1 cycle
  L1 miss rate = 5%
  L1 miss penalty = 100 cycles

Per instruction:
  Assume 1 instruction fetch + 0.3 data accesses on average

Instruction stalls = 1 × 0.05 × 100 = 5 cycles
Data stalls = 0.3 × 0.05 × 100 = 1.5 cycles

Effective CPI = 1.0 + 5 + 1.5 = 7.5

Without L1 cache: CPI = 1.0 + 1×100 + 0.3×100 = 131 cycles
With L1 cache: CPI = 7.5 cycles

→ 17.5× speedup from L1 cache! 🚀
```

---

## Effective Memory Access Time (EMAT)

### Single-Level Cache

```
EMAT = Hit_Time + Miss_Rate × Miss_Penalty

Example:
  Hit time = 1 cycle
  Miss rate = 5%
  Miss penalty = 200 cycles
  
  EMAT = 1 + 0.05 × 200 = 11 cycles
```

### Multi-Level Cache

```
EMAT = L1_Hit_Time
       + L1_Miss_Rate × (L2_Hit_Time
       + L2_Miss_Rate × (L3_Hit_Time
       + L3_Miss_Rate × Memory_Time))

Example:
  L1: 4 cycles, 95% hit
  L2: 12 cycles, 80% hit (of L1 misses)
  L3: 40 cycles, 90% hit (of L2 misses)
  Memory: 200 cycles
  
  EMAT = 4 
         + 0.05 × (12 
         + 0.20 × (40 
         + 0.10 × 200))
       = 4 + 0.05 × (12 + 0.20 × 60)
       = 4 + 0.05 × 24
       = 5.2 cycles
```

---

## Cache Performance Metrics

### Miss Rate vs Miss Penalty

```
Reducing miss rate by 1% at 200-cycle penalty:
  Savings = 0.01 × 200 = 2 cycles per access

Reducing miss penalty by 10 cycles at 5% miss rate:
  Savings = 0.05 × 10 = 0.5 cycles per access

→ Miss rate reduction more impactful!
```

### AMAT (Average Memory Access Time)

```
AMAT = Hit_Time + Miss_Rate × Miss_Penalty

Sensitivity analysis:
┌────────────┬──────────┬──────────┬──────────┐
│ Miss Rate  │ AMAT (cy)│ vs 1%    │ vs 5%    │
├────────────┼──────────┼──────────┼──────────┤
│ 1%         │ 3.0      │ baseline │ 6.7× faster│
│ 2%         │ 5.0      │ 1.7× slower│ 4.0× faster│
│ 5%         │ 11.0     │ 3.7× slower│ baseline │
│ 10%        │ 21.0     │ 7.0× slower│ 1.9× slower│
└────────────┴──────────┴──────────┴──────────┘

Assumes: Hit=1cy, Miss Penalty=200cy
```

---

## TLB Performance Impact

### TLB Miss Penalty

```
Without TLB:
  Every memory access requires page walk (4 levels)
  4 memory accesses × 200 cycles = 800 cycles overhead!

With TLB (95% hit rate):
  0.95 × 1 cycle + 0.05 × 800 cycles = 40.95 cycles

→ 19.5× speedup! 🚀
```

### Combined Cache + TLB

```
Memory access breakdown:
  1. TLB lookup (translate VA→PA)
  2. Cache lookup (fetch data)

Case 1: TLB hit, Cache hit
  Time = TLB_hit + Cache_hit = 1 + 1 = 2 cycles

Case 2: TLB hit, Cache miss
  Time = TLB_hit + Cache_miss_penalty = 1 + 200 = 201 cycles

Case 3: TLB miss, Cache hit
  Time = Page_walk + Cache_hit = 800 + 1 = 801 cycles

Case 4: TLB miss, Cache miss
  Time = Page_walk + Cache_miss_penalty = 800 + 200 = 1000 cycles

Probabilities:
  TLB hit = 95%, Cache hit = 95%
  
  Case 1: 0.95 × 0.95 = 90.25%  → 2 cycles
  Case 2: 0.95 × 0.05 = 4.75%   → 201 cycles
  Case 3: 0.05 × 0.95 = 4.75%   → 801 cycles
  Case 4: 0.05 × 0.05 = 0.25%   → 1000 cycles

Average = 0.9025×2 + 0.0475×201 + 0.0475×801 + 0.0025×1000
        = 1.805 + 9.548 + 38.048 + 2.5
        = 51.9 cycles

→ TLB misses add 50 cycles on average!
```

---

## Multi-Level Cache Analysis

### Inclusive vs Exclusive Caches

**Inclusive**: L2 contains all data in L1
- Pros: Simpler coherence
- Cons: Wasted capacity

**Exclusive**: L2 and L1 don't overlap
- Pros: More total capacity
- Cons: Complex management

### Local vs Global Miss Rate

```
Local Miss Rate: Misses at this level / Accesses to this level
Global Miss Rate: Misses at this level / Total accesses

Example:
  L1: 1000 accesses, 50 misses → Local MR = 5%
  L2: 50 accesses, 10 misses   → Local MR = 20%
  
  Global L1 MR = 50/1000 = 5%
  Global L2 MR = 10/1000 = 1%
  
  Overall miss rate = 1% (go to memory)
```

### Victim Cache

Small fully-associative cache for recently evicted L1 lines.

```
Without victim cache:
  Conflict miss → evict → reload → evict (thrashing)

With victim cache (4 entries):
  Conflict miss → check victim cache → hit! (fast recovery)
  
Typical: 4-16 entries, removes 20-40% of conflict misses
```

---

## Performance Examples

### Example 1: Matrix Multiplication

```python
# Naive: bad cache behavior
for i in range(N):
    for j in range(N):
        for k in range(N):
            C[i][j] += A[i][k] * B[k][j]  # B accessed by column (bad!)

# Blocked: good cache behavior
for ii in range(0, N, BLOCK):
    for jj in range(0, N, BLOCK):
        for kk in range(0, N, BLOCK):
            for i in range(ii, min(ii+BLOCK, N)):
                for j in range(jj, min(jj+BLOCK, N)):
                    for k in range(kk, min(kk+BLOCK, N)):
                        C[i][j] += A[i][k] * B[k][j]

Performance:
  Naive: 85% cache miss rate
  Blocked (32×32): 5% cache miss rate
  → 10× speedup for large matrices!
```

### Example 2: Huge Pages

```
Application: Database with 4GB working set

With 4KB pages:
  Pages needed: 1,048,576
  TLB (512 entries): covers 2MB
  TLB miss rate: 99.95%! 💥
  
  Time per access = 0.0005×1 + 0.9995×800 = 800 cycles

With 2MB huge pages:
  Pages needed: 2,048
  TLB (512 entries): covers 1GB
  TLB miss rate: 50%
  
  Time per access = 0.50×1 + 0.50×800 = 400.5 cycles
  
  → 2× speedup! 🚀
```

### Example 3: Prefetching

```
Sequential access pattern (streaming):

Without prefetching:
  Access[i] → miss (100 cycles)
  Access[i+1] → miss (100 cycles)
  ...
  Average: 100 cycles per access

With sequential prefetcher:
  Access[i] → miss, trigger prefetch of [i+1, i+2, ...]
  Access[i+1] → hit! (prefetched)
  Access[i+2] → hit! (prefetched)
  ...
  Average: ~10 cycles per access (90% prefetch accuracy)
  
  → 10× speedup for streaming workloads!
```

---

## Python Tools

See [`performance_analyzer.py`](./performance_analyzer.py) for tools to:
- Calculate EMAT
- Analyze CPI impact
- Compare cache configurations
- Model TLB performance

### Command Line Usage

```bash
# View help
python performance_analyzer.py --help

# Run all demos
python performance_analyzer.py

# Run specific demo
python performance_analyzer.py --demo emat
python performance_analyzer.py --demo cpi
python performance_analyzer.py --demo tlb
python performance_analyzer.py --demo combined
python performance_analyzer.py --demo optimization

# Calculate EMAT for specific cache configuration
python performance_analyzer.py --emat --hit-time 1 --miss-rate 0.05 --miss-penalty 200
```

#### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--demo` | Run specific demo (emat/cpi/tlb/combined/optimization/all) | all |
| `--emat` | Calculate EMAT for single-level cache | False |
| `--hit-time` | Cache hit time in cycles (for EMAT) | 1.0 |
| `--miss-rate` | Cache miss rate 0.0-1.0 (for EMAT) | 0.05 |
| `--miss-penalty` | Cache miss penalty in cycles (for EMAT) | 200.0 |

### Python API Usage

```python
from performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Single-level cache
emat = analyzer.emat_single_level(
    hit_time=1,
    miss_rate=0.05,
    miss_penalty=200
)

# Multi-level cache
emat = analyzer.emat_multi_level(
    l1_hit=1, l1_miss_rate=0.05,
    l2_hit=12, l2_miss_rate=0.20,
    l3_hit=40, l3_miss_rate=0.10,
    mem_time=200
)
```

---

## Key Formulas

| Formula | Description |
|---------|-------------|
| `Effective CPI = Base CPI + Memory Stalls` | Impact on overall performance |
| `EMAT = Hit_Time + MR × Miss_Penalty` | Average memory access time |
| `Speedup = Time_old / Time_new` | Performance improvement |
| `IPC = 1 / CPI` | Instructions per cycle |
| `Throughput = IPC × Clock_Frequency` | Instructions per second |

---

## Interview Questions

1. **What's more important: reducing miss rate or miss penalty?**
   - Depends on current values; typically miss rate has bigger impact

2. **How does TLB miss penalty compare to cache miss penalty?**
   - TLB miss (page walk): 20-800 cycles; Cache miss: 100-200 cycles

3. **Why do huge pages improve performance?**
   - Increase TLB reach (512 × 2MB = 1GB vs 512 × 4KB = 2MB)

4. **What's the difference between local and global miss rate?**
   - Local: misses at this level / accesses to this level
   - Global: misses at this level / all accesses

5. **How much does a 1% cache miss rate improvement help?**
   - At 200-cycle penalty: saves 2 cycles per access

---

## Next Steps

✅ Run `performance_analyzer.py` to model different configurations  
✅ Experiment with workload scenarios  
✅ Move to [Module 06: Web App](../06_WebApp/README.md)

---

**📌 Key Insight**: Memory hierarchy design is about balancing hit rate, hit time, and miss penalty. Small improvements (1-2%) in hit rate can yield 10-20% overall performance gains!

