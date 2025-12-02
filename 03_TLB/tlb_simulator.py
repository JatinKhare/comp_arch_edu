"""
TLB (Translation Lookaside Buffer) Simulator
=============================================

This module implements a configurable TLB simulator with:
- Fully associative organization
- Multi-page-size support (4KB, 2MB, 1GB)
- LRU replacement policy
- Permission checking (R/W/X)
- Statistics tracking

The TLB caches virtual-to-physical address translations to avoid
expensive page table walks.

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum
import random


class PageSize(Enum):
    """Supported page sizes"""
    KB_4 = 4096          # 4 KB (12-bit offset)
    MB_2 = 2097152       # 2 MB (21-bit offset)
    GB_1 = 1073741824    # 1 GB (30-bit offset)
    
    @property
    def offset_bits(self) -> int:
        """Return number of offset bits for this page size"""
        return {
            PageSize.KB_4: 12,
            PageSize.MB_2: 21,
            PageSize.GB_1: 30
        }[self]
    
    def __str__(self) -> str:
        return {
            PageSize.KB_4: "4KB",
            PageSize.MB_2: "2MB",
            PageSize.GB_1: "1GB"
        }[self]


@dataclass
class TLBEntry:
    """
    A single TLB entry storing a page table entry (PTE).
    
    Attributes:
        valid: Whether this entry is valid
        vpn: Virtual Page Number (tag)
        ppn: Physical Page Number (translation result)
        page_size: Size of the page
        readable: Read permission
        writable: Write permission
        executable: Execute permission
        dirty: Page has been modified
        accessed: Page has been accessed
        global_page: Don't flush on context switch
        lru_counter: For LRU replacement
    """
    valid: bool = False
    vpn: int = 0
    ppn: int = 0
    page_size: PageSize = PageSize.KB_4
    readable: bool = True
    writable: bool = True
    executable: bool = False
    dirty: bool = False
    accessed: bool = False
    global_page: bool = False
    lru_counter: int = 0


class TLB:
    """
    Translation Lookaside Buffer simulator.
    
    Fully associative organization with LRU replacement.
    Supports multiple page sizes.
    """
    
    def __init__(
        self,
        num_entries: int = 64,
        address_bits: int = 32
    ):
        """
        Initialize TLB.
        
        Args:
            num_entries: Number of TLB entries
            address_bits: Address width in bits
        """
        self.num_entries = num_entries
        self.address_bits = address_bits
        
        # TLB storage (fully associative)
        self.entries: list[TLBEntry] = [TLBEntry() for _ in range(num_entries)]
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.global_lru_counter = 0
        
        # Simulated page table (VPN -> PPN mapping)
        # In real hardware, this would trigger a page walk
        self.page_table: Dict[tuple[int, PageSize], int] = {}
        
        self._print_config()
    
    def _print_config(self) -> None:
        """Print TLB configuration"""
        print("=" * 70)
        print("TLB Configuration")
        print("=" * 70)
        print(f"Number of Entries: {self.num_entries}")
        print(f"Organization:      Fully Associative")
        print(f"Replacement:       LRU (Least Recently Used)")
        print(f"Address Width:     {self.address_bits} bits")
        print(f"Supported Pages:   4KB, 2MB, 1GB")
        print("=" * 70)
        print()
    
    def _extract_vpn(self, va: int, page_size: PageSize) -> int:
        """Extract Virtual Page Number from virtual address"""
        return va >> page_size.offset_bits
    
    def _extract_offset(self, va: int, page_size: PageSize) -> int:
        """Extract page offset from virtual address"""
        return va & ((1 << page_size.offset_bits) - 1)
    
    def _construct_pa(self, ppn: int, offset: int, page_size: PageSize) -> int:
        """Construct physical address from PPN and offset"""
        return (ppn << page_size.offset_bits) | offset
    
    def _find_entry(self, vpn: int, page_size: PageSize) -> Optional[int]:
        """
        Search TLB for matching entry.
        
        Args:
            vpn: Virtual Page Number to search for
            page_size: Page size
        
        Returns:
            Entry index if found, None otherwise
        """
        for i in range(self.num_entries):
            entry = self.entries[i]
            if entry.valid and entry.vpn == vpn and entry.page_size == page_size:
                return i
        return None
    
    def _find_victim(self) -> int:
        """
        Find victim entry for replacement using LRU.
        
        Returns:
            Index of victim entry
        """
        # First, check for invalid entries
        for i in range(self.num_entries):
            if not self.entries[i].valid:
                return i
        
        # All valid: use LRU
        lru_idx = 0
        min_lru = self.entries[0].lru_counter
        for i in range(1, self.num_entries):
            if self.entries[i].lru_counter < min_lru:
                min_lru = self.entries[i].lru_counter
                lru_idx = i
        
        return lru_idx
    
    def _update_lru(self, index: int) -> None:
        """Update LRU counter for an entry"""
        self.global_lru_counter += 1
        self.entries[index].lru_counter = self.global_lru_counter
    
    def _page_walk(self, vpn: int, page_size: PageSize) -> Optional[int]:
        """
        Simulate page table walk.
        
        In real hardware, this walks multi-level page tables.
        Here, we use a simple dictionary lookup.
        
        Args:
            vpn: Virtual Page Number
            page_size: Page size
        
        Returns:
            PPN if found, None if page fault
        """
        key = (vpn, page_size)
        return self.page_table.get(key)
    
    def install_mapping(
        self,
        va: int,
        pa: int,
        page_size: PageSize = PageSize.KB_4,
        readable: bool = True,
        writable: bool = True,
        executable: bool = False
    ) -> None:
        """
        Install a VA->PA mapping in the simulated page table.
        
        This simulates OS page table setup.
        
        Args:
            va: Virtual address
            pa: Physical address
            page_size: Page size
            readable: Read permission
            writable: Write permission
            executable: Execute permission
        """
        vpn = self._extract_vpn(va, page_size)
        ppn = self._extract_vpn(pa, page_size)
        
        key = (vpn, page_size)
        self.page_table[key] = ppn
        
        # Note: We store permissions in TLB entries, not page table (simplified)
    
    def translate(
        self,
        va: int,
        page_size: PageSize = PageSize.KB_4,
        is_write: bool = False,
        verbose: bool = True
    ) -> Optional[int]:
        """
        Translate virtual address to physical address.
        
        Args:
            va: Virtual address
            page_size: Page size
            is_write: Whether this is a write access
            verbose: Print detailed output
        
        Returns:
            Physical address if successful, None if page fault
        """
        vpn = self._extract_vpn(va, page_size)
        offset = self._extract_offset(va, page_size)
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"TLB Translation: VA=0x{va:08X} (Page Size: {page_size})")
            print(f"{'=' * 70}")
            print(f"VPN:         0x{vpn:X}")
            print(f"Page Offset: 0x{offset:X}")
            print()
        
        # Search TLB
        entry_idx = self._find_entry(vpn, page_size)
        
        if entry_idx is not None:
            # TLB HIT
            self.hits += 1
            entry = self.entries[entry_idx]
            
            # Check permissions
            if is_write and not entry.writable:
                if verbose:
                    print("❌ TLB Hit but WRITE PROTECTION FAULT!")
                return None
            
            ppn = entry.ppn
            pa = self._construct_pa(ppn, offset, page_size)
            
            # Update LRU
            self._update_lru(entry_idx)
            
            # Set accessed/dirty bits
            entry.accessed = True
            if is_write:
                entry.dirty = True
            
            if verbose:
                print(f"✅ TLB HIT (Entry {entry_idx})")
                print(f"PPN:         0x{ppn:X}")
                print(f"Permissions: R={'✅' if entry.readable else '❌'} "
                      f"W={'✅' if entry.writable else '❌'} "
                      f"X={'✅' if entry.executable else '❌'}")
                print(f"Flags:       Dirty={'✅' if entry.dirty else '❌'} "
                      f"Accessed={'✅' if entry.accessed else '❌'}")
                print()
                print(f"Physical Address: 0x{pa:08X}")
            
            return pa
        
        else:
            # TLB MISS
            self.misses += 1
            
            if verbose:
                print("❌ TLB MISS!")
                print("Initiating page table walk...")
            
            # Page walk
            ppn = self._page_walk(vpn, page_size)
            
            if ppn is None:
                if verbose:
                    print("❌ PAGE FAULT! (No mapping in page table)")
                return None
            
            if verbose:
                print(f"Page walk result: PPN=0x{ppn:X}")
                print("Inserting into TLB...")
            
            # Find victim and evict
            victim_idx = self._find_victim()
            victim = self.entries[victim_idx]
            
            if victim.valid and verbose:
                print(f"Evicting entry {victim_idx}: VPN=0x{victim.vpn:X} ({victim.page_size})")
            
            # Insert new entry
            self.entries[victim_idx] = TLBEntry(
                valid=True,
                vpn=vpn,
                ppn=ppn,
                page_size=page_size,
                readable=True,
                writable=True,
                executable=False,
                accessed=True,
                dirty=is_write
            )
            
            self._update_lru(victim_idx)
            
            pa = self._construct_pa(ppn, offset, page_size)
            
            if verbose:
                print(f"Inserted into entry {victim_idx}")
                print()
                print(f"Physical Address: 0x{pa:08X}")
            
            return pa
    
    def invalidate(self, va: int, page_size: PageSize = PageSize.KB_4) -> bool:
        """
        Invalidate a TLB entry (e.g., after munmap).
        
        Args:
            va: Virtual address
            page_size: Page size
        
        Returns:
            True if entry was found and invalidated
        """
        vpn = self._extract_vpn(va, page_size)
        entry_idx = self._find_entry(vpn, page_size)
        
        if entry_idx is not None:
            self.entries[entry_idx].valid = False
            print(f"TLB entry {entry_idx} invalidated (VPN=0x{vpn:X})")
            return True
        
        return False
    
    def flush(self) -> None:
        """Flush entire TLB (e.g., on context switch)"""
        for entry in self.entries:
            if not entry.global_page:
                entry.valid = False
        print("TLB flushed (except global pages)")
    
    def get_reach(self) -> int:
        """
        Calculate TLB reach (total memory coverage).
        
        Returns:
            TLB reach in bytes
        """
        reach = 0
        for entry in self.entries:
            if entry.valid:
                reach += entry.page_size.value
        return reach
    
    def print_stats(self) -> None:
        """Print TLB statistics"""
        total = self.hits + self.misses
        
        print(f"\n{'=' * 70}")
        print("TLB Statistics")
        print("=" * 70)
        print(f"Total Accesses: {total:,}")
        print(f"Hits:           {self.hits:,}")
        print(f"Misses:         {self.misses:,}")
        
        if total > 0:
            hit_rate = (self.hits / total) * 100
            miss_rate = (self.misses / total) * 100
            print(f"Hit Rate:       {hit_rate:.2f}%")
            print(f"Miss Rate:      {miss_rate:.2f}%")
        
        reach = self.get_reach()
        print()
        print(f"TLB Reach:      {reach:,} bytes ({reach // 1024:,} KB)")
        
        # Count entries by page size
        count_4kb = sum(1 for e in self.entries if e.valid and e.page_size == PageSize.KB_4)
        count_2mb = sum(1 for e in self.entries if e.valid and e.page_size == PageSize.MB_2)
        count_1gb = sum(1 for e in self.entries if e.valid and e.page_size == PageSize.GB_1)
        
        print()
        print(f"Valid Entries:  {count_4kb + count_2mb + count_1gb} / {self.num_entries}")
        print(f"  4KB pages:    {count_4kb}")
        print(f"  2MB pages:    {count_2mb}")
        print(f"  1GB pages:    {count_1gb}")
        
        print("=" * 70)
    
    def print_contents(self) -> None:
        """Print all valid TLB entries"""
        print(f"\n{'=' * 70}")
        print("TLB Contents")
        print("=" * 70}")
        print(f"{'Idx':<4} {'VPN':<10} {'PPN':<10} {'Size':<6} {'R W X':<6} {'D A':<4}")
        print("-" * 70)
        
        for i, entry in enumerate(self.entries):
            if entry.valid:
                perms = f"{'R' if entry.readable else '-'}" \
                        f"{'W' if entry.writable else '-'}" \
                        f"{'X' if entry.executable else '-'}"
                flags = f"{'D' if entry.dirty else '-'}{'A' if entry.accessed else '-'}"
                
                print(f"{i:<4} 0x{entry.vpn:<8X} 0x{entry.ppn:<8X} {str(entry.page_size):<6} "
                      f"{perms:<6} {flags:<4}")
        
        print("=" * 70)


def demo_basic_usage():
    """Demonstrate basic TLB usage"""
    print("\n" + "🎯" * 35)
    print("DEMO 1: Basic TLB Usage")
    print("🎯" * 35 + "\n")
    
    tlb = TLB(num_entries=8)  # Small TLB for demo
    
    # Install some mappings
    print("Installing page table mappings...")
    tlb.install_mapping(va=0x00401000, pa=0x12345000, page_size=PageSize.KB_4)
    tlb.install_mapping(va=0x00402000, pa=0x23456000, page_size=PageSize.KB_4)
    tlb.install_mapping(va=0x00500000, pa=0x34567000, page_size=PageSize.MB_2)
    print()
    
    # First access: TLB miss
    tlb.translate(0x00401234, PageSize.KB_4)
    
    # Second access: TLB hit
    tlb.translate(0x00401567, PageSize.KB_4)
    
    # New page: TLB miss
    tlb.translate(0x00402123, PageSize.KB_4)
    
    # Huge page: TLB miss
    tlb.translate(0x00501234, PageSize.MB_2)
    
    tlb.print_stats()
    tlb.print_contents()


def demo_huge_pages():
    """Demonstrate benefit of huge pages for TLB reach"""
    print("\n" + "📄" * 35)
    print("DEMO 2: Huge Pages for Better TLB Reach")
    print("📄" * 35 + "\n")
    
    tlb = TLB(num_entries=64)
    
    print("Scenario: Accessing 128 MB of memory\n")
    
    # Scenario 1: Use 4KB pages
    print("--- Using 4KB pages ---")
    num_4kb_pages = (128 * 1024 * 1024) // (4 * 1024)  # 32,768 pages
    print(f"Need {num_4kb_pages:,} pages of 4KB")
    
    # Simulate random access pattern
    for _ in range(100):
        va = random.randint(0, 128 * 1024 * 1024 - 1)
        # Install mapping if needed
        vpn = va >> 12
        if (vpn, PageSize.KB_4) not in tlb.page_table:
            pa = random.randint(0, 0xFFFFFFFF) & ~0xFFF
            tlb.install_mapping(va, pa, PageSize.KB_4)
        tlb.translate(va, PageSize.KB_4, verbose=False)
    
    print(f"\nResult with 4KB pages:")
    tlb.print_stats()
    
    # Scenario 2: Use 2MB huge pages
    print("\n--- Using 2MB huge pages ---")
    tlb_huge = TLB(num_entries=64)
    
    num_2mb_pages = (128 * 1024 * 1024) // (2 * 1024 * 1024)  # 64 pages
    print(f"Need {num_2mb_pages} pages of 2MB")
    
    for _ in range(100):
        va = random.randint(0, 128 * 1024 * 1024 - 1)
        vpn = va >> 21
        if (vpn, PageSize.MB_2) not in tlb_huge.page_table:
            pa = random.randint(0, 0xFFFFFFFF) & ~0x1FFFFF
            tlb_huge.install_mapping(va, pa, PageSize.MB_2)
        tlb_huge.translate(va, PageSize.MB_2, verbose=False)
    
    print(f"\nResult with 2MB huge pages:")
    tlb_huge.print_stats()
    
    print("\n✅ Huge pages drastically improve TLB hit rate!")


def demo_tlb_invalidation():
    """Demonstrate TLB invalidation"""
    print("\n" + "🔄" * 35)
    print("DEMO 3: TLB Invalidation and Flush")
    print("🔄" * 35 + "\n")
    
    tlb = TLB(num_entries=8)
    
    # Setup
    tlb.install_mapping(va=0x00401000, pa=0x12345000)
    tlb.install_mapping(va=0x00402000, pa=0x23456000)
    
    tlb.translate(0x00401000, verbose=False)
    tlb.translate(0x00402000, verbose=False)
    
    print("TLB after initial accesses:")
    tlb.print_contents()
    
    # Invalidate one entry
    print("\nInvalidating VA=0x00401000...")
    tlb.invalidate(0x00401000)
    
    print("\nTLB after invalidation:")
    tlb.print_contents()
    
    # Flush all
    print("\nFlushing entire TLB (simulating context switch)...")
    tlb.flush()
    
    print("\nTLB after flush:")
    tlb.print_contents()


def main():
    """Main entry point"""
    demo_basic_usage()
    demo_huge_pages()
    demo_tlb_invalidation()
    
    print("\n" + "=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("1. TLB caches VA→PA translations (avoids page walks)")
    print("2. TLB reach = number of entries × page size")
    print("3. Huge pages (2MB, 1GB) dramatically improve TLB reach")
    print("4. TLB misses are expensive (20-200 cycles)")
    print("5. High hit rate (>95%) is critical for performance")
    print("=" * 70)


if __name__ == "__main__":
    main()

