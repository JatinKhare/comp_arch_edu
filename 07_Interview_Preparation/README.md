# Module 07: Interview Preparation 💼

## Overview

This module contains **50+ curated interview questions** covering cache, TLB, page walks, VIPT, and memory hierarchy concepts. Each question includes:
- ✅ Detailed answer with explanations
- ✅ Diagrams where helpful
- ✅ Common pitfalls and misconceptions
- ✅ Real-world examples

---

## 📚 Table of Contents

1. [Cache Basics (Questions 1-15)](#cache-basics-questions-1-15)
2. [VIPT/PIPT/VIVT (Questions 16-25)](#viptpiptvivt-questions-16-25)
3. [TLB (Questions 26-35)](#tlb-questions-26-35)
4. [Page Walks (Questions 36-45)](#page-walks-questions-36-45)
5. [Performance Analysis (Questions 46-55)](#performance-analysis-questions-46-55)
6. [Advanced Topics (Questions 56-60)](#advanced-topics-questions-56-60)

---

## Cache Basics (Questions 1-15)

### Q1: What is a cache line and why is it typically 64 bytes?

**Answer:**
A **cache line** (or block) is the minimum unit of data transferred between cache and memory. It's typically 64 bytes because:

1. **Spatial Locality**: Programs often access nearby data. Loading 64 bytes amortizes the cost of fetching from memory.
2. **Tag Overhead**: Larger lines reduce tag storage overhead per byte.
3. **Balance**: Too small → more tag overhead, more misses. Too large → wasted bandwidth, false sharing in multicore.

**Example**: Accessing `array[i]` loads `array[i]` through `array[i+63]` into cache. Accessing `array[i+1]` is a hit!

---

### Q2: Explain tag, index, and offset in cache addressing.

**Answer:**
Every memory address is decomposed into three parts:

```
Address: [Tag | Index | Offset]

Tag:    Identifies which block (compared with cache line tags)
Index:  Selects which set in set-associative cache
Offset: Byte within the cache line
```

**Example**: 32-bit address, 4KB cache, 64B lines, 4-way:
- Offset bits = log₂(64) = 6 bits
- Sets = 4096 / (64 × 4) = 16 sets
- Index bits = log₂(16) = 4 bits
- Tag bits = 32 - 4 - 6 = 22 bits

Address `0x00401234`:
- Tag = `0x010040` (bits 31:10)
- Index = `0x0` (bits 9:6)
- Offset = `0x34` (bits 5:0)

---

### Q3: What's the difference between direct-mapped, set-associative, and fully-associative caches?

**Answer:**

| Type | Organization | Pros | Cons |
|------|-------------|------|------|
| **Direct-mapped** | 1-way (1 line per set) | Simple, fast | Conflict misses |
| **Set-associative** | N-way (N lines per set) | Reduced conflicts | More complex |
| **Fully-associative** | All lines in one set | No conflicts | Expensive (must search all) |

**Example**: 4-way set-associative means each set has 4 possible locations for a block, reducing conflicts vs direct-mapped while being faster than fully-associative.

---

### Q4: How does LRU (Least Recently Used) replacement work?

**Answer:**
LRU evicts the cache line that hasn't been accessed for the longest time.

**Implementation**: Track access order (counters or linked list).

**Example**:
```
4-way set, same set:
Access A → [A, _, _, _]
Access B → [A, B, _, _]
Access C → [A, B, C, _]
Access D → [A, B, C, D]
Access E → [E, B, C, D]  ← A evicted (LRU)
Access B → [E, B, C, D]  ← B updated (now MRU)
```

**Real CPUs**: Use pseudo-LRU (tree-based) for efficiency.

---

### Q5: What is a dirty bit and when is it used?

**Answer:**
A **dirty bit** (modified bit) indicates a cache line has been written to and differs from memory.

**Write-back policy**:
- Write → update cache, set dirty bit
- Eviction → if dirty, write back to memory; if clean, just invalidate

**Example**:
```
1. Read 0x1000 → cache loads, dirty=0
2. Write 0x1000 → cache updated, dirty=1
3. Evict → must write back to memory (dirty=1)
```

**Without dirty bit**: Would write back every eviction (wasteful).

---

### Q6: What are the three types of cache misses?

**Answer:**

1. **Compulsory (Cold) Miss**: First access to a block
   - Unavoidable, even with infinite cache
   
2. **Capacity Miss**: Cache too small to hold working set
   - Would be hit with larger cache
   
3. **Conflict Miss**: Multiple blocks map to same set (not fully-associative)
   - Would be hit with higher associativity

**Example**: 
- Compulsory: First access to new page
- Capacity: Array larger than cache
- Conflict: Two addresses with same index, different tags

---

### Q7: Explain write-through vs write-back policies.

**Answer:**

**Write-Through**:
- Update cache AND memory immediately
- Pros: Memory always consistent, simpler
- Cons: Every write goes to memory (slow)

**Write-Back**:
- Update only cache, mark dirty
- Write to memory only on eviction
- Pros: Fewer memory writes (faster)
- Cons: Memory temporarily inconsistent, needs dirty bit

**Real-world**: L1 caches often write-through for simplicity; L2/L3 use write-back.

---

### Q8: What is cache associativity and why does it matter?

**Answer:**
**Associativity** = number of ways (cache lines per set).

**Impact**:
- Higher associativity → fewer conflict misses
- But: More complex hardware (must search multiple ways)

**Example**: 
- Direct-mapped (1-way): Simple but conflicts
- 4-way: Good balance (most L1 caches)
- Fully-associative: No conflicts but expensive (used for small TLBs)

---

### Q9: How do you calculate the number of sets in a cache?

**Answer:**

```
Number of Sets = Cache_Size / (Block_Size × Associativity)

Example:
  Cache size = 32 KB = 32768 bytes
  Block size = 64 bytes
  Associativity = 4-way
  
  Sets = 32768 / (64 × 4) = 128 sets
```

**Why**: Each set holds `associativity` blocks, so total blocks = sets × associativity.

---

### Q10: What is spatial locality and how do caches exploit it?

**Answer:**
**Spatial locality**: Data near recently accessed data is likely to be accessed soon.

**Caches exploit it** by loading entire cache lines (64 bytes) on a miss.

**Example**:
```c
for (int i = 0; i < 1000; i++) {
    sum += array[i];  // Accessing consecutive elements
}
```
Accessing `array[0]` loads `array[0..63]` into cache. Next 63 accesses are hits!

---

### Q11: What is temporal locality and how do caches exploit it?

**Answer:**
**Temporal locality**: Recently accessed data is likely to be accessed again soon.

**Caches exploit it** by keeping recently accessed data in fast cache.

**Example**:
```c
for (int i = 0; i < 1000; i++) {
    for (int j = 0; j < 1000; j++) {
        result += matrix[i][j];  // Accessing same row repeatedly
    }
}
```
After first iteration, `matrix[0]` is in cache → subsequent accesses hit.

---

### Q12: Explain the concept of cache hit rate and miss rate.

**Answer:**

```
Hit Rate = Hits / Total Accesses
Miss Rate = Misses / Total Accesses = 1 - Hit Rate
```

**Example**:
- 1000 accesses, 950 hits, 50 misses
- Hit rate = 95%
- Miss rate = 5%

**Typical values**:
- L1: 95-99% hit rate
- L2: 80-95% hit rate
- L3: 50-80% hit rate

---

### Q13: What is AMAT (Average Memory Access Time)?

**Answer:**

```
AMAT = Hit_Time + Miss_Rate × Miss_Penalty

Example:
  Hit time = 1 cycle
  Miss rate = 5%
  Miss penalty = 200 cycles
  
  AMAT = 1 + 0.05 × 200 = 11 cycles
```

**Interpretation**: Average time to access memory through this cache level.

---

### Q14: How does cache size affect performance?

**Answer:**

**Larger cache**:
- ✅ More capacity → fewer capacity misses
- ❌ Longer hit time (more ways to search)
- ❌ More expensive

**Optimal size**: Balance between hit rate and hit time.

**Example**: 
- 32 KB L1: Fast (1 cycle), good hit rate (95%)
- 256 KB L1: Slower (2 cycles), better hit rate (98%)
- Net: Often worse due to slower hit time!

---

### Q15: What is a victim cache?

**Answer:**
A **victim cache** is a small fully-associative cache holding recently evicted L1 lines.

**Purpose**: Reduce conflict misses.

**Example**:
```
L1 conflict miss → evict line A
Victim cache → check if A is there → hit! (fast recovery)

Typical: 4-16 entries, removes 20-40% of conflict misses
```

---

## VIPT/PIPT/VIVT (Questions 16-25)

### Q16: What is VIPT and why is it common in L1 caches?

**Answer:**
**VIPT** = Virtually Indexed, Physically Tagged.

- **Index from VA**: Fast (no TLB needed for set selection)
- **Tag from PA**: Correct (avoids context switch issues)

**Why common**: Combines speed (parallel TLB/cache lookup) with correctness (PA tags).

**Example**: Modern Intel/ARM L1 caches are VIPT.

---

### Q17: What is the synonym problem?

**Answer:**
**Synonym (aliasing) problem**: Multiple virtual addresses map to the same physical address, but cache treats them as different locations.

**Occurs in**: VIVT caches (different VA tags → different cache lines).

**Example**:
```
VA1 = 0x1000 → PA = 0x5000
VA2 = 0x2000 → PA = 0x5000 (same physical memory!)

VIVT cache:
  VA1 → Cache Set X (Tag=0x1)
  VA2 → Cache Set Y (Tag=0x2)
  
Result: Two copies of same data → stale data bug!
```

---

### Q18: What is the VIPT safety rule?

**Answer:**

```
For VIPT to avoid synonyms:
    index_bits ≤ page_offset_bits

For 4KB pages (12-bit offset):
    index_bits ≤ 12
```

**Why**: Index bits must come from page offset (same in VA and PA).

**Example**: 32 KB cache, 4-way, 64B lines:
- Sets = 128 → index_bits = 7
- 7 ≤ 12 ✅ SAFE

---

### Q19: Compare VIVT, PIPT, and VIPT.

**Answer:**

| Mode | Index | Tag | Speed | Synonym? | Context Switch |
|------|-------|-----|-------|----------|---------------|
| **VIVT** | VA | VA | Very Fast | Yes ❌ | Flush needed ❌ |
| **PIPT** | PA | PA | Slow | No ✅ | No flush ✅ |
| **VIPT** | VA | PA | Fast | No* ✅ | No flush ✅ |

*VIPT safe if index_bits ≤ page_offset_bits

**Real-world**: L1=VIPT, L2/L3=PIPT

---

### Q20: How does VIPT avoid the synonym problem?

**Answer:**
VIPT uses **PA tags**, so even if two VAs map to the same PA, they have the same tag.

**If index comes from page offset** (VIPT safety rule):
- Same page offset → same index → same set
- Same PA tag → same tag → same cache line
- ✅ No synonym!

**Example**:
```
VA1 = 0x00401234, PA = 0x12345234
VA2 = 0x00502234, PA = 0x12345234 (same PA!)

Page offset = 0x234 (same!)
Index from offset → same set
PA tag → same tag
→ Same cache line ✅
```

---

### Q21: What happens if VIPT violates the safety rule?

**Answer:**
If `index_bits > page_offset_bits`, some index bits come from VPN (not page offset).

**Result**: Different VAs to same PA could map to different sets → synonym problem!

**Solution**: 
1. Use PIPT (slower but safe)
2. Increase associativity (reduces sets → reduces index bits)
3. Use larger pages (more offset bits)
4. OS-level cache coloring

---

### Q22: What is cache coloring?

**Answer:**
**Cache coloring**: OS technique to prevent synonyms by controlling VA allocation.

**Idea**: Ensure synonyms have matching "color" (VA bits used for cache indexing beyond page offset).

**Example**:
```
Index bits = [13:6]
Color = VA[13:12] (bits beyond page offset)

OS rule: If VA1 and VA2 → same PA, then VA1[13:12] = VA2[13:12]
```

**Trade-off**: Restricts VA space but allows larger VIPT caches.

---

### Q23: Why are L2 and L3 caches usually PIPT?

**Answer:**

1. **Size**: L2/L3 are larger → would violate VIPT safety rule
2. **Speed less critical**: Already slower (10-40 cycles)
3. **Multi-core coherence**: Easier with physical addresses

**Example**: 256 KB L2, 4-way, 64B lines:
- Sets = 1024 → index_bits = 10
- With 4KB pages: 10 ≤ 12 ✅ Could be VIPT
- But: Larger caches (1MB+) need PIPT

---

### Q24: What is a homonym problem?

**Answer:**
**Homonym**: Same virtual address in different processes maps to different physical addresses.

**Problem in VIVT**: Same VA tag → same cache line → wrong data!

**Example**:
```
Process A: VA=0x1000 → PA=0x5000
Process B: VA=0x1000 → PA=0x7000 (different!)

VIVT cache: Both use same tag → conflict!
```

**Solution**: VIPT uses PA tags (unique) → no homonym problem.

---

### Q25: How do you calculate if a VIPT cache is safe?

**Answer:**

```
1. Calculate number of sets:
   Sets = Cache_Size / (Block_Size × Associativity)

2. Calculate index bits:
   index_bits = log₂(Sets)

3. Get page offset bits:
   page_offset_bits = log₂(Page_Size)

4. Check safety:
   if index_bits ≤ page_offset_bits:
       SAFE ✅
   else:
       UNSAFE ❌ (synonym possible)
```

**Example**: 64 KB cache, 8-way, 64B lines, 4KB pages:
- Sets = 128 → index_bits = 7
- page_offset_bits = 12
- 7 ≤ 12 ✅ SAFE

---

## TLB (Questions 26-35)

### Q26: What is a TLB and why is it needed?

**Answer:**
**TLB** (Translation Lookaside Buffer) = cache for page table entries (VA→PA translations).

**Why needed**: Page table walks are expensive (4 memory accesses for 4-level paging = 800 cycles).

**Benefit**: 95% hit rate → average translation time = 1 cycle instead of 800!

---

### Q27: Why are TLBs fully associative?

**Answer:**
TLBs are small (64-512 entries) → fully associative is feasible.

**Benefits**:
- No conflict misses (any entry can hold any translation)
- Maximum flexibility

**Trade-off**: Must search all entries (parallel comparison in hardware).

---

### Q28: What happens on a TLB miss?

**Answer:**

**Hardware-managed (x86, ARM)**:
1. CPU hardware page walker walks page tables
2. Loads PTE into TLB
3. Retries instruction (now TLB hit)

**Software-managed (RISC-V, MIPS)**:
1. Raise exception (trap to OS)
2. OS walks page tables in software
3. OS writes TLB entry (tlbwr instruction)
4. Return from exception
5. Retry instruction

---

### Q29: What is TLB reach?

**Answer:**
**TLB Reach** = Total memory coverage of all TLB entries.

```
TLB Reach = Num_Entries × Page_Size

Example:
  64 entries × 4KB = 256 KB
  64 entries × 2MB = 128 MB
```

**Larger reach** → fewer TLB misses for large working sets.

---

### Q30: How do huge pages improve TLB performance?

**Answer:**

**Problem**: Small pages → many pages → many TLB misses

**Solution**: Use larger pages (2MB, 1GB) → fewer pages → better TLB coverage

**Example**:
```
Working set: 128 MB

With 4KB pages:
  Pages needed: 32,768
  TLB (64 entries): covers 256 KB
  Miss rate: 99.2%! 💥

With 2MB pages:
  Pages needed: 64
  TLB (64 entries): covers 128 MB
  Miss rate: 0% ✅
```

---

### Q31: What is TLB shootdown?

**Answer:**
**TLB Shootdown**: Invalidating TLB entries across multiple CPU cores.

**When needed**: Page table changes (munmap, mprotect) → all cores must invalidate stale entries.

**Process**:
1. Core A changes page table
2. Send IPI (Inter-Processor Interrupt) to all cores
3. All cores invalidate TLB entry
4. Wait for acknowledgment

**Cost**: Expensive (~1000 cycles per core).

---

### Q32: What are the components of a TLB entry?

**Answer:**

- **VPN** (Virtual Page Number): Tag for lookup
- **PPN** (Physical Page Number): Translation result
- **Page Size**: 4KB, 2MB, 1GB, etc.
- **Flags**: 
  - Valid, Read, Write, Execute
  - User, Global, Accessed, Dirty

**Size**: ~8-16 bytes per entry.

---

### Q33: How does TLB size affect performance?

**Answer:**

**Larger TLB**:
- ✅ More entries → higher reach → fewer misses
- ❌ More expensive (fully associative → longer critical path)

**Typical sizes**:
- L1 TLB: 64-128 entries (fast, small)
- L2 TLB: 512-2048 entries (larger, slightly slower)

**Balance**: Larger L2 TLB compensates for small L1.

---

### Q34: What is the difference between ITLB and DTLB?

**Answer:**

- **ITLB** (Instruction TLB): Caches translations for instruction fetches
- **DTLB** (Data TLB): Caches translations for data accesses

**Why separate**: Can be optimized independently (ITLB often larger, simpler).

**Example**: Intel Core i7:
- ITLB: 128 entries (4KB)
- DTLB: 64 entries (4KB) + 32 entries (2MB)

---

### Q35: How do you calculate TLB miss penalty?

**Answer:**

```
TLB Miss Penalty = Page_Walk_Time

For 4-level page table:
  Page_Walk_Time = 4 × Memory_Access_Time
                 = 4 × 200 cycles
                 = 800 cycles

Average Translation Time:
  = TLB_Hit_Time × Hit_Rate + Page_Walk_Time × Miss_Rate
  = 1 × 0.95 + 800 × 0.05
  = 40.95 cycles
```

---

## Page Walks (Questions 36-45)

### Q36: Why use multi-level page tables instead of single-level?

**Answer:**

**Single-level problem**: Huge page table (4 MB for 32-bit, 512 GB for 64-bit).

**Multi-level solution**: Only allocate page tables for used memory regions (sparse).

**Example**:
- Single-level: 4 MB always allocated
- Multi-level: ~20 KB typically allocated (only for used pages)

**Trade-off**: More memory accesses per translation (but TLB hides this).

---

### Q37: How many memory accesses for a 4-level page walk?

**Answer:**

**4 memory accesses** (one per level):
1. Read PML4 entry
2. Read PDPT entry
3. Read PD entry
4. Read PT entry

**Plus**: 1 access for actual data = **5 total accesses**.

**Cost**: 4 × 200 cycles = 800 cycles (without TLB).

---

### Q38: Explain RISC-V Sv39 page table format.

**Answer:**

**Sv39**: 39-bit virtual addresses, 3-level page tables.

**Address format**:
```
[VPN2(9) | VPN1(9) | VPN0(9) | Offset(12)]
```

**Each level**: 512 entries (2^9), 8-byte PTEs.

**Page sizes**: 4KB (all 3 levels), 2MB (stop at L1), 1GB (stop at L2).

---

### Q39: What is a leaf PTE?

**Answer:**
A **leaf PTE** is a page table entry that completes translation (doesn't point to another level).

**RISC-V**: Leaf if R, W, or X bit is set.

**x86-64**: Leaf if Present=1 and PS (Page Size) bit indicates final level.

**Example**: 2MB huge page → PTE at PD level is leaf (doesn't use PT level).

---

### Q40: What happens on a page fault?

**Answer:**

**Causes**:
1. Non-present page (not allocated)
2. Permission violation (write to read-only)
3. Invalid address

**Handling**:
1. CPU saves context (PC, fault address, error code)
2. Jump to page fault handler (OS)
3. OS determines cause and handles:
   - Allocate page (demand paging)
   - Load from swap (swap-in)
   - Send signal (protection fault)
4. Return from exception
5. Retry instruction

---

### Q41: How do huge pages reduce page walk depth?

**Answer:**

**Normal 4KB page**: Requires all 4 levels (x86) or 3 levels (RISC-V).

**2MB huge page**: Stops at PD level (x86) or L1 level (RISC-V) → 3 levels instead of 4.

**1GB huge page**: Stops at PDPT level (x86) or L2 level (RISC-V) → 2 levels instead of 4.

**Benefit**: Fewer memory accesses → faster page walk.

---

### Q42: What is the difference between hardware and software page walks?

**Answer:**

| Feature | Hardware (x86, ARM) | Software (RISC-V, MIPS) |
|---------|---------------------|-------------------------|
| **Speed** | Faster (~20 cycles) | Slower (~100 cycles) |
| **Flexibility** | Fixed format | OS-defined format |
| **Complexity** | More HW | Simpler HW |

**Hardware**: CPU automatically walks page tables.
**Software**: TLB miss → exception → OS walks → writes TLB.

---

### Q43: How do you construct a physical address from a PTE?

**Answer:**

```
Physical Address = (PPN << page_offset_bits) | page_offset

Example (RISC-V Sv39):
  PTE.PPN = 0x12345
  Page offset = 0x234 (from VA)
  
  PA = (0x12345 << 12) | 0x234
     = 0x12345000 | 0x234
     = 0x12345234
```

**Key**: PPN is shifted left by page offset bits, then combined with offset.

---

### Q44: What are page table entry flags?

**Answer:**

**Common flags**:
- **V/P (Valid/Present)**: Entry is valid
- **R (Read)**: Page is readable
- **W (Write)**: Page is writable
- **X (Execute)**: Page is executable
- **U (User)**: User-mode accessible
- **A (Accessed)**: Page has been accessed
- **D (Dirty)**: Page has been written

**Usage**: OS uses A/D for page replacement (LRU), swap decisions.

---

### Q45: How does page table size scale with address space?

**Answer:**

**Single-level**: Scales linearly with address space size.

**Multi-level**: Scales with **used** memory (sparse).

**Example**:
- 32-bit, 4KB pages: Single-level = 4 MB
- 32-bit, 4KB pages: Multi-level = ~20 KB (typical usage)
- 64-bit, 4KB pages: Single-level = 512 GB (impossible!)
- 64-bit, 4KB pages: Multi-level = ~100 KB (typical usage)

---

## Performance Analysis (Questions 46-55)

### Q46: How do you calculate effective CPI including memory stalls?

**Answer:**

```
Effective CPI = Base CPI + Instruction Stalls + Data Stalls

Instruction Stalls = Inst_per_Instr × Inst_Miss_Rate × Miss_Penalty
Data Stalls = Data_per_Instr × Data_Miss_Rate × Miss_Penalty

Example:
  Base CPI = 1.0
  Inst/instr = 1.0, Inst MR = 5%, Penalty = 100 cycles
  Data/instr = 0.3, Data MR = 5%, Penalty = 100 cycles
  
  CPI = 1.0 + 1.0×0.05×100 + 0.3×0.05×100
     = 1.0 + 5 + 1.5
     = 7.5 cycles
```

---

### Q47: What's more important: reducing miss rate or miss penalty?

**Answer:**

**Depends on current values**, but typically **miss rate** has bigger impact.

**Example**:
- Reducing MR by 1% at 200cy penalty: saves 2 cycles
- Reducing penalty by 10 cycles at 5% MR: saves 0.5 cycles

**Rule of thumb**: Focus on miss rate first (bigger impact).

---

### Q48: How do you calculate speedup from cache improvements?

**Answer:**

```
Speedup = Time_Old / Time_New

Example:
  Old: AMAT = 11 cycles
  New: AMAT = 5.2 cycles
  
  Speedup = 11 / 5.2 = 2.12×
```

**Interpretation**: New system is 2.12× faster.

---

### Q49: What is the impact of TLB misses on performance?

**Answer:**

**TLB miss penalty**: 20-800 cycles (page walk).

**Impact**:
```
Without TLB: Every access = 800 cycles (page walk)
With TLB (95% hit): Average = 1×0.95 + 800×0.05 = 40.95 cycles

Speedup: 800 / 40.95 = 19.5×
```

**Key**: TLB misses are VERY expensive → high hit rate critical!

---

### Q50: How do you model multi-level cache performance?

**Answer:**

```
EMAT = L1_Hit_Time
       + L1_Miss_Rate × (L2_Hit_Time
       + L2_Miss_Rate × (L3_Hit_Time
       + L3_Miss_Rate × Memory_Time))

Example:
  L1: 1 cycle, 5% miss
  L2: 12 cycles, 20% miss (of L1 misses)
  L3: 40 cycles, 10% miss (of L2 misses)
  Memory: 200 cycles
  
  EMAT = 1 + 0.05×(12 + 0.20×(40 + 0.10×200))
       = 1 + 0.05×(12 + 0.20×60)
       = 1 + 0.05×24
       = 2.2 cycles
```

---

### Q51: What is local vs global miss rate?

**Answer:**

**Local Miss Rate**: Misses at this level / Accesses to this level

**Global Miss Rate**: Misses at this level / Total accesses

**Example**:
```
L1: 1000 accesses, 50 misses → Local MR = 5%
L2: 50 accesses, 10 misses   → Local MR = 20%

Global L1 MR = 50/1000 = 5%
Global L2 MR = 10/1000 = 1%
```

**Use**: Global MR for overall performance, Local MR for level-specific analysis.

---

### Q52: How does prefetching improve performance?

**Answer:**

**Prefetching**: Load data into cache before it's needed.

**Sequential prefetcher**: On miss, prefetch next N cache lines.

**Example**:
```
Without prefetch: 100% miss rate for streaming → 100 cycles/access
With prefetch: 10% miss rate → 10 cycles/access

Speedup: 10×
```

**Trade-off**: Prefetch accuracy matters (wrong prefetches waste bandwidth).

---

### Q53: What is the impact of cache line size on performance?

**Answer:**

**Larger lines**:
- ✅ Better spatial locality → fewer misses
- ❌ More bandwidth waste (if not all data used)
- ❌ More false sharing (multicore)

**Optimal**: Typically 64 bytes (balance).

**Example**: 
- 32 bytes: More misses, less waste
- 64 bytes: Good balance ✅
- 128 bytes: Fewer misses, more waste

---

### Q54: How do you calculate IPC from CPI?

**Answer:**

```
IPC (Instructions Per Cycle) = 1 / CPI

Example:
  CPI = 2.0
  IPC = 1 / 2.0 = 0.5
  
  At 3 GHz: Throughput = 0.5 × 3 GHz = 1.5 billion instructions/sec
```

**Higher IPC** = better performance.

---

### Q55: What is the combined impact of cache and TLB misses?

**Answer:**

**Four cases**:
1. TLB hit, Cache hit: Fast (2 cycles)
2. TLB hit, Cache miss: Cache penalty (201 cycles)
3. TLB miss, Cache hit: TLB penalty (801 cycles)
4. TLB miss, Cache miss: Both penalties (1000 cycles)

**Average** (95% TLB hit, 95% cache hit):
```
= 0.95×0.95×2 + 0.95×0.05×201 + 0.05×0.95×801 + 0.05×0.05×1000
= 1.805 + 9.548 + 38.048 + 2.5
= 51.9 cycles
```

**Key**: TLB misses dominate (even with cache hits)!

---

## Advanced Topics (Questions 56-60)

### Q56: What is cache coherence and why is it needed?

**Answer:**

**Cache coherence**: Ensuring all cores see consistent view of memory.

**Problem**: Multiple cores have copies of same data → writes must propagate.

**Example**:
```
Core 0: Reads X → cache
Core 1: Reads X → cache
Core 0: Writes X → only Core 0's cache updated!
Core 1: Reads X → sees stale data! 💥
```

**Solution**: MESI protocol (Modified, Exclusive, Shared, Invalid).

---

### Q57: Explain the MESI cache coherence protocol.

**Answer:**

**States**:
- **M (Modified)**: Dirty, only this core has it
- **E (Exclusive)**: Clean, only this core has it
- **S (Shared)**: Clean, multiple cores have it
- **I (Invalid)**: Not in cache

**Transitions**:
- Read miss → Request from other cores → S or E
- Write → Invalidate others → M
- Other core writes → Invalidate this → I

**Goal**: Ensure only one M copy exists.

---

### Q58: What is false sharing?

**Answer:**

**False sharing**: Two variables in same cache line, different cores modify different variables.

**Problem**: Cache line ping-pongs between cores (coherence overhead).

**Example**:
```c
struct {
    int x;  // Core 0 writes
    int y;  // Core 1 writes
} data;  // Same cache line!

Result: Cache line invalidated repeatedly → performance degradation
```

**Solution**: Pad variables to different cache lines.

---

### Q59: What is non-uniform memory access (NUMA)?

**Answer:**

**NUMA**: Memory access time depends on location (local vs remote).

**Architecture**: Each CPU has local memory + access to remote memory.

**Example**:
```
CPU 0: Local memory = 100 ns
CPU 0: Remote memory (CPU 1's) = 300 ns

Impact: Affinity matters (keep data near CPU using it)
```

**Optimization**: NUMA-aware allocation (numactl).

---

### Q60: How do you optimize memory access patterns?

**Answer:**

**Techniques**:
1. **Blocking/Tiling**: Access data in blocks (fits in cache)
2. **Prefetching**: Load data before needed
3. **Huge pages**: Reduce TLB misses
4. **NUMA awareness**: Keep data local to CPU
5. **Avoid false sharing**: Pad shared data structures

**Example**: Matrix multiplication → blocked version 10× faster!

---

## Summary

These 60 questions cover:
- ✅ Cache fundamentals (15 questions)
- ✅ VIPT/PIPT/VIVT (10 questions)
- ✅ TLB (10 questions)
- ✅ Page walks (10 questions)
- ✅ Performance analysis (10 questions)
- ✅ Advanced topics (5 questions)

**Study Tips**:
1. Understand the concepts, not just memorize answers
2. Draw diagrams for complex topics
3. Practice calculations (EMAT, CPI, etc.)
4. Know real-world examples (Intel, ARM, RISC-V)
5. Understand trade-offs (speed vs correctness, size vs hit rate)

**Good luck with your interviews!** 🚀

