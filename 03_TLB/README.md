# Module 03: Translation Lookaside Buffer (TLB) 🔄

## Overview

The **Translation Lookaside Buffer (TLB)** is a specialized cache that stores recent virtual-to-physical address translations. It's critical for performance because page table walks are expensive (multiple memory accesses).

This module covers:
- TLB organization and operation
- Multi-page-size support (4KB, 2MB, 1GB)
- TLB reach and coverage
- TLB miss handling
- Performance impact

---

## 📚 Table of Contents

1. [What is a TLB?](#what-is-a-tlb)
2. [Why TLBs are Critical](#why-tlbs-are-critical)
3. [TLB Organization](#tlb-organization)
4. [TLB Lookup Process](#tlb-lookup-process)
5. [Multi-Page-Size Support](#multi-page-size-support)
6. [TLB Reach and Coverage](#tlb-reach-and-coverage)
7. [TLB Miss Handling](#tlb-miss-handling)
8. [TLB Shootdown](#tlb-shootdown)
9. [Real-World Examples](#real-world-examples)
10. [Python Simulator](#python-simulator)

---

## What is a TLB?

The **TLB** is a small, fast cache for page table entries (PTEs).

```
Virtual Address → [TLB] → Physical Address
                    ↓
              Hit? Fast!
                    ↓
              Miss? Page Walk (slow)
```

### Key Characteristics

- **Size**: 64-512 entries (much smaller than caches)
- **Organization**: Fully associative or set-associative
- **Latency**: 1-2 cycles
- **Miss penalty**: 20-200 cycles (page table walk)

### TLB vs Cache

| Feature | TLB | Cache |
|---------|-----|-------|
| **Purpose** | VA → PA translation | Store data |
| **Size** | 64-512 entries | 32KB - 32MB |
| **Organization** | Fully associative | Set-associative |
| **Entry Size** | ~8-16 bytes | 64 bytes |
| **Coverage** | 256KB - 2GB | 32KB - 32MB |
| **Miss Penalty** | Page walk (20-200 cycles) | Memory access (200+ cycles) |

---

## Why TLBs are Critical

### Problem: Page Table Walks are Expensive

Without a TLB, **every memory access** requires a page table walk!

```
Example: 4-level page table (x86-64)

Single memory access:
  1. Read L4 page table
  2. Read L3 page table
  3. Read L2 page table
  4. Read L1 page table
  5. Finally, read actual data

Result: 5 memory accesses instead of 1! (5× slowdown)
```

### Solution: TLB Caches Translations

```
With TLB (95% hit rate):

  95% of accesses: 1 cycle (TLB hit)
  5% of accesses: ~100 cycles (TLB miss → page walk)
  
Average: 0.95×1 + 0.05×100 = 5.95 cycles

Without TLB: 100 cycles average

→ 16× speedup! 🚀
```

---

## TLB Organization

### Fully Associative TLB

Most TLBs are **fully associative**: any entry can hold any translation.

```
┌─────────────────────────────────────┐
│  TLB (Fully Associative)           │
├─────┬─────┬─────┬──────┬───────────┤
│ Way │Valid│ VPN │ PPN  │ Flags     │
├─────┼─────┼─────┼──────┼───────────┤
│  0  │  1  │0x123│0xABC │R,W,X,D,A  │
│  1  │  1  │0x456│0xDEF │R,X        │
│  2  │  1  │0x789│0x111 │R,W        │
│ ... │ ... │ ... │ ...  │ ...       │
│ 63  │  0  │  -  │  -   │ -         │
└─────┴─────┴─────┴──────┴───────────┘
```

### Entry Contents

Each TLB entry contains:
- **VPN** (Virtual Page Number): Tag for lookup
- **PPN** (Physical Page Number): Translation result
- **Flags**: Permission and status bits
  - **V** (Valid): Entry is valid
  - **R** (Read): Readable
  - **W** (Write): Writable
  - **X** (Execute): Executable
  - **D** (Dirty): Page has been written to
  - **A** (Accessed): Page has been accessed
  - **U** (User): User-mode accessible
  - **G** (Global): Don't flush on context switch

### Page Size Field

For multi-page-size TLBs:
- **Page Size**: 4KB, 2MB, 1GB, etc.
- Determines how many address bits are offset vs page number

---

## TLB Lookup Process

### Step-by-Step

```
1. Extract VPN from virtual address
   VA = [VPN | Page Offset]
   
2. Search TLB for matching VPN (parallel comparison)
   
3a. TLB Hit:
    - Get PPN from TLB entry
    - Check permission bits
    - If OK: PA = [PPN | Page Offset]
    - Done! (1-2 cycles)
    
3b. TLB Miss:
    - Trigger page table walk
    - Load PTE into TLB
    - Evict old entry if full (LRU)
    - Retry translation
    - Done! (20-200 cycles)
```

### Diagram: TLB Hit

```
Virtual Address: 0x00401234

┌────────────────────────┬────────────┐
│   VPN = 0x00401        │ Offset=0x234│
└────────────────────────┴────────────┘
         ↓
    [TLB Lookup]
         ↓
   Found: VPN=0x00401 → PPN=0x12345
         ↓
┌────────────────────────┬────────────┐
│   PPN = 0x12345        │ Offset=0x234│
└────────────────────────┴────────────┘

Physical Address: 0x12345234
```

### Diagram: TLB Miss

```
Virtual Address: 0x00501234

┌────────────────────────┬────────────┐
│   VPN = 0x00501        │ Offset=0x234│
└────────────────────────┴────────────┘
         ↓
    [TLB Lookup]
         ↓
     NOT FOUND!
         ↓
    [Page Table Walk]
    ├─ Read L4 entry
    ├─ Read L3 entry
    ├─ Read L2 entry
    └─ Read L1 entry → PPN=0xABCDE
         ↓
    [Insert into TLB]
    VPN=0x00501 → PPN=0xABCDE
         ↓
┌────────────────────────┬────────────┐
│   PPN = 0xABCDE        │ Offset=0x234│
└────────────────────────┴────────────┘

Physical Address: 0xABCDE234
```

---

## Multi-Page-Size Support

Modern CPUs support multiple page sizes:

| Page Size | Linux Name | Use Case | TLB Reach (64 entries) |
|-----------|-----------|----------|------------------------|
| **4 KB** | Base page | Default | 256 KB |
| **2 MB** | Huge page | Databases, VMs | 128 MB |
| **1 GB** | Giant page | Large datasets | 64 GB |

### Why Multiple Page Sizes?

```
Problem with 4KB pages:
  64-entry TLB covers only 64 × 4KB = 256KB
  
  Large application (1GB working set):
    Needs 262,144 PTEs
    TLB can hold only 64
    → 99.98% TLB miss rate! 💥
    
Solution: Use 2MB huge pages
  64 entries × 2MB = 128MB coverage
  1GB working set:
    Needs only 512 PTEs
    TLB holds 64 → ~88% hit rate ✅
```

### Multi-Level TLB

Modern CPUs have separate TLBs:

```
┌─────────────────┐
│  Instruction    │  L1 ITLB: 64-128 entries (4KB pages)
│  TLB (ITLB)     │
└─────────────────┘

┌─────────────────┐
│  Data TLB       │  L1 DTLB: 64-128 entries (4KB + 2MB pages)
│  (DTLB)         │
└─────────────────┘

┌─────────────────┐
│  L2 TLB         │  L2 TLB: 512-2048 entries (all sizes)
│  (Unified)      │
└─────────────────┘
```

### Example: Intel Core i7

```
L1 DTLB:
  - 64 entries for 4KB pages
  - 32 entries for 2MB/4MB pages
  
L1 ITLB:
  - 128 entries for 4KB pages
  - 8 entries for 2MB/4MB pages
  
L2 TLB (unified):
  - 1536 entries for 4KB pages
  - 16 entries for 1GB pages
```

---

## TLB Reach and Coverage

### TLB Reach

**TLB Reach** = Total memory coverage of all TLB entries

```
TLB Reach = (Num Entries) × (Page Size)

Example 1: 64 entries, 4KB pages
  Reach = 64 × 4KB = 256KB
  
Example 2: 64 entries, 2MB pages
  Reach = 64 × 2MB = 128MB
  
Example 3: Mixed
  32 × 4KB + 32 × 2MB = 128KB + 64MB ≈ 64MB
```

### Improving TLB Reach

1. **Increase TLB Size**
   - ❌ Expensive (fully associative → long critical path)
   
2. **Use Larger Pages**
   - ✅ 2MB huge pages common
   - ✅ 1GB for extreme cases
   - ❌ Increases internal fragmentation
   
3. **Multi-Level TLB**
   - ✅ L1 TLB: small, fast
   - ✅ L2 TLB: large, slightly slower

---

## TLB Miss Handling

### Hardware Page Walk (x86, ARM)

CPU automatically walks page tables on TLB miss.

```
1. TLB miss detected
2. Hardware page walker:
   - Reads page table base (CR3 on x86)
   - Follows page table levels
   - Loads PTE
3. Insert PTE into TLB
4. Retry instruction (now TLB hit)
```

### Software Page Walk (RISC-V, MIPS)

TLB miss triggers exception → OS handles it.

```
1. TLB miss detected
2. Raise exception (trap to OS)
3. OS exception handler:
   - Walks page table in software
   - Loads PTE
   - Writes TLB entry (tlbwr instruction)
4. Return from exception
5. Retry instruction (now TLB hit)
```

### Comparison

| Feature | Hardware Walk (x86) | Software Walk (RISC-V) |
|---------|---------------------|------------------------|
| **Speed** | Faster (~20 cycles) | Slower (~100 cycles) |
| **Flexibility** | Fixed format | OS-defined format |
| **Complexity** | More HW | Simpler HW |

---

## TLB Shootdown

**TLB Shootdown**: Invalidating TLB entries across multiple cores.

### When Needed

```
Scenario: Process frees a page

Core 0: munmap(0x1000) → page no longer valid
        ↓
Core 1: Still has TLB entry: 0x1000 → 0xABCD
        ↓
Core 1: Uses stale translation! 💥 Bug!

Solution: TLB Shootdown
  1. Core 0 sends Inter-Processor Interrupt (IPI)
  2. All cores invalidate TLB entry for VA 0x1000
  3. Core 0 continues
```

### Implementation

```c
// Pseudo-code for TLB shootdown
void invalidate_tlb_global(va_t virtual_address) {
    // Invalidate local TLB
    tlb_invalidate_local(virtual_address);
    
    // Send IPI to all other cores
    for_each_cpu(cpu) {
        if (cpu != current_cpu()) {
            send_ipi(cpu, TLB_SHOOTDOWN, virtual_address);
        }
    }
    
    // Wait for acknowledgment
    wait_for_all_acks();
}
```

### Cost

TLB shootdown is **expensive**:
- IPI latency: ~1000 cycles
- Synchronization overhead
- Stalls other cores

**Optimization**: Batch shootdowns, use global bit

---

## Real-World Examples

### x86-64 (Intel Core i7)

```
L1 DTLB:
  - 64 entries (4KB)
  - 32 entries (2MB/4MB)
  
L2 TLB:
  - 1536 entries (4KB)
  - 16 entries (1GB)

Total Reach: ~6.5 MB (4KB) + ~80 MB (large pages)
```

### ARM Cortex-A53

```
Unified TLB:
  - 512 entries
  - Supports 4KB, 64KB, 1MB, 16MB, 1GB pages
  
Fully associative
LRU replacement
```

### RISC-V (SiFive U74)

```
L1 TLB:
  - 40 entries (Instruction)
  - 40 entries (Data)
  
Fully associative
Software-managed (OS handles misses)
Supports 4KB, 2MB, 1GB (Sv39)
```

---

## Python Simulator

See [`tlb_simulator.py`](./tlb_simulator.py) for a complete implementation.

### Features

- ✅ Fully associative TLB
- ✅ Multi-page-size support (4KB, 2MB, 1GB)
- ✅ LRU replacement
- ✅ Permission checking (R/W/X)
- ✅ TLB miss simulation with page walk
- ✅ Statistics (hit rate, reach)

### Usage Example

```python
from tlb_simulator import TLB, PageSize

# Create TLB with 64 entries
tlb = TLB(num_entries=64)

# Simulate address translation
pa = tlb.translate(va=0x00401000, page_size=PageSize.KB_4)

# Print statistics
tlb.print_stats()
```

### Example Output

```
=== TLB Translation: VA=0x00401000 ===
VPN: 0x00401
TLB Miss! Initiating page walk...
Page walk result: PPN=0x12345
Inserting into TLB...

Physical Address: 0x12345000

TLB Statistics:
  Accesses:   1000
  Hits:       950 (95.00%)
  Misses:     50 (5.00%)
  TLB Reach:  256 KB (64 × 4KB pages)
```

---

## Performance Impact

### Example Calculation

```
System:
  TLB hit time: 1 cycle
  Page walk time: 100 cycles
  TLB hit rate: 95%

Average translation time:
  0.95 × 1 + 0.05 × 100 = 5.95 cycles

If hit rate drops to 80%:
  0.80 × 1 + 0.20 × 100 = 20.8 cycles
  → 3.5× slower!
```

### Improving TLB Performance

1. **Use Huge Pages**
   - 2MB pages → 512× fewer TLB entries needed
   
2. **Optimize Memory Layout**
   - Keep hot data in fewer pages
   
3. **TLB-Aware Scheduling**
   - Avoid unnecessary context switches
   
4. **Global Pages**
   - Kernel mappings stay in TLB across switches

---

## Key Formulas

| Formula | Description |
|---------|-------------|
| `TLB Reach = Entries × Page Size` | Total memory coverage |
| `VPN = VA >> page_offset_bits` | Extract virtual page number |
| `PA = (PPN << page_offset_bits) | offset` | Construct physical address |
| `ATAT = hit_time + miss_rate × walk_time` | Average translation access time |

---

## Interview Questions

1. **What is the purpose of the TLB?**
   - Caches VA→PA translations to avoid expensive page table walks

2. **Why are TLBs fully associative?**
   - Small size makes it feasible; avoids conflict misses

3. **What happens on a TLB miss?**
   - Hardware or software page table walk, load PTE, evict old entry

4. **How do huge pages improve performance?**
   - Increase TLB reach (64 × 2MB = 128MB vs 64 × 4KB = 256KB)

5. **What is TLB shootdown?**
   - Invalidating TLB entries across multiple cores (expensive!)

---

## Next Steps

✅ Run `tlb_simulator.py` to see TLB in action  
✅ Experiment with different page sizes  
✅ Move to [Module 04: Page Walk](../04_Page_Walk/README.md) to see detailed translation

---

**📌 Key Insight**: The TLB is critical for performance! A 95% hit rate is typical, but workloads with large memory footprints benefit greatly from huge pages.

