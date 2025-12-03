# Module 02: VIPT, PIPT, and VIVT Caches 🔍

## Overview

This module explores the critical distinction between **virtual** and **physical** addressing in caches, focusing on:
- **VIVT** (Virtually Indexed, Virtually Tagged)
- **VIPT** (Virtually Indexed, Physically Tagged)
- **PIPT** (Physically Indexed, Physically Tagged)
- The **synonym (aliasing) problem**
- Why modern L1 caches are typically VIPT

---

## 📚 Table of Contents

1. [Virtual vs Physical Memory](#virtual-vs-physical-memory)
2. [The Three Cache Indexing Modes](#the-three-cache-indexing-modes)
3. [VIVT: Virtually Indexed, Virtually Tagged](#vivt-virtually-indexed-virtually-tagged)
4. [PIPT: Physically Indexed, Physically Tagged](#pipt-physically-indexed-physically-tagged)
5. [VIPT: Virtually Indexed, Physically Tagged](#vipt-virtually-indexed-physically-tagged)
6. [The Synonym Problem](#the-synonym-problem)
7. [VIPT Safety Rule](#vipt-safety-rule)
8. [Cache Coloring](#cache-coloring)
9. [Real-World Examples](#real-world-examples)
10. [Python Visualizers](#python-visualizers)

---

## Virtual vs Physical Memory

Modern CPUs use **virtual memory** for isolation, protection, and flexibility.

```
CPU generates: Virtual Address (VA)
Memory uses:   Physical Address (PA)

Translation: VA → (via TLB/Page Table) → PA
```

### Example: 4KB Pages

```
Virtual Address:   0x00401234
Page Number (VPN): 0x00401      (bits 31:12)
Page Offset:       0x234        (bits 11:0)

After translation (assume PA = 0x12345234):
Physical Address:  0x12345234
Page Frame (PPN):  0x12345     (bits 31:12)
Page Offset:       0x234        (bits 11:0)  ← SAME as VA!
```

**Key Insight**: The **page offset bits are identical** in VA and PA!

---

## The Three Cache Indexing Modes

A cache can use VA or PA for two operations:
1. **Indexing**: Selecting which set to look in
2. **Tagging**: Identifying which line matches

This gives us three combinations:

| Mode | Index from | Tag from | Pros | Cons |
|------|-----------|----------|------|------|
| **VIVT** | VA | VA | Fast (no translation needed) | Synonym problem, context switch issues |
| **PIPT** | PA | PA | No aliasing, simple | Slow (needs TLB before cache lookup) |
| **VIPT** | VA | PA | Fast + safe (if designed correctly) | Limited cache size |

---

## VIVT: Virtually Indexed, Virtually Tagged

### How it Works

```
VA → Split into Tag/Index/Offset
      ↓
      Cache Lookup (no translation needed!)
      ↓
      Compare VA Tag
      ↓
      Hit/Miss
```

### Diagram

```
Virtual Address: 0x00401234

┌────────────┬─────────┬────────┐
│  VA Tag    │  Index  │ Offset │
└────────────┴─────────┴────────┘
      ↓            ↓         ↓
   Compare      Select    Byte
   with cache   Set       in line
```

### Advantages

✅ **Very fast**: No TLB lookup needed for cache access  
✅ **Simple**: No coordination between cache and TLB

### Disadvantages

❌ **Synonym problem**: Two VAs can map to same PA  
❌ **Context switch overhead**: Must flush cache on process switch  
❌ **Homonyms**: Same VA in different processes → different data  

### The Synonym Problem in VIVT

```
Process uses two virtual addresses:
VA1 = 0x1000  ───┐
                 ├──→ PA = 0x5000
VA2 = 0x2000  ───┘

Both map to same physical memory but have different VA tags!

VIVT cache stores:
Set 0: Tag=0x1, Data=X    (from VA1)
Set 1: Tag=0x2, Data=?    (from VA2)

Result: Two copies of same physical data!
When VA1 writes, VA2 sees stale data → INCONSISTENCY!
```

### When VIVT is Used

- Rare in modern CPUs (too many problems)
- Sometimes in simple embedded systems
- Early ARM processors (ARM9)

---

## PIPT: Physically Indexed, Physically Tagged

### How it Works

```
VA → TLB Lookup → PA
                   ↓
     Split into Tag/Index/Offset
                   ↓
              Cache Lookup
                   ↓
           Compare PA Tag
                   ↓
              Hit/Miss
```

### Diagram

```
Virtual Address: 0x00401234
         ↓
    [TLB Lookup]
         ↓
Physical Address: 0x12345234

┌────────────┬─────────┬────────┐
│  PA Tag    │  Index  │ Offset │
└────────────┴─────────┴────────┘
      ↓            ↓         ↓
   Compare      Select    Byte
   with cache   Set       in line
```

### Advantages

✅ **No aliasing**: Same PA always has same tag  
✅ **No context switch issues**: Physical addresses unique  
✅ **Simple logic**: No special handling needed  

### Disadvantages

❌ **Slower**: Must wait for TLB before cache lookup  
❌ **Critical path**: TLB → Cache (serial)  

### When PIPT is Used

- L2 and L3 caches (speed less critical)
- Some L1 data caches
- Intel Pentium 4, modern ARM cores (for L2/L3)

---

## VIPT: Virtually Indexed, Physically Tagged

The **"best of both worlds"** approach used in most modern L1 caches!

### How it Works

```
VA → Split into Index/Offset (from VA)
  ↓
  TLB Lookup (for tag) ── parallel with ──→ Cache Set Selection (using VA index)
  ↓                                               ↓
  PA Tag ──────────────────────→ Compare with tags in selected set
                                       ↓
                                   Hit/Miss
```

### Key Insight: **Parallel Operation**

```
         Virtual Address
               │
         ┌─────┴─────┐
         ↓           ↓
    TLB Lookup   Extract Index (from VA)
         │           │
         ↓           ↓
     PA Tag      Select Set
         │           │
         └─────┬─────┘
               ↓
         Compare Tags
               ↓
           Hit/Miss
```

### Advantages

✅ **Fast**: TLB and cache set selection happen in parallel  
✅ **No homonym problem**: Uses PA tag (unique across processes)  
✅ **Most common**: Balanced performance and correctness  

### Disadvantages

❌ **Limited size**: Must follow VIPT safety rule  
⚠️ **Synonym possible** if rule violated  

### Diagram: VIPT Operation

```
Virtual Address: 0x00401234
                      ↓
        ┌─────────────┴──────────────┐
        ↓                            ↓
   [VA Index bits]              [TLB Lookup]
   Select Set 0x48                   ↓
        ↓                     PA Tag: 0x12345
        ↓                            ↓
   ┌────┴────┐                      │
   │ Set 0x48│◄──── Compare PA Tags ┘
   │ Way 0: Tag=0x12345, Valid=1 ── HIT!
   │ Way 1: Tag=...
   └─────────┘
```

---

## The Synonym Problem

**Synonym (Aliasing)**: Multiple virtual addresses map to the same physical address.

### Why Synonyms Exist

```
Use Case 1: Shared Memory
Process A: VA1 = 0x10000 ─┐
                          ├──→ PA = 0x50000 (shared data)
Process B: VA2 = 0x20000 ─┘

Use Case 2: Memory Mapping
Program maps file at two locations:
VA1 = 0x30000 ─┐
               ├──→ PA = 0x60000 (same file page)
VA2 = 0x40000 ─┘
```

### Problem in VIVT

```
Cache indexed by VA:
Set(VA1) ≠ Set(VA2)  (different index bits)

Result: Two cache lines hold the same physical data!

Timeline:
1. CPU reads VA1  → Cache loads PA data into Set X
2. CPU writes VA2 → Cache loads PA data into Set Y, modifies it
3. CPU reads VA1  → Still sees OLD data from Set X!
   
STALE DATA BUG! 💥
```

### Why VIPT Can Avoid It

In VIPT, even if two VAs map to same PA:
- They use the **same PA tag**
- If index bits come from **page offset** (same in VA and PA), they map to the **same set**!

```
VA1 = 0x00401234
VA2 = 0x00502234  (different VPN, same page offset)

Page offset = 0x234 (bits 11:0)
If index bits come from page offset → same index!
If tags use PA → same tag!

Result: Both VAs hit the same cache line → NO SYNONYM! ✅
```

---

## VIPT Safety Rule

### The Golden Rule

**For VIPT to avoid synonyms:**

```
Index bits must come ONLY from page offset bits

Mathematical condition:
    index_bits ≤ page_offset_bits

For 4KB pages:
    page_offset_bits = 12
    → index_bits ≤ 12
```

### Derivation

```
Page size = 4096 bytes = 2^12 bytes
→ Page offset = bits [11:0]

Cache:
    Size = 32 KB
    Block size = 64 bytes = 2^6
    Associativity = 8-way

Number of sets = 32768 / (64 × 8) = 64 sets
Index bits = log₂(64) = 6 bits

Since 6 ≤ 12: SAFE! ✅

Index uses bits [11:6] (from offset) → same in VA and PA
```

### Example: UNSAFE VIPT

```
Cache:
    Size = 128 KB
    Block size = 64 bytes
    Associativity = 4-way

Number of sets = 128K / (64 × 4) = 512 sets
Index bits = log₂(512) = 9 bits

Since 9 ≤ 12: SAFE! ✅

But with 1-way (direct-mapped):
    Sets = 128K / 64 = 2048 sets
    Index bits = 11 bits
    
Still okay: 11 ≤ 12 ✅

But with 256 KB, 64B, direct-mapped:
    Sets = 256K / 64 = 4096 sets
    Index bits = 12 bits
    
Exactly at limit: 12 ≤ 12 ✅

With 512 KB:
    Index bits = 13 bits
    
UNSAFE! 13 > 12 ❌ → Synonym problem possible!
```

### Solutions for Large L1 Caches

If you want L1 > (page_size × associativity):

1. **Use PIPT** (slower but safe)
2. **Increase associativity** (reduces sets, thus index bits)
3. **Use larger pages** (e.g., 2MB huge pages → 21 offset bits)
4. **OS-level cache coloring** (restrict VA allocation)

---

## Cache Coloring

**Cache coloring** is an OS technique to prevent synonyms by controlling VA allocation.

### Concept

```
OS ensures that if two VAs map to same PA, their "color" matches.

Color = VA bits used for cache indexing

Example:
    Index bits = [13:6]
    Color = VA[13:12] (the bits beyond page offset)
    
OS rule: If VA1 and VA2 → same PA, then VA1[13:12] = VA2[13:12]
```

### Implementation

```c
// Kernel allocates virtual memory aligned by cache size
void* allocate_colored(size_t size, int color) {
    uintptr_t mask = (cache_size - 1) & ~(page_size - 1);
    uintptr_t va = allocate_va(size);
    va = (va & ~mask) | (color << 12);
    return (void*)va;
}
```

### Trade-offs

✅ Allows VIPT with larger caches  
❌ Restricts VA space usage  
❌ Increases OS complexity  

---

## Real-World Examples

### ARM Cortex-A53

- **L1 I-Cache**: 32 KB, 2-way, VIPT
  - Sets = 32K / (64 × 2) = 256
  - Index bits = 8 ≤ 12 ✅
- **L1 D-Cache**: 32 KB, 4-way, PIPT
  - Uses physical indexing for multi-core coherence

### Intel Core i7

- **L1**: 32 KB, 8-way, VIPT
  - Sets = 32K / (64 × 8) = 64
  - Index bits = 6 ≤ 12 ✅
- **L2**: 256 KB per core, PIPT
- **L3**: Shared, PIPT

### RISC-V Implementations

- SiFive U74: 32 KB L1, 4-way, VIPT
- Varies by vendor

---

## Python Visualizers

### vipt_visualizer.py

Demonstrates:
- Address decomposition for VIPT, PIPT, VIVT
- Shows when index bits overlap with VPN bits
- Validates VIPT safety rule

#### Command Line Usage

```bash
# View help
python vipt_visualizer.py --help

# Run with default settings
python vipt_visualizer.py

# Custom cache configuration
python vipt_visualizer.py --cache-size 8192 --associativity 8 --block-size 128

# Test with huge pages
python vipt_visualizer.py --page-size 2097152

# Run specific demo only
python vipt_visualizer.py --demo safe
python vipt_visualizer.py --demo unsafe
python vipt_visualizer.py --demo huge
```

#### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--cache-size` | `-s` | Cache size in bytes | 32768 (32KB) |
| `--associativity` | `-a` | Number of ways | 4 |
| `--block-size` | `-b` | Cache block size in bytes | 64 |
| `--page-size` | `-p` | Page size in bytes | 4096 (4KB) |
| `--address-bits` | | Address width in bits | 32 |
| `--demo` | | Run specific demo (safe/unsafe/huge/all) | all |
| `--va` | | Virtual address in hex | 0x00401234 |
| `--pa` | | Physical address in hex | 0x12345234 |

### synonym_demo.py

Simulates:
- Two VAs mapping to same PA
- VIVT cache showing stale data
- VIPT cache avoiding the problem

#### Command Line Usage

```bash
# View help
python synonym_demo.py --help

# Run all demos
python synonym_demo.py

# Run specific demo
python synonym_demo.py --demo vivt
python synonym_demo.py --demo vipt
python synonym_demo.py --demo unsafe
```

#### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--demo` | Run specific demo (vivt/vipt/unsafe/all) | all |
| `--num-sets` | Number of cache sets | 64 |
| `--block-size` | Cache block size in bytes | 64 |

---

## Key Takeaways

| Concept | Summary |
|---------|---------|
| **VIVT** | Fast but has synonym/homonym problems (rare today) |
| **PIPT** | Safe but slower (TLB before cache) |
| **VIPT** | Best of both (if index ≤ offset bits) |
| **Synonym** | Multiple VAs → same PA (can cause stale data) |
| **VIPT Rule** | Index bits ≤ page offset bits for safety |
| **L1 caches** | Usually VIPT (32-64 KB with high associativity) |
| **L2/L3** | Usually PIPT (speed less critical) |

---

## Interview Questions

1. **Why are most L1 caches VIPT instead of PIPT?**
   - Parallelism: TLB lookup and cache set selection happen simultaneously

2. **What is the synonym problem?**
   - Multiple VAs → same PA can map to different cache lines, causing stale data

3. **What's the VIPT safety rule?**
   - Index bits must be ≤ page offset bits (12 for 4KB pages)

4. **Can a 64KB direct-mapped VIPT L1 cache be safe with 4KB pages?**
   - 64K / 64B = 1024 sets → 10 index bits → 10 ≤ 12 ✅ SAFE

5. **How does cache coloring help?**
   - OS restricts VA allocations so synonyms have matching index bits

---

## Next Steps

✅ Run `vipt_visualizer.py` to see address decomposition  
✅ Run `synonym_demo.py` to see aliasing problem  
✅ Move to [Module 03: TLB](../03_TLB/README.md) to understand address translation

---

**📌 Key Insight**: VIPT combines speed (parallel TLB/cache) with correctness (PA tags), making it the dominant choice for modern L1 caches!

