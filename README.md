# Memory Hierarchy Educational Repository 🧠

**A comprehensive, hands-on guide to understanding Caches, TLBs, Page Walks, VIPT, and Synonym Problems**

---

## 📚 About This Repository

This repository provides a structured, professional, and deeply educational exploration of modern computer memory hierarchy concepts. It is designed for:

- Computer Architecture students
- Systems engineers
- Hardware engineers preparing for technical interviews
- Anyone wanting to deeply understand how CPUs interact with memory

Each module includes:
- ✅ **Detailed theory** with explanations, formulas, and diagrams
- ✅ **Working Python simulators** to visualize concepts
- ✅ **Real-world examples** and performance implications
- ✅ **Interview preparation** questions and answers

---

## 🗂️ Repository Structure

```
memory_hierarchy_edu/
├── 01_Cache_Basics/              # Cache fundamentals, indexing, LRU, dirty bits
├── 02_VIPT_PIPT_VIVT/            # Cache indexing modes and synonym problems
├── 03_TLB/                       # Translation Lookaside Buffer simulation
├── 04_Page_Walk/                 # Page table walks (RISC-V Sv39 & x86)
├── 05_Performance_Model/         # CPI impact, cache miss penalties
├── 06_WebApp/                    # React-based interactive visualizer (placeholder)
├── 07_Interview_Preparation/     # 50+ curated interview questions
└── diagrams/                     # Visual aids and architecture diagrams
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- (Optional) NumPy for performance modeling

### Installation

```bash
git clone <your-repo-url>
cd memory_hierarchy_edu
pip install -r requirements.txt  # if needed
```

### Quick Start

Run any simulator directly:

```bash
# Cache simulator with LRU eviction
python 01_Cache_Basics/cache_simulator.py

# VIPT vs PIPT visualizer
python 02_VIPT_PIPT_VIVT/vipt_visualizer.py

# TLB simulator with multi-page sizes
python 03_TLB/tlb_simulator.py

# Page walk simulator (RISC-V Sv39)
python 04_Page_Walk/page_walk_sim.py

# Synonym problem demonstrator
python 02_VIPT_PIPT_VIVT/synonym_demo.py
```

---

## 📖 Learning Path

We recommend following this order:

### 1. **Cache Basics** (Module 01)
   - What is a cache line?
   - Cache indexing: tag, index, offset
   - Associativity (direct-mapped, set-associative, fully-associative)
   - Replacement policies (LRU, FIFO, Random)
   - Dirty bits and write-back vs write-through

### 2. **VIPT/PIPT/VIVT** (Module 02)
   - Virtual vs Physical indexing/tagging
   - Why L1 caches are often VIPT
   - The synonym (aliasing) problem
   - VIPT rule: index bits ≤ page offset bits
   - Cache coloring

### 3. **Translation Lookaside Buffer** (Module 03)
   - TLB organization (fully associative)
   - Multi-page size support (4KB, 2MB, 1GB)
   - TLB hit/miss behavior
   - TLB reach and coverage

### 4. **Page Table Walks** (Module 04)
   - Multi-level page tables
   - RISC-V Sv39 format
   - x86-64 4-level paging
   - Step-by-step VA → PA translation
   - Page fault handling

### 5. **Performance Modeling** (Module 05)
   - CPI impact of cache misses
   - Memory access time breakdown
   - Effective memory access time (EMAT)
   - TLB miss penalties

### 6. **Interview Preparation** (Module 07)
   - 50+ curated questions
   - Detailed answers with diagrams
   - Common pitfalls and misconceptions

---

## 🎯 Key Concepts Covered

| Concept | Description |
|---------|-------------|
| **Cache Line** | Fixed-size block of data (typically 64 bytes) |
| **Tag/Index/Offset** | Three components of a memory address for cache lookup |
| **Associativity** | Number of ways a cache line can be placed |
| **LRU** | Least Recently Used replacement policy |
| **VIPT** | Virtually Indexed, Physically Tagged |
| **Synonyms** | Multiple virtual addresses mapping to same physical address |
| **TLB** | Cache for virtual-to-physical address translations |
| **Page Walk** | Multi-level lookup to translate VA to PA |
| **Sv39** | RISC-V 39-bit virtual addressing with 3-level page tables |
| **Huge Pages** | 2MB or 1GB pages for reduced TLB pressure |

---

## 🔬 Simulators Overview

### Cache Simulator
- Configurable size, associativity, block size
- Visual representation of cache state
- Hit/miss tracking with detailed statistics
- LRU eviction visualization
- Dirty bit management

### TLB Simulator
- Fully associative TLB
- Multi-page-size support
- VA → PA translation with breakdown
- TLB miss handling

### Page Walk Simulator
- Supports RISC-V Sv39 and x86-64
- Step-by-step page table lookup
- Visual representation of each level
- Physical address computation

### VIPT Visualizer
- Shows index bit selection from VA vs PA
- Demonstrates when synonyms can occur
- Validates VIPT safety rule
- Compares VIPT, PIPT, VIVT side-by-side

### Synonym Demonstrator
- Creates two VAs mapping to same PA
- Shows potential data corruption scenarios
- Demonstrates how VIPT avoids aliasing
- Shows VIVT synonym problem

---

## 📊 Example Output

```
=== Cache Access: 0x00401234 ===
Tag:    0x0010    (bits 31:14)
Index:  0x048     (bits 13:6)
Offset: 0x34      (bits 5:0)

Result: MISS (cold start)
Eviction: None
Loading from memory...
Cache state updated.
```

---

## 🤝 Contributing

This is an educational project. Contributions are welcome:

- Add more examples
- Improve documentation
- Add support for other architectures (ARM, MIPS)
- Enhance visualizations
- Report issues or suggest improvements

---

## 📚 References and Further Reading

### Books
- *Computer Architecture: A Quantitative Approach* by Hennessy & Patterson
- *Computer Organization and Design* by Patterson & Hennessy
- *Modern Processor Design* by Shen & Lipasti

### Online Resources
- [RISC-V Privileged Spec](https://riscv.org/technical/specifications/)
- [Intel Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation/)

### Papers
- "Virtual Memory Mapped Endian Neutral Shared Memory" (HP Labs)
- "The Alpha 21264 Microprocessor" (Compaq)
- "Virtually Addressed Caches" (Various)

---

## 🎓 Educational Philosophy

This repository follows these principles:

1. **Hands-on learning**: Every concept has a working simulator
2. **Visual explanations**: Diagrams and ASCII art for clarity
3. **Progressive complexity**: Start simple, build to advanced topics
4. **Real-world relevance**: Connect theory to actual CPUs (ARM, x86, RISC-V)
5. **Interview readiness**: Prepare for technical discussions

---

## 📝 License

MIT License - Feel free to use for educational purposes.

---

## ✨ Author

Created as a comprehensive educational resource for understanding memory hierarchy in modern computer systems.

**Last Updated**: December 2025

---

## 🗺️ Roadmap

- [x] Core simulators (Cache, TLB, Page Walk)
- [x] VIPT/PIPT/VIVT visualization
- [x] Interview questions
- [ ] React-based web interface
- [ ] ARM architecture support
- [ ] Multi-core cache coherence (MESI protocol)
- [ ] Prefetching strategies
- [ ] Cache compression techniques

---

**Ready to dive deep into memory hierarchy? Start with [Module 01: Cache Basics](./01_Cache_Basics/README.md)!** 🚀

