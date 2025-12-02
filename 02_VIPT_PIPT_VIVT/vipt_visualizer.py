"""
VIPT/PIPT/VIVT Cache Visualizer
================================

This module visualizes how different cache indexing schemes work:
- VIVT: Virtually Indexed, Virtually Tagged
- PIPT: Physically Indexed, Physically Tagged  
- VIPT: Virtually Indexed, Physically Tagged

It demonstrates:
- Address decomposition for each mode
- When VIPT is safe (index bits ≤ page offset bits)
- Parallel TLB/cache lookup in VIPT

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Tuple
from dataclasses import dataclass
import math


@dataclass
class AddressBreakdown:
    """Breakdown of an address for cache lookup"""
    address: int
    tag: int
    index: int
    offset: int
    tag_bits: int
    index_bits: int
    offset_bits: int


class VIPTVisualizer:
    """
    Visualizes VIPT, PIPT, and VIVT cache indexing modes.
    
    Helps understand:
    - How virtual vs physical addressing affects cache lookup
    - When synonyms can occur
    - VIPT safety rule
    """
    
    def __init__(
        self,
        cache_size: int = 32768,    # 32 KB
        block_size: int = 64,       # 64 bytes
        associativity: int = 4,     # 4-way
        page_size: int = 4096,      # 4 KB
        address_bits: int = 32      # 32-bit addresses
    ):
        """
        Initialize the visualizer.
        
        Args:
            cache_size: Total cache size in bytes
            block_size: Cache line size in bytes
            associativity: Number of ways
            page_size: Virtual memory page size in bytes
            address_bits: Address width in bits
        """
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.page_size = page_size
        self.address_bits = address_bits
        
        # Calculate cache parameters
        self.num_sets = cache_size // (block_size * associativity)
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(self.num_sets))
        self.page_offset_bits = int(math.log2(page_size))
        
        # Check VIPT safety
        self.is_vipt_safe = self.index_bits <= self.page_offset_bits
        
        self._print_configuration()
    
    def _print_configuration(self) -> None:
        """Print cache and page configuration"""
        print("=" * 80)
        print("VIPT/PIPT/VIVT Visualizer Configuration")
        print("=" * 80)
        print(f"Cache Size:        {self.cache_size:,} bytes ({self.cache_size // 1024} KB)")
        print(f"Block Size:        {self.block_size} bytes")
        print(f"Associativity:     {self.associativity}-way")
        print(f"Number of Sets:    {self.num_sets}")
        print(f"Page Size:         {self.page_size:,} bytes ({self.page_size // 1024} KB)")
        print()
        print(f"Address Width:     {self.address_bits} bits")
        print(f"Offset Bits:       {self.offset_bits} bits")
        print(f"Index Bits:        {self.index_bits} bits")
        print(f"Page Offset Bits:  {self.page_offset_bits} bits")
        print()
        print(f"VIPT Safety:       {'✅ SAFE' if self.is_vipt_safe else '❌ UNSAFE (synonym possible)'}")
        if self.is_vipt_safe:
            print(f"                   Index bits ({self.index_bits}) ≤ Page offset bits ({self.page_offset_bits})")
        else:
            print(f"                   Index bits ({self.index_bits}) > Page offset bits ({self.page_offset_bits})")
        print("=" * 80)
        print()
    
    def _decompose_address(self, address: int, use_physical: bool = False) -> AddressBreakdown:
        """
        Decompose an address into tag, index, offset.
        
        Args:
            address: The address to decompose
            use_physical: If True, treat as physical address
            
        Returns:
            AddressBreakdown object
        """
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        
        tag_bits = self.address_bits - self.offset_bits - self.index_bits
        
        return AddressBreakdown(
            address=address,
            tag=tag,
            index=index,
            offset=offset,
            tag_bits=tag_bits,
            index_bits=self.index_bits,
            offset_bits=self.offset_bits
        )
    
    def _get_vpn_and_offset(self, va: int) -> Tuple[int, int]:
        """Extract VPN (Virtual Page Number) and page offset from VA"""
        page_offset = va & ((1 << self.page_offset_bits) - 1)
        vpn = va >> self.page_offset_bits
        return vpn, page_offset
    
    def _get_ppn_and_offset(self, pa: int) -> Tuple[int, int]:
        """Extract PPN (Physical Page Number) and page offset from PA"""
        page_offset = pa & ((1 << self.page_offset_bits) - 1)
        ppn = pa >> self.page_offset_bits
        return ppn, page_offset
    
    def visualize_vivt(self, va: int) -> None:
        """Visualize VIVT (Virtually Indexed, Virtually Tagged) lookup"""
        print("\n" + "=" * 80)
        print("VIVT: Virtually Indexed, Virtually Tagged")
        print("=" * 80)
        
        breakdown = self._decompose_address(va)
        vpn, page_offset = self._get_vpn_and_offset(va)
        
        print(f"Virtual Address: 0x{va:08X}")
        print()
        print("Address Breakdown:")
        print(f"  VPN:          0x{vpn:X} (bits {self.address_bits-1}:{self.page_offset_bits})")
        print(f"  Page Offset:  0x{page_offset:X} (bits {self.page_offset_bits-1}:0)")
        print()
        
        # Show cache decomposition
        print("Cache Lookup (using VA only):")
        print(f"  VA Tag:       0x{breakdown.tag:X} (bits {self.address_bits-1}:{self.offset_bits + self.index_bits})")
        print(f"  Index:        0x{breakdown.index:X} (bits {self.offset_bits + self.index_bits - 1}:{self.offset_bits})")
        print(f"  Offset:       0x{breakdown.offset:X} (bits {self.offset_bits-1}:0)")
        print()
        
        print("Operation Flow:")
        print("  1. Use VA index to select cache set")
        print("  2. Compare VA tag with cache line tags")
        print("  3. Hit/Miss")
        print()
        print("⚠️  Problem: Synonym - Different VAs to same PA have different tags!")
        print("⚠️  Problem: Context switch requires cache flush")
    
    def visualize_pipt(self, va: int, pa: int) -> None:
        """Visualize PIPT (Physically Indexed, Physically Tagged) lookup"""
        print("\n" + "=" * 80)
        print("PIPT: Physically Indexed, Physically Tagged")
        print("=" * 80)
        
        vpn, va_offset = self._get_vpn_and_offset(va)
        ppn, pa_offset = self._get_ppn_and_offset(pa)
        pa_breakdown = self._decompose_address(pa)
        
        print(f"Virtual Address:  0x{va:08X}")
        print(f"  VPN:            0x{vpn:X}")
        print(f"  Page Offset:    0x{va_offset:X}")
        print()
        print("         ↓ [TLB Lookup]")
        print()
        print(f"Physical Address: 0x{pa:08X}")
        print(f"  PPN:            0x{ppn:X}")
        print(f"  Page Offset:    0x{pa_offset:X}")
        print()
        
        print("Cache Lookup (using PA only):")
        print(f"  PA Tag:       0x{pa_breakdown.tag:X} (bits {self.address_bits-1}:{self.offset_bits + self.index_bits})")
        print(f"  Index:        0x{pa_breakdown.index:X} (bits {self.offset_bits + self.index_bits - 1}:{self.offset_bits})")
        print(f"  Offset:       0x{pa_breakdown.offset:X} (bits {self.offset_bits-1}:0)")
        print()
        
        print("Operation Flow:")
        print("  1. TLB translates VA → PA")
        print("  2. Use PA index to select cache set")
        print("  3. Compare PA tag with cache line tags")
        print("  4. Hit/Miss")
        print()
        print("✅ Advantage: No synonym problem (same PA → same tag)")
        print("❌ Disadvantage: Must wait for TLB before cache lookup (SERIAL)")
    
    def visualize_vipt(self, va: int, pa: int) -> None:
        """Visualize VIPT (Virtually Indexed, Physically Tagged) lookup"""
        print("\n" + "=" * 80)
        print("VIPT: Virtually Indexed, Physically Tagged")
        print("=" * 80)
        
        va_breakdown = self._decompose_address(va)
        pa_breakdown = self._decompose_address(pa)
        vpn, va_offset = self._get_vpn_and_offset(va)
        ppn, pa_offset = self._get_ppn_and_offset(pa)
        
        print(f"Virtual Address:  0x{va:08X}")
        print(f"  VPN:            0x{vpn:X} (bits {self.address_bits-1}:{self.page_offset_bits})")
        print(f"  Page Offset:    0x{va_offset:X} (bits {self.page_offset_bits-1}:0)")
        print()
        
        print("         ┌─────────────────┐")
        print("         ↓                 ↓")
        print("   [TLB Lookup]      [VA Index → Select Set]")
        print("         ↓                 ↓")
        print(f"   PA Tag: 0x{pa_breakdown.tag:X}      Set: 0x{va_breakdown.index:X}")
        print("         └─────────┬───────┘")
        print("                   ↓")
        print("           Compare PA Tag")
        print("                   ↓")
        print("              Hit/Miss")
        print()
        
        print(f"Physical Address: 0x{pa:08X}")
        print(f"  PPN:            0x{ppn:X}")
        print(f"  Page Offset:    0x{pa_offset:X}")
        print()
        
        print("Cache Lookup:")
        print(f"  Index (from VA):  0x{va_breakdown.index:X} (bits {self.offset_bits + self.index_bits - 1}:{self.offset_bits})")
        print(f"  Tag (from PA):    0x{pa_breakdown.tag:X} (bits {self.address_bits-1}:{self.offset_bits + self.index_bits})")
        print(f"  Offset:           0x{va_breakdown.offset:X} (bits {self.offset_bits-1}:0)")
        print()
        
        # Check if index bits are within page offset
        index_start_bit = self.offset_bits
        index_end_bit = self.offset_bits + self.index_bits - 1
        
        print(f"Index Bit Range: [{index_end_bit}:{index_start_bit}]")
        print(f"Page Offset Range: [{self.page_offset_bits-1}:0]")
        print()
        
        if self.is_vipt_safe:
            print("✅ SAFE: Index bits are within page offset")
            print("   → Same page offset in VA and PA → Same cache set")
            print("   → No synonym problem!")
        else:
            print("⚠️  UNSAFE: Some index bits from VPN (not page offset)")
            print("   → Different VAs to same PA could map to different sets")
            print("   → Synonym problem possible!")
        print()
        
        print("✅ Advantage: TLB and set selection happen in PARALLEL (fast!)")
        print("✅ Advantage: PA tag avoids context switch issues")
        if self.is_vipt_safe:
            print("✅ Advantage: No synonym problem (if index ≤ page offset)")
    
    def compare_all_modes(self, va: int, pa: int) -> None:
        """Compare all three cache indexing modes side by side"""
        self.visualize_vivt(va)
        self.visualize_pipt(va, pa)
        self.visualize_vipt(va, pa)
        
        print("\n" + "=" * 80)
        print("Summary Comparison")
        print("=" * 80)
        print()
        print("| Mode  | Index from | Tag from | Speed      | Synonym? | Context Switch |")
        print("|-------|-----------|----------|------------|----------|----------------|")
        print("| VIVT  | VA        | VA       | Very Fast  | Yes ❌   | Flush needed ❌ |")
        print("| PIPT  | PA        | PA       | Slow       | No ✅    | No flush ✅     |")
        print("| VIPT  | VA        | PA       | Fast       | No* ✅   | No flush ✅     |")
        print()
        print("* VIPT is safe from synonyms if index_bits ≤ page_offset_bits")


def demo_vipt_safe():
    """Demonstrate a safe VIPT configuration"""
    print("\n" + "🎯" * 40)
    print("DEMO 1: VIPT Safe Configuration (Typical L1)")
    print("🎯" * 40 + "\n")
    
    # Typical L1: 32 KB, 4-way, 64B lines
    visualizer = VIPTVisualizer(
        cache_size=32768,
        block_size=64,
        associativity=4,
        page_size=4096
    )
    
    va = 0x00401234
    pa = 0x12345234  # Same page offset
    
    visualizer.compare_all_modes(va, pa)


def demo_vipt_unsafe():
    """Demonstrate an unsafe VIPT configuration"""
    print("\n" + "⚠️" * 40)
    print("DEMO 2: VIPT Unsafe Configuration (Too Large)")
    print("⚠️" * 40 + "\n")
    
    # Too large: 256 KB, 1-way (direct-mapped), 64B lines
    visualizer = VIPTVisualizer(
        cache_size=262144,  # 256 KB
        block_size=64,
        associativity=1,    # Direct-mapped
        page_size=4096
    )
    
    va = 0x00401234
    pa = 0x12345234
    
    visualizer.compare_all_modes(va, pa)


def demo_huge_pages():
    """Demonstrate VIPT with huge pages"""
    print("\n" + "📄" * 40)
    print("DEMO 3: VIPT with 2MB Huge Pages")
    print("📄" * 40 + "\n")
    
    # Larger cache possible with huge pages
    visualizer = VIPTVisualizer(
        cache_size=262144,      # 256 KB
        block_size=64,
        associativity=1,        # Direct-mapped
        page_size=2*1024*1024   # 2 MB huge page
    )
    
    va = 0x00401234
    pa = 0x12345234
    
    visualizer.compare_all_modes(va, pa)


def main():
    """Main entry point"""
    demo_vipt_safe()
    demo_vipt_unsafe()
    demo_huge_pages()
    
    print("\n" + "=" * 80)
    print("Key Takeaways:")
    print("=" * 80)
    print("1. VIPT combines fast lookup (parallel TLB/cache) with safety (PA tags)")
    print("2. VIPT is safe when: index_bits ≤ page_offset_bits")
    print("3. Modern L1 caches: 32-64 KB, high associativity → VIPT safe")
    print("4. Larger caches: Use PIPT (L2/L3) or huge pages")
    print("=" * 80)


if __name__ == "__main__":
    main()

