# Diagrams and Visual Aids 📊

This folder contains visual aids and diagrams for the memory hierarchy educational repository.

## Placeholder Images

The following diagrams are referenced in the documentation but are placeholders for future development:

### Cache Diagrams
- `cache_indexing.png` - Address decomposition (tag/index/offset)
- `cache_organization.png` - Direct-mapped vs set-associative vs fully-associative
- `cache_line_structure.png` - Cache line layout with valid/dirty bits

### VIPT/PIPT/VIVT Diagrams
- `vipt_vs_pipt.png` - Comparison of indexing modes
- `vipt_parallel_lookup.png` - Parallel TLB and cache lookup
- `synonym_problem.png` - Visual demonstration of aliasing

### TLB Diagrams
- `tlb_structure.png` - TLB organization (fully associative)
- `tlb_reach.png` - TLB coverage with different page sizes
- `tlb_shootdown.png` - Multi-core TLB invalidation

### Page Walk Diagrams
- `page_walk_sv39.png` - RISC-V Sv39 3-level page walk
- `page_walk_x86.png` - x86-64 4-level page walk
- `page_table_structure.png` - Multi-level page table tree

### Performance Diagrams
- `memory_hierarchy.png` - Complete memory hierarchy pyramid
- `cpi_breakdown.png` - CPI components and stalls
- `amat_calculation.png` - Effective memory access time

## ASCII Diagrams

For now, ASCII diagrams are included directly in the README files. Future versions may include:
- Interactive SVG diagrams
- Animated GIFs showing cache operations
- PDF versions for printing

## Contributing

If you'd like to contribute diagrams:
1. Use vector formats (SVG preferred)
2. Keep diagrams clear and educational
3. Include labels and annotations
4. Match the style of existing documentation

## Tools for Creating Diagrams

Recommended tools:
- **Draw.io** (diagrams.net) - Free, web-based
- **TikZ** (LaTeX) - Programmatic diagrams
- **Inkscape** - Vector graphics editor
- **Mermaid** - Text-based diagramming

