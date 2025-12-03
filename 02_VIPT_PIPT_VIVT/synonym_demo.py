"""
Synonym (Aliasing) Problem Demonstrator
========================================

This module demonstrates the synonym/aliasing problem in caches:
- How multiple VAs can map to the same PA
- Why VIVT caches suffer from stale data
- How VIPT caches avoid the problem (when designed correctly)

The synonym problem occurs when two different virtual addresses
map to the same physical address, but the cache treats them as
different locations.

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Dict, Optional
from dataclasses import dataclass
import math
import argparse


@dataclass
class CacheEntry:
    """A single cache entry (simplified)"""
    valid: bool = False
    tag: int = 0
    data: int = 0  # Simplified: single int value
    dirty: bool = False


class VIVTCache:
    """
    Simplified VIVT (Virtually Indexed, Virtually Tagged) cache.
    
    This implementation shows how synonyms cause problems:
    - Uses VA for both indexing and tagging
    - Different VAs → different cache locations (even if same PA)
    """
    
    def __init__(self, num_sets: int = 64, block_size: int = 64):
        self.num_sets = num_sets
        self.block_size = block_size
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(num_sets))
        
        # Storage: one entry per set (simplified direct-mapped)
        self.cache: Dict[int, CacheEntry] = {}
    
    def _decompose(self, va: int) -> tuple[int, int]:
        """Decompose VA into tag and index"""
        index = (va >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = va >> (self.offset_bits + self.index_bits)
        return tag, index
    
    def read(self, va: int, pa: int) -> Optional[int]:
        """
        Read from cache using VA.
        Returns data if hit, None if miss.
        """
        tag, index = self._decompose(va)
        
        if index in self.cache:
            entry = self.cache[index]
            if entry.valid and entry.tag == tag:
                print(f"  [OK] VIVT HIT:  VA=0x{va:08X} -> Set {index} (Tag 0x{tag:X}) -> Data={entry.data}")
                return entry.data
        
        print(f"  [MISS] VIVT MISS: VA=0x{va:08X} -> Set {index} (Tag 0x{tag:X})")
        return None
    
    def write(self, va: int, pa: int, data: int) -> None:
        """Write to cache using VA"""
        tag, index = self._decompose(va)
        
        # Always allocate on write (simplified)
        self.cache[index] = CacheEntry(valid=True, tag=tag, data=data, dirty=True)
        print(f"  ✏️  VIVT WRITE: VA=0x{va:08X} → Set {index} (Tag 0x{tag:X}) → Data={data}")
    
    def get_state(self) -> str:
        """Return string representation of cache state"""
        if not self.cache:
            return "  [Empty]"
        
        lines = []
        for index in sorted(self.cache.keys()):
            entry = self.cache[index]
            if entry.valid:
                dirty_marker = " (dirty)" if entry.dirty else ""
                lines.append(f"  Set {index:3d}: Tag=0x{entry.tag:X}, Data={entry.data}{dirty_marker}")
        
        return "\n".join(lines) if lines else "  [Empty]"


class VIPTCache:
    """
    Simplified VIPT (Virtually Indexed, Physically Tagged) cache.
    
    This implementation shows how VIPT avoids synonyms:
    - Uses VA for indexing (fast)
    - Uses PA for tagging (correct)
    - Safe when index bits ≤ page offset bits
    """
    
    def __init__(self, num_sets: int = 64, block_size: int = 64):
        self.num_sets = num_sets
        self.block_size = block_size
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(num_sets))
        
        # Storage: one entry per set (simplified direct-mapped)
        self.cache: Dict[int, CacheEntry] = {}
    
    def _get_index(self, va: int) -> int:
        """Get index from VA"""
        return (va >> self.offset_bits) & ((1 << self.index_bits) - 1)
    
    def _get_tag(self, pa: int) -> int:
        """Get tag from PA"""
        return pa >> (self.offset_bits + self.index_bits)
    
    def read(self, va: int, pa: int) -> Optional[int]:
        """
        Read from cache using VA for index, PA for tag.
        Returns data if hit, None if miss.
        """
        index = self._get_index(va)
        tag = self._get_tag(pa)
        
        if index in self.cache:
            entry = self.cache[index]
            if entry.valid and entry.tag == tag:
                print(f"  [OK] VIPT HIT:  VA=0x{va:08X}, PA=0x{pa:08X} -> Set {index} (PA Tag 0x{tag:X}) -> Data={entry.data}")
                return entry.data
        
        print(f"  [MISS] VIPT MISS: VA=0x{va:08X}, PA=0x{pa:08X} -> Set {index} (PA Tag 0x{tag:X})")
        return None
    
    def write(self, va: int, pa: int, data: int) -> None:
        """Write to cache using VA for index, PA for tag"""
        index = self._get_index(va)
        tag = self._get_tag(pa)
        
        # Always allocate on write (simplified)
        self.cache[index] = CacheEntry(valid=True, tag=tag, data=data, dirty=True)
        print(f"  ✏️  VIPT WRITE: VA=0x{va:08X}, PA=0x{pa:08X} → Set {index} (PA Tag 0x{tag:X}) → Data={data}")
    
    def get_state(self) -> str:
        """Return string representation of cache state"""
        if not self.cache:
            return "  [Empty]"
        
        lines = []
        for index in sorted(self.cache.keys()):
            entry = self.cache[index]
            if entry.valid:
                dirty_marker = " (dirty)" if entry.dirty else ""
                lines.append(f"  Set {index:3d}: PA_Tag=0x{entry.tag:X}, Data={entry.data}{dirty_marker}")
        
        return "\n".join(lines) if lines else "  [Empty]"


def demo_synonym_problem():
    """
    Demonstrate the synonym problem with VIVT cache.
    
    Scenario:
    - Two different VAs (0x10001000 and 0x20001000) map to same PA (0x50001000)
    - VIVT cache treats them as different locations
    - Results in stale data!
    """
    print("=" * 80)
    print("DEMO: Synonym Problem with VIVT Cache")
    print("=" * 80)
    print()
    print("Scenario: Shared memory between two processes")
    print("  Process A maps physical page 0x50001000 at VA 0x10001000")
    print("  Process B maps physical page 0x50001000 at VA 0x20001000")
    print("  (Same physical memory, different virtual addresses!)")
    print()
    
    vivt = VIVTCache(num_sets=64, block_size=64)
    
    # Two VAs mapping to the same PA
    va1 = 0x10001000  # Process A's view
    va2 = 0x20001000  # Process B's view
    pa = 0x50001000   # Shared physical address
    
    print("Step 1: Process A writes value 42 to VA1")
    print(f"        VA1=0x{va1:08X} → PA=0x{pa:08X}")
    vivt.write(va1, pa, 42)
    print()
    
    print("Step 2: Process A reads from VA1")
    data = vivt.read(va1, pa)
    print(f"        Got value: {data} [OK]")
    print()
    
    print("Step 3: Process B reads from VA2 (same PA!)")
    print(f"        VA2=0x{va2:08X} -> PA=0x{pa:08X} (same physical memory)")
    data = vivt.read(va2, pa)
    print(f"        Got value: {data} [MISS] MISS! Should see 42!")
    print()
    
    print("[WARN] Problem: VIVT cache has two different VA tags")
    print(f"   VA1 and VA2 map to different cache sets!")
    print()
    print("VIVT Cache State:")
    print(vivt.get_state())
    print()
    
    print("Step 4: Process B writes value 99 to VA2")
    vivt.write(va2, pa, 99)
    print()
    
    print("Step 5: Process A reads from VA1 again")
    data = vivt.read(va1, pa)
    print(f"        Got value: {data} [ERROR] STALE DATA!")
    print(f"        Expected: 99 (written by Process B)")
    print()
    
    print("[ERROR] SYNONYM PROBLEM: Two cache lines hold different versions of same PA!")
    print("   This violates cache coherence and causes bugs.")
    print()
    print("VIVT Cache State (two entries for same physical memory!):")
    print(vivt.get_state())


def demo_vipt_solution():
    """
    Demonstrate how VIPT solves the synonym problem.
    
    Same scenario as above, but with VIPT cache.
    """
    print("\n" + "=" * 80)
    print("DEMO: VIPT Solution to Synonym Problem")
    print("=" * 80)
    print()
    print("Same scenario, but with VIPT cache:")
    print("  - Index from VA (fast)")
    print("  - Tag from PA (correct)")
    print()
    
    vipt = VIPTCache(num_sets=64, block_size=64)
    
    # Same scenario as before
    va1 = 0x10001000  # Process A's view
    va2 = 0x20001000  # Process B's view
    pa = 0x50001000   # Shared physical address
    
    # For VIPT to work correctly, va1 and va2 should have the same
    # index bits (from page offset). Let's use addresses that satisfy this:
    # Page size = 4096 (0x1000), so offset = bits [11:0]
    # For 64B cache lines, offset bits = 6, index bits = 6
    # Index uses bits [11:6] - these are in the page offset!
    
    va1 = 0x10001040  # Index bits [11:6] = 0x01
    va2 = 0x20001040  # Index bits [11:6] = 0x01 (SAME!)
    pa = 0x50001040   # Same page offset = 0x040
    
    print(f"VA1 = 0x{va1:08X} (page offset = 0x{va1 & 0xFFF:03X})")
    print(f"VA2 = 0x{va2:08X} (page offset = 0x{va2 & 0xFFF:03X})")
    print(f"PA  = 0x{pa:08X} (page offset = 0x{pa & 0xFFF:03X})")
    print()
    print("[OK] All have SAME page offset -> SAME cache index!")
    print()
    
    print("Step 1: Process A writes value 42 to VA1")
    vipt.write(va1, pa, 42)
    print()
    
    print("Step 2: Process A reads from VA1")
    data = vipt.read(va1, pa)
    print(f"        Got value: {data} [OK]")
    print()
    
    print("Step 3: Process B reads from VA2 (same PA!)")
    data = vipt.read(va2, pa)
    print(f"        Got value: {data} [OK] HIT! Sees same data!")
    print()
    
    print("[OK] Success: VIPT uses PA tag, so both VAs hit the same cache line")
    print()
    print("VIPT Cache State:")
    print(vipt.get_state())
    print()
    
    print("Step 4: Process B writes value 99 to VA2")
    vipt.write(va2, pa, 99)
    print()
    
    print("Step 5: Process A reads from VA1 again")
    data = vipt.read(va1, pa)
    print(f"        Got value: {data} [OK] Sees updated value!")
    print()
    
    print("[OK] NO SYNONYM PROBLEM with VIPT!")
    print("   - VA index → same set (index from page offset)")
    print("   - PA tag → matches for both VAs")
    print("   - Single cache line for the physical address")
    print()
    print("VIPT Cache State (single entry):")
    print(vipt.get_state())


def demo_vipt_unsafe():
    """
    Demonstrate when VIPT can still have synonym problems.
    
    If cache index uses bits beyond page offset, synonyms can occur.
    """
    print("\n" + "=" * 80)
    print("DEMO: VIPT Unsafe Configuration")
    print("=" * 80)
    print()
    print("Scenario: Cache too large (index bits > page offset bits)")
    print()
    
    # Large cache: index bits extend beyond page offset
    vipt = VIPTCache(num_sets=512, block_size=64)  # 9 index bits
    # Page size = 4096, offset bits = 12
    # Index bits [14:6] - some bits are from VPN, not page offset!
    
    print("Configuration:")
    print("  Cache: 512 sets, 64B lines")
    print("  Index bits: 9 (bits [14:6])")
    print("  Page offset: 12 bits [11:0]")
    print("  [WARN] Index uses bits [14:12] from VPN (not page offset)!")
    print()
    
    # Two VAs with same page offset but different VPNs
    va1 = 0x10001040  # VPN=0x10001, offset=0x040
    va2 = 0x20001040  # VPN=0x20001, offset=0x040 (same offset!)
    pa = 0x50001040
    
    index1 = (va1 >> 6) & 0x1FF
    index2 = (va2 >> 6) & 0x1FF
    
    print(f"VA1 = 0x{va1:08X} -> Index = {index1}")
    print(f"VA2 = 0x{va2:08X} -> Index = {index2}")
    print()
    
    if index1 != index2:
        print("[ERROR] Different indices even though page offsets are the same!")
        print("   Synonym problem can occur!")
    else:
        print("[OK] Same indices (got lucky with this example)")


def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(
        description="Synonym Problem Demonstrator - Shows VIVT vs VIPT behavior",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all demos
  python synonym_demo.py

  # Run specific demo
  python synonym_demo.py --demo vivt
  python synonym_demo.py --demo vipt
  python synonym_demo.py --demo unsafe
        """
    )
    
    parser.add_argument(
        "--demo",
        choices=["vivt", "vipt", "unsafe", "all"],
        default="all",
        help="Run specific demo (default: all)"
    )
    
    parser.add_argument(
        "--num-sets",
        type=int,
        default=64,
        help="Number of cache sets (default: 64)"
    )
    
    parser.add_argument(
        "--block-size",
        type=int,
        default=64,
        help="Cache block size in bytes (default: 64)"
    )
    
    args = parser.parse_args()
    
    if args.demo == "vivt" or args.demo == "all":
        demo_synonym_problem()
    
    if args.demo == "vipt" or args.demo == "all":
        demo_vipt_solution()
    
    if args.demo == "unsafe" or args.demo == "all":
        demo_vipt_unsafe()
    
    print("\n" + "=" * 80)
    print("Key Takeaways:")
    print("=" * 80)
    print()
    print("1. Synonym Problem:")
    print("   - Multiple VAs -> same PA, but cache treats as different")
    print("   - Causes stale data and coherence violations")
    print()
    print("2. VIVT Issues:")
    print("   - Uses VA tags -> different VAs have different tags")
    print("   - Even if they map to same PA!")
    print()
    print("3. VIPT Solution:")
    print("   - Index from VA (fast)")
    print("   - Tag from PA (correct)")
    print("   - Works if index bits <= page offset bits")
    print()
    print("4. VIPT Safety Rule:")
    print("   - index_bits <= page_offset_bits")
    print("   - For 4KB pages: index_bits <= 12")
    print("   - Typical L1: 32-64 KB, 4-8 way -> 6-8 index bits [OK]")
    print("=" * 80)


if __name__ == "__main__":
    main()

