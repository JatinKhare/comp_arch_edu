# Module 01: Cache Basics 🗄️

## Overview

This module covers the fundamentals of CPU caches - the fastest level of memory in modern computer systems. You'll learn how caches work, how addresses are decomposed, and how different cache organizations affect performance.

---

## 📚 Table of Contents

1. [What is a Cache?](#what-is-a-cache)
2. [Why Do We Need Caches?](#why-do-we-need-caches)
3. [Cache Line (Block)](#cache-line-block)
4. [Address Decomposition](#address-decomposition)
5. [Cache Organization](#cache-organization)
6. [Replacement Policies](#replacement-policies)
7. [Write Policies](#write-policies)
8. [Python Simulator](#python-simulator)

---

## What is a Cache?

A **cache** is a small, fast memory located close to the CPU that stores copies of frequently accessed data from main memory (DRAM). The goal is to reduce average memory access time by exploiting:

- **Temporal locality**: Recently accessed data is likely to be accessed again soon
- **Spatial locality**: Data near recently accessed data is likely to be accessed soon

### Memory Hierarchy

```
Register File      ~1 cycle     ~KB
   ↓
L1 Cache          ~4 cycles     32-64 KB
   ↓
L2 Cache          ~12 cycles    256KB-1MB
   ↓
L3 Cache          ~40 cycles    8-32MB (shared)
   ↓
Main Memory       ~200 cycles   8-64GB
   ↓
SSD/HDD           ~100,000 cycles  TB
```

**Key insight**: Each level is ~10x larger and ~10x slower than the one above it.

---

## Why Do We Need Caches?

### The Memory Wall Problem

```
CPU Speed Growth:     ~55% per year (historically)
Memory Speed Growth:  ~7% per year

Result: Growing gap between CPU and memory speed!
```

Without caches, the CPU would spend most of its time waiting for data from slow DRAM.

### Example: Cache Impact

```
Without L1 Cache:
- Every load/store: 200 cycles to DRAM
- CPI (Cycles Per Instruction) increases dramatically

With L1 Cache (95% hit rate):
- 95% of accesses: 1 cycle (hit)
- 5% of accesses: 200 cycles (miss)
- Average: 0.95×1 + 0.05×200 = 10.95 cycles
- 18× speedup!
```

---

## Cache Line (Block)

A **cache line** (or block) is the **minimum unit of data** transferred between cache and memory.

### Typical Cache Line Size: 64 bytes

Why 64 bytes?
- ✅ Exploits spatial locality (nearby data loaded together)
- ✅ Amortizes tag storage overhead
- ❌ Too large → wasted bandwidth (false sharing in multicore)
- ❌ Too small → more tag storage, more misses

### Example: Cache Line

```
Memory Address:  0x00401000
Cache Line:      0x00401000 - 0x0040103F (64 bytes)

If you access 0x00401004, the entire line [0x00401000:0x0040103F] is loaded.
Next access to 0x00401008? Hit! (already in cache)
```

---

## Address Decomposition

Every memory address is divided into three parts for cache lookup:

```
┌─────────────┬──────────────┬─────────────┐
│     Tag     │    Index     │   Offset    │
└─────────────┴──────────────┴─────────────┘
```

### Field Sizes

```
Offset bits = log₂(block_size)
Index bits  = log₂(num_sets)
Tag bits    = address_bits - index_bits - offset_bits
```

### Example: 32-bit address, 4KB cache, 64B lines, 4-way set-associative

```
Total sets = cache_size / (block_size × associativity)
           = 4096 / (64 × 4)
           = 16 sets

Offset bits = log₂(64) = 6 bits
Index bits  = log₂(16) = 4 bits
Tag bits    = 32 - 4 - 6 = 22 bits

Address: 0xABCD1234
Binary:  10101011 11001101 0001 001000 110100
         └─────Tag─────┘ └Idx┘ └─Offset─┘
```

---

## Cache Organization

### 1. Direct-Mapped Cache (1-way)

Each memory block maps to **exactly one** cache line.

```
Set index = (address / block_size) % num_sets

Pros: Simple, fast
Cons: Conflict misses (two addresses → same set)
```

**Diagram**:
```
Memory Block 0  →  Cache Set 0
Memory Block 1  →  Cache Set 1
Memory Block 2  →  Cache Set 2
...
Memory Block 8  →  Cache Set 0  (conflict!)
```

### 2. Fully Associative Cache

A block can go in **any** cache line.

```
Pros: No conflict misses (maximum flexibility)
Cons: Expensive (must search all entries)
Use case: Small caches (TLB)
```

### 3. N-Way Set Associative Cache

Compromise: A block can go in any of N lines within a set.

```
Typical: 4-way or 8-way

Pros: Reduced conflict misses vs direct-mapped
      Faster search than fully associative
Cons: More complex
```

**Example: 4-way Set Associative**
```
                Set 0
         ┌───────────────────┐
Block 0  → Way0 Way1 Way2 Way3
Block 4  → Way0 Way1 Way2 Way3
Block 8  → Way0 Way1 Way2 Way3
         └───────────────────┘
                Set 1
         ┌───────────────────┐
Block 1  → Way0 Way1 Way2 Way3
Block 5  → Way0 Way1 Way2 Way3
         └───────────────────┘
```

---

## Replacement Policies

When a set is full, which line should be evicted?

### 1. LRU (Least Recently Used)

Evict the line that hasn't been accessed for the longest time.

```
Pros: Good performance (exploits temporal locality)
Cons: Requires tracking access order
```

**Example**:
```
Access sequence: A, B, C, D, E (with 4-way set, same set)

Initial: [   ,    ,    ,    ]
A:       [ A ,    ,    ,    ]
B:       [ A , B ,    ,    ]
C:       [ A , B , C ,    ]
D:       [ A , B , C , D ]
E:       [ E , B , C , D ]  ← A evicted (LRU)
```

### 2. FIFO (First-In-First-Out)

Evict the oldest line (by insertion time).

```
Pros: Simple to implement
Cons: Doesn't consider usage patterns
```

### 3. Random

Randomly pick a line to evict.

```
Pros: Simplest, no state needed
Cons: Unpredictable
```

### 4. LFU (Least Frequently Used)

Evict the line accessed the fewest times.

```
Pros: Good for some workloads
Cons: Expensive to track, old data never evicted
```

**In practice**: Modern CPUs use pseudo-LRU or tree-based approximations of LRU.

---

## Write Policies

What happens when the CPU writes to a cached location?

### Write-Hit Policies

**1. Write-Through**
- Update both cache and memory immediately
- Pros: Memory always consistent
- Cons: Slow (every write goes to memory)

**2. Write-Back**
- Update only cache, mark line as "dirty"
- Write to memory only when evicted
- Pros: Fast (fewer memory writes)
- Cons: Memory inconsistent temporarily

### Write-Miss Policies

**1. Write-Allocate**
- Load the block into cache, then write
- Common with write-back

**2. No-Write-Allocate**
- Write directly to memory, don't load into cache
- Common with write-through

### Dirty Bit

A **dirty bit** (modified bit) per cache line indicates if the line has been written to.

```
Dirty = 0: Cache line matches memory (clean)
Dirty = 1: Cache line modified, memory stale (dirty)

On eviction of dirty line → must write back to memory
```

---

## Cache Performance Metrics

### Hit Rate & Miss Rate

```
Hit Rate = (Number of hits) / (Total accesses)
Miss Rate = 1 - Hit Rate
```

### AMAT (Average Memory Access Time)

```
AMAT = Hit_Time + (Miss_Rate × Miss_Penalty)

Example:
  Hit time = 1 cycle
  Miss rate = 5%
  Miss penalty = 200 cycles
  
  AMAT = 1 + (0.05 × 200) = 11 cycles
```

### Miss Types

1. **Compulsory (Cold) Miss**: First access to a block
2. **Capacity Miss**: Cache too small to hold working set
3. **Conflict Miss**: Multiple blocks map to same set (not fully associative)

---

## Python Simulator

See [`cache_simulator.py`](./cache_simulator.py) for a complete implementation.

### Features

- ✅ Configurable cache size, associativity, block size
- ✅ LRU replacement policy
- ✅ Dirty bit tracking
- ✅ Write-back policy
- ✅ Visual output showing tag/index/offset decomposition
- ✅ Hit/miss statistics

### Command Line Usage

The cache simulator supports comprehensive command line arguments:

```bash
# View help
python cache_simulator.py --help

# Run with default settings (4KB, 4-way, 64B blocks)
python cache_simulator.py

# Configure cache properties
python cache_simulator.py --size 8192 --associativity 8 --block-size 128

# Enable debug mode to see cache structure breakdown
python cache_simulator.py --debug

# Run built-in demonstrations
python cache_simulator.py --demos

# Interactive mode for manual testing
python cache_simulator.py --interactive

# Quiet mode (suppress verbose output)
python cache_simulator.py --quiet
```

#### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--size` | `-s` | Total cache size in bytes | 4096 (4KB) |
| `--associativity` | `-a` | Number of ways | 4 |
| `--block-size` | `-b` | Cache line size in bytes | 64 |
| `--address-bits` | | Address bus width in bits | 32 |
| `--debug` | `-d` | Print cache structure breakdown | False |
| `--demos` | | Run built-in demonstrations | False |
| `--interactive` | `-i` | Interactive mode | False |
| `--quiet` | `-q` | Suppress verbose output | False |

#### Command Line Examples

```bash
# Example 1: View cache structure for 8KB cache
python cache_simulator.py --size 8192 --debug

# Example 2: Direct-mapped cache (1-way)
python cache_simulator.py --size 4096 --associativity 1 --demos

# Example 3: Large cache with bigger blocks
python cache_simulator.py --size 32768 --block-size 128 --associativity 8 --debug

# Example 4: Fully associative (high associativity)
python cache_simulator.py --size 4096 --associativity 64 --demos

# Example 5: 64-bit address space
python cache_simulator.py --address-bits 64 --size 65536 --debug

# Example 6: Interactive mode with custom cache
python cache_simulator.py --size 2048 --associativity 2 --interactive

# Example 7: Run demos with quiet output
python cache_simulator.py --demos --quiet

# Example 8: Combine multiple options
python cache_simulator.py -s 16384 -a 4 -b 64 --debug --demos
```

#### Debug Mode

Debug mode shows detailed cache structure:
- Address bit layout (tag/index/offset)
- Cache organization details
- Bit field breakdown with ranges
- Example address decompositions
- Cache array structure table
- Address mapping formulas

### Python API Usage

```python
from cache_simulator import Cache

# Create a 4KB, 4-way set-associative cache with 64-byte lines
cache = Cache(size=4096, associativity=4, block_size=64)

# Simulate memory accesses
cache.read(0x00401000)   # Miss (cold start)
cache.read(0x00401004)   # Hit (same cache line)
cache.write(0x00401008)  # Hit, sets dirty bit

# Print statistics
cache.print_stats()
```

### Example Output

```
=== Cache Access: READ 0x00401000 ===
Tag:    0x010040  (bits 31:10)
Index:  0x00      (bits 9:6)
Offset: 0x00      (bits 5:0)

Result: MISS (cold start)
Action: Load from memory → Set 0, Way 0

Cache State (Set 0):
Way  Valid  Dirty  Tag        LRU
0    1      0      0x010040   0    ← Just loaded
1    0      0      -          -
2    0      0      -          -
3    0      0      -          -

Statistics:
  Reads:  1  (Hits: 0, Misses: 1)
  Writes: 0  (Hits: 0, Misses: 0)
  Hit Rate: 0.00%
```

---

## Key Formulas Summary

| Formula | Description |
|---------|-------------|
| `num_sets = cache_size / (block_size × associativity)` | Number of sets in cache |
| `offset_bits = log₂(block_size)` | Bits for byte offset within block |
| `index_bits = log₂(num_sets)` | Bits to select set |
| `tag_bits = address_bits - index_bits - offset_bits` | Remaining bits for tag |
| `AMAT = hit_time + miss_rate × miss_penalty` | Average memory access time |

---

## Common Interview Questions

1. **Why is cache line size typically 64 bytes?**
   - Balances spatial locality exploitation vs. bandwidth waste

2. **What's the difference between write-through and write-back?**
   - Write-through: updates memory immediately (slow, consistent)
   - Write-back: updates memory on eviction (fast, needs dirty bit)

3. **Why use set-associative instead of direct-mapped?**
   - Reduces conflict misses while keeping hardware reasonable

4. **What is a dirty bit?**
   - Tracks if cache line has been modified (needs write-back on eviction)

5. **How does LRU work in a 4-way set?**
   - Tracks access order, evicts least recently used way

---

## Next Steps

✅ Run `cache_simulator.py` to see caches in action  
✅ Experiment with different configurations (size, associativity, block size)  
✅ Move to [Module 02: VIPT/PIPT/VIVT](../02_VIPT_PIPT_VIVT/README.md) to learn about virtual vs physical indexing

---

**📌 Key Takeaway**: Caches exploit locality to bridge the speed gap between CPU and memory. Understanding tag/index/offset decomposition is fundamental to all cache analysis!

