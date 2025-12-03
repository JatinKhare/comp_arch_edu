# Module 04: Page Table Walks 🚶

## Overview

This module explains **page table walks** - the process of translating a virtual address to a physical address by traversing multi-level page tables. We cover both **RISC-V Sv39** (3-level) and **x86-64** (4-level) page table formats.

---

## 📚 Table of Contents

1. [Why Multi-Level Page Tables?](#why-multi-level-page-tables)
2. [RISC-V Sv39 Format](#risc-v-sv39-format)
3. [x86-64 4-Level Paging](#x86-64-4-level-paging)
4. [Step-by-Step Page Walk](#step-by-step-page-walk)
5. [Page Faults](#page-faults)
6. [Optimization Techniques](#optimization-techniques)
7. [Python Simulator](#python-simulator)

---

## Why Multi-Level Page Tables?

### Problem with Single-Level Page Tables

For 32-bit address space with 4KB pages:
```
Virtual address: 32 bits
Page size: 4KB (12-bit offset)
VPN: 32 - 12 = 20 bits

Number of pages: 2^20 = 1,048,576 pages
PTE size: 4 bytes

Page table size: 1M × 4B = 4 MB per process! 😱
```

For 64-bit (48-bit used):
```
VPN: 48 - 12 = 36 bits
Number of pages: 2^36 = 68 billion pages
Page table size: 68B × 8B = 512 GB per process! 💥
```

### Solution: Multi-Level (Hierarchical) Page Tables

Idea: Only allocate page tables for memory regions actually used!

```
Single-level: Flat array (wasteful)
[PTE0][PTE1][PTE2]...[PTE_1M]  ← 4 MB always allocated

Multi-level: Tree structure (sparse)
        Root
       /    \
     L2      L2   ← Only allocate branches needed
    /  \    /
  L1  L1  L1
  
Typical usage: ~20 KB (vs 4 MB)
```

---

## RISC-V Sv39 Format

**Sv39**: 39-bit virtual addresses, 3-level page tables

### Address Format

```
Virtual Address (39 bits):

┌────────┬────────┬────────┬──────────────┐
│  VPN2  │  VPN1  │  VPN0  │ Page Offset  │
│ [38:30]│ [29:21]│ [20:12]│   [11:0]     │
│ 9 bits │ 9 bits │ 9 bits │   12 bits    │
└────────┴────────┴────────┴──────────────┘
    │        │        │            │
    │        │        │            └─ Byte within page (4KB)
    │        │        └──────────────  Level 0 index (512 entries)
    │        └───────────────────────  Level 1 index (512 entries)
    └────────────────────────────────  Level 2 index (512 entries)
```

### Page Table Entry (PTE) Format

64-bit PTE:
```
┌──────────┬───────┬───┬───┬───┬───┬───┬───┬───┬───┐
│   PPN    │  RSW  │ D │ A │ G │ U │ X │ W │ R │ V │
│ [53:10]  │ [9:8] │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 │
└──────────┴───────┴───┴───┴───┴───┴───┴───┴───┴───┘

Flags:
  V (Valid):     1 = entry is valid
  R (Read):      1 = readable
  W (Write):     1 = writable
  X (Execute):   1 = executable
  U (User):      1 = user-accessible
  G (Global):    1 = global mapping (all address spaces)
  A (Accessed):  1 = page has been accessed
  D (Dirty):     1 = page has been written to
  RSW:           Reserved for software use
  PPN:           Physical Page Number (44 bits)
```

### Special Cases

**Leaf PTE**: R, W, or X bit is set → translation complete
**Non-leaf PTE**: R=W=X=0 → pointer to next level

### Page Walk Algorithm

```
1. Start with satp register (page table base)
2. Extract VPN[2] → index into level 2 table
3. Read PTE:
   - If invalid (V=0): Page fault
   - If leaf (R/W/X set): Done! (2MB superpage)
   - Otherwise: pointer to level 1 table
4. Extract VPN[1] → index into level 1 table
5. Read PTE:
   - If invalid: Page fault
   - If leaf: Done! (4MB megapage)
   - Otherwise: pointer to level 0 table
6. Extract VPN[0] → index into level 0 table
7. Read PTE:
   - If invalid: Page fault
   - If leaf: Done! (4KB page)
8. Construct PA: PPN from PTE + page offset from VA
```

---

## x86-64 4-Level Paging

**x86-64**: 48-bit virtual addresses, 4-level page tables

### Address Format

```
Virtual Address (48 bits, sign-extended to 64):

┌────────┬────────┬────────┬────────┬──────────────┐
│  PML4  │  PDPT  │   PD   │   PT   │ Page Offset  │
│ [47:39]│ [38:30]│ [29:21]│ [20:12]│   [11:0]     │
│ 9 bits │ 9 bits │ 9 bits │ 9 bits │   12 bits    │
└────────┴────────┴────────┴────────┴──────────────┘
    │        │        │        │            │
    │        │        │        │            └─ Byte within page
    │        │        │        └──────────────  Page Table (512 entries)
    │        │        └───────────────────────  Page Directory (512 entries)
    │        └────────────────────────────────  Page Dir Pointer Table (512 entries)
    └─────────────────────────────────────────  Page Map Level 4 (512 entries)
```

### Page Table Entry (PTE) Format

64-bit PTE:
```
┌──────────┬─────────────┬─┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│   PPN    │   Reserved  │NX│ G │PAT│ D │ A │PCD│PWT│U/S│R/W│ P │
│ [51:12]  │  [63:52]    │63│ 8 │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 │
└──────────┴─────────────┴─┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

Flags:
  P (Present):        1 = entry is present
  R/W (Read/Write):   1 = writable, 0 = read-only
  U/S (User/Super):   1 = user, 0 = supervisor
  PWT (Write-Through):1 = write-through cache
  PCD (Cache Disable):1 = disable cache
  A (Accessed):       1 = page accessed
  D (Dirty):          1 = page written
  PAT (Page Attr):    Page attribute table
  G (Global):         1 = global page
  NX (No Execute):    1 = non-executable
  PPN:                Physical Page Number (40 bits)
```

### Page Sizes

x86-64 supports multiple page sizes:
- **4 KB**: Normal pages (all 4 levels)
- **2 MB**: Large pages (stop at PD, set PS bit)
- **1 GB**: Huge pages (stop at PDPT, set PS bit)

### Page Walk Algorithm

```
1. Start with CR3 register (PML4 base)
2. Extract PML4 index → read PML4 entry
   - If P=0: Page fault
3. Extract PDPT index → read PDPT entry
   - If P=0: Page fault
   - If PS=1: Done! (1GB page)
4. Extract PD index → read PD entry
   - If P=0: Page fault
   - If PS=1: Done! (2MB page)
5. Extract PT index → read PT entry
   - If P=0: Page fault
6. Construct PA: PPN + page offset
```

---

## Step-by-Step Page Walk

### Example: RISC-V Sv39 Walk

```
Virtual Address: 0x0000003F_C0401234

Binary breakdown:
  VPN[2] = 0x0000000 (bits 38:30) = 0
  VPN[1] = 0x1F (bits 29:21) = 31
  VPN[0] = 0x01 (bits 20:12) = 1
  Offset = 0x234 (bits 11:0) = 564

satp = 0x80000000_00100000 (page table base)

Step 1: Level 2 lookup
  Address: satp + (VPN[2] × 8) = 0x100000 + (0 × 8) = 0x100000
  Read PTE: 0x20044001
    PPN = 0x20044 (bits [53:10])
    Flags: V=1, R=0, W=0, X=0 → Non-leaf, continue

Step 2: Level 1 lookup
  Address: (PPN << 12) + (VPN[1] × 8)
         = (0x20044 << 12) + (31 × 8)
         = 0x20044000 + 248 = 0x200440F8
  Read PTE: 0x30055001
    PPN = 0x30055
    Flags: V=1, R=0, W=0, X=0 → Non-leaf, continue

Step 3: Level 0 lookup
  Address: (0x30055 << 12) + (1 × 8)
         = 0x30055000 + 8 = 0x30055008
  Read PTE: 0x400660CF
    PPN = 0x40066
    Flags: V=1, R=1, W=1, X=1 → Leaf! Translation complete

Step 4: Construct PA
  PA = (PPN << 12) | offset
     = (0x40066 << 12) | 0x234
     = 0x40066234

Result: VA 0x3FC0401234 → PA 0x40066234
```

### Diagram: Multi-Level Lookup

```
        Virtual Address
        0x3FC0401234
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
  VPN[2]=0          Offset=0x234
    │
    ↓
┌─────────┐
│ Level 2 │ satp
│  Entry 0├─────→ PPN=0x20044
└─────────┘              ↓
    VPN[1]=31           PPN << 12
              ↓
          ┌─────────┐
          │ Level 1 │ 0x20044000
          │ Entry 31├─────→ PPN=0x30055
          └─────────┘              ↓
    VPN[0]=1                PPN << 12
              ↓
          ┌─────────┐
          │ Level 0 │ 0x30055000
          │ Entry 1 ├─────→ PPN=0x40066
          └─────────┘              ↓
              Offset=0x234    PPN << 12 | offset
                    ↓              ↓
            Physical Address: 0x40066234
```

---

## Page Faults

**Page Fault**: CPU exception when translation fails

### Causes

1. **Non-present page** (V=0 or P=0)
   - Page not yet allocated
   - Swapped to disk
   
2. **Permission violation**
   - Write to read-only page
   - Execute non-executable page
   - User accessing kernel page
   
3. **Invalid address**
   - Access outside valid address space

### Page Fault Handling

```
1. CPU saves context (PC, fault address, error code)
2. Jump to page fault handler (OS)
3. OS determines cause:
   a) Demand paging: Allocate page, update page table
   b) Swap-in: Load page from disk, update page table
   c) COW: Copy page, update page table
   d) Protection fault: Send SIGSEGV signal to process
4. Return from exception
5. Retry instruction (should succeed now)
```

---

## Optimization Techniques

### 1. TLB (Translation Lookaside Buffer)

Cache recent translations to avoid page walks.

```
Hit rate: 95-99% → Only 1-5% require page walk
```

### 2. Large Pages

Reduce page table levels.

```
1 GB page: Only 2 levels instead of 4
2 MB page: Only 3 levels instead of 4
```

### 3. Page Table Caching

Cache intermediate page table entries.

```
Intel: "Paging-Structure Caches"
- PML4 cache
- PDPT cache
- PD cache
```

### 4. Lazy Allocation

Don't allocate page tables until needed.

### 5. Shared Page Tables

Multiple processes share read-only page tables (e.g., shared libraries).

---

## Python Simulator

See [`page_walk_sim.py`](./page_walk_sim.py) for complete implementations.

### Features

- ✅ RISC-V Sv39 simulation
- ✅ x86-64 4-level paging simulation
- ✅ Step-by-step visualization
- ✅ Multi-level page table structure
- ✅ Permission checking
- ✅ Page fault simulation

### Command Line Usage

```bash
# View help
python page_walk_sim.py --help

# Run all demos
python page_walk_sim.py

# Run specific demo
python page_walk_sim.py --demo sv39
python page_walk_sim.py --demo comparison

# Translate specific address
python page_walk_sim.py --translate 0x401234

# Map and translate
python page_walk_sim.py --map 0x401000 0x12345000 --translate 0x401234
```

#### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--demo` | | Run specific demo (sv39/comparison/all) | None |
| `--translate` | `-t` | Translate a specific virtual address (hex) | None |
| `--map` | | Map VA to PA (both in hex, space-separated) | None |
| `--verbose` | `-v` | Verbose output | True |

#### Command Line Examples

```bash
# Example 1: Run Sv39 page walk demo
python page_walk_sim.py --demo sv39

# Example 2: Run address format comparison demo
python page_walk_sim.py --demo comparison

# Example 3: Run all demos
python page_walk_sim.py --demo all

# Example 4: Translate specific address
python page_walk_sim.py --translate 0x401234

# Example 5: Map VA to PA and then translate
python page_walk_sim.py --map 0x401000 0x12345000 --translate 0x401234

# Example 6: Translate multiple addresses (map first, then translate)
python page_walk_sim.py --map 0x401000 0x12345000
python page_walk_sim.py --translate 0x401234
python page_walk_sim.py --translate 0x401567

# Example 7: Quiet mode (less verbose)
python page_walk_sim.py --translate 0x401234 --no-verbose

# Example 8: Map multiple pages
python page_walk_sim.py --map 0x401000 0x12345000
python page_walk_sim.py --map 0x402000 0x23456000
python page_walk_sim.py --translate 0x401234
```

### Python API Usage

```python
from page_walk_sim import RISCV_Sv39_PageWalker

walker = RISCV_Sv39_PageWalker()

# Setup page tables
walker.map_page(va=0x401000, pa=0x12345000)

# Translate
pa = walker.translate(va=0x401234)
```

---

## Key Formulas

| Formula | Description |
|---------|-------------|
| `VPN = VA >> page_offset_bits` | Extract virtual page number |
| `offset = VA & ((1 << page_offset_bits) - 1)` | Extract page offset |
| `PA = (PPN << page_offset_bits) | offset` | Construct physical address |
| `PTE_addr = table_base + (index × PTE_size)` | Calculate PTE address |

---

## Interview Questions

1. **Why use multi-level page tables instead of single-level?**
   - Sparse address space → only allocate tables for used regions

2. **How many memory accesses for a page walk with 4 levels?**
   - 4 accesses (one per level) + 1 for actual data = 5 total

3. **What's the difference between Sv39 and x86-64 paging?**
   - Sv39: 3 levels, 39-bit VA; x86-64: 4 levels, 48-bit VA

4. **How do huge pages reduce page walk overhead?**
   - Fewer levels to traverse (1GB page: 2 levels vs 4)

5. **What happens on a page fault?**
   - Exception → OS allocates/loads page → updates PTE → retry

---

## Next Steps

✅ Run `page_walk_sim.py` to see step-by-step walks  
✅ Compare RISC-V and x86-64 formats  
✅ Move to [Module 05: Performance Modeling](../05_Performance_Model/README.md)

---

**📌 Key Insight**: Multi-level page tables save memory by exploiting sparse virtual address spaces. TLBs are critical to hide the latency of multi-level walks!

