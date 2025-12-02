"""
Page Table Walk Simulator
==========================

This module simulates page table walks for:
- RISC-V Sv39 (3-level paging)
- x86-64 (4-level paging)

It demonstrates step-by-step address translation through
multi-level page tables, including permission checking
and page fault handling.

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random


class PageSize(Enum):
    """Page sizes supported"""
    KB_4 = 4096
    MB_2 = 2 * 1024 * 1024
    GB_1 = 1024 * 1024 * 1024


class FaultType(Enum):
    """Types of page faults"""
    NOT_PRESENT = auto()
    PERMISSION_VIOLATION = auto()
    INVALID_ADDRESS = auto()


@dataclass
class PageTableEntry:
    """
    Generic page table entry.
    
    Attributes:
        valid: Entry is valid/present
        ppn: Physical Page Number
        readable: Read permission
        writable: Write permission
        executable: Execute permission
        user: User-mode accessible
        global_page: Global mapping (don't flush on context switch)
        accessed: Page has been accessed
        dirty: Page has been written
        is_leaf: Is this a leaf PTE (vs pointer to next level)
    """
    valid: bool = False
    ppn: int = 0
    readable: bool = False
    writable: bool = False
    executable: bool = False
    user: bool = False
    global_page: bool = False
    accessed: bool = False
    dirty: bool = False
    is_leaf: bool = False


class RISCV_Sv39_PageWalker:
    """
    RISC-V Sv39 page walker.
    
    Sv39: 39-bit virtual addresses, 3-level page tables
    - VPN[2]: bits [38:30] (9 bits)
    - VPN[1]: bits [29:21] (9 bits)
    - VPN[0]: bits [20:12] (9 bits)
    - Offset: bits [11:0] (12 bits)
    
    Each page table has 512 entries (2^9).
    PTE size: 8 bytes.
    """
    
    def __init__(self):
        """Initialize RISC-V Sv39 page walker"""
        # Simulated physical memory (sparse)
        self.memory: Dict[int, bytes] = {}
        
        # Root page table (level 2) physical address
        self.satp = self._allocate_page_table()
        
        # Statistics
        self.page_walks = 0
        self.page_faults = 0
        
        print("=" * 70)
        print("RISC-V Sv39 Page Walker Initialized")
        print("=" * 70)
        print(f"Page table root (satp): 0x{self.satp:X}")
        print("Address format: [VPN2(9) | VPN1(9) | VPN0(9) | Offset(12)]")
        print("=" * 70)
        print()
    
    def _allocate_page_table(self) -> int:
        """Allocate a page table (returns physical address)"""
        # Generate random PA for page table
        pa = random.randint(0x10000, 0xFFFFFF) & ~0xFFF  # Page-aligned
        
        # Initialize page table (512 entries × 8 bytes = 4096 bytes)
        self.memory[pa] = bytearray(4096)
        
        return pa
    
    def _write_pte(self, table_pa: int, index: int, pte: PageTableEntry) -> None:
        """Write a PTE to a page table"""
        # Encode PTE (simplified)
        flags = 0
        if pte.valid:
            flags |= 0x01
        if pte.readable:
            flags |= 0x02
        if pte.writable:
            flags |= 0x04
        if pte.executable:
            flags |= 0x08
        if pte.user:
            flags |= 0x10
        if pte.global_page:
            flags |= 0x20
        if pte.accessed:
            flags |= 0x40
        if pte.dirty:
            flags |= 0x80
        
        pte_value = (pte.ppn << 10) | flags
        
        # Write 8-byte PTE
        offset = index * 8
        pte_bytes = pte_value.to_bytes(8, byteorder='little')
        self.memory[table_pa][offset:offset+8] = pte_bytes
    
    def _read_pte(self, table_pa: int, index: int) -> PageTableEntry:
        """Read a PTE from a page table"""
        offset = index * 8
        pte_bytes = bytes(self.memory[table_pa][offset:offset+8])
        pte_value = int.from_bytes(pte_bytes, byteorder='little')
        
        # Decode PTE
        valid = bool(pte_value & 0x01)
        readable = bool(pte_value & 0x02)
        writable = bool(pte_value & 0x04)
        executable = bool(pte_value & 0x08)
        user = bool(pte_value & 0x10)
        global_page = bool(pte_value & 0x20)
        accessed = bool(pte_value & 0x40)
        dirty = bool(pte_value & 0x80)
        ppn = pte_value >> 10
        
        # Leaf if any RWX bit is set
        is_leaf = readable or writable or executable
        
        return PageTableEntry(
            valid=valid,
            ppn=ppn,
            readable=readable,
            writable=writable,
            executable=executable,
            user=user,
            global_page=global_page,
            accessed=accessed,
            dirty=dirty,
            is_leaf=is_leaf
        )
    
    def _decompose_va(self, va: int) -> Tuple[int, int, int, int]:
        """Decompose VA into VPN[2], VPN[1], VPN[0], offset"""
        offset = va & 0xFFF
        vpn0 = (va >> 12) & 0x1FF
        vpn1 = (va >> 21) & 0x1FF
        vpn2 = (va >> 30) & 0x1FF
        return vpn2, vpn1, vpn0, offset
    
    def map_page(
        self,
        va: int,
        pa: int,
        readable: bool = True,
        writable: bool = True,
        executable: bool = False,
        user: bool = True
    ) -> None:
        """
        Map a virtual page to a physical page.
        
        Args:
            va: Virtual address (page-aligned)
            pa: Physical address (page-aligned)
            readable: Read permission
            writable: Write permission
            executable: Execute permission
            user: User-mode accessible
        """
        vpn2, vpn1, vpn0, _ = self._decompose_va(va)
        
        # Level 2
        pte_l2 = self._read_pte(self.satp, vpn2)
        if not pte_l2.valid:
            # Allocate level 1 table
            l1_pa = self._allocate_page_table()
            pte_l2 = PageTableEntry(valid=True, ppn=l1_pa >> 12, is_leaf=False)
            self._write_pte(self.satp, vpn2, pte_l2)
        
        l1_pa = pte_l2.ppn << 12
        
        # Level 1
        pte_l1 = self._read_pte(l1_pa, vpn1)
        if not pte_l1.valid:
            # Allocate level 0 table
            l0_pa = self._allocate_page_table()
            pte_l1 = PageTableEntry(valid=True, ppn=l0_pa >> 12, is_leaf=False)
            self._write_pte(l1_pa, vpn1, pte_l1)
        
        l0_pa = pte_l1.ppn << 12
        
        # Level 0 (leaf)
        ppn = pa >> 12
        pte_l0 = PageTableEntry(
            valid=True,
            ppn=ppn,
            readable=readable,
            writable=writable,
            executable=executable,
            user=user,
            is_leaf=True
        )
        self._write_pte(l0_pa, vpn0, pte_l0)
    
    def translate(self, va: int, is_write: bool = False, verbose: bool = True) -> Optional[int]:
        """
        Translate virtual address to physical address.
        
        Args:
            va: Virtual address
            is_write: Whether this is a write access
            verbose: Print step-by-step output
        
        Returns:
            Physical address if successful, None if page fault
        """
        self.page_walks += 1
        
        vpn2, vpn1, vpn0, offset = self._decompose_va(va)
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"RISC-V Sv39 Page Walk: VA=0x{va:09X}")
            print(f"{'=' * 70}")
            print(f"Virtual Address Breakdown:")
            print(f"  VPN[2]:      0x{vpn2:03X} (bits 38:30)")
            print(f"  VPN[1]:      0x{vpn1:03X} (bits 29:21)")
            print(f"  VPN[0]:      0x{vpn0:03X} (bits 20:12)")
            print(f"  Offset:      0x{offset:03X} (bits 11:0)")
            print()
        
        # Level 2 lookup
        if verbose:
            print(f"Step 1: Level 2 Lookup")
            print(f"  Table PA:    0x{self.satp:X}")
            print(f"  Index:       {vpn2}")
            print(f"  PTE Address: 0x{self.satp + vpn2 * 8:X}")
        
        pte_l2 = self._read_pte(self.satp, vpn2)
        
        if not pte_l2.valid:
            if verbose:
                print(f"  ❌ Page Fault: Level 2 PTE not valid")
            self.page_faults += 1
            return None
        
        if verbose:
            print(f"  PPN:         0x{pte_l2.ppn:X}")
            print(f"  Leaf?        {'Yes' if pte_l2.is_leaf else 'No'}")
        
        if pte_l2.is_leaf:
            # 1GB superpage
            pa = (pte_l2.ppn << 30) | (va & 0x3FFFFFFF)
            if verbose:
                print(f"  ✅ 1GB Superpage!")
                print(f"\nPhysical Address: 0x{pa:X}")
            return pa
        
        # Level 1 lookup
        l1_pa = pte_l2.ppn << 12
        
        if verbose:
            print()
            print(f"Step 2: Level 1 Lookup")
            print(f"  Table PA:    0x{l1_pa:X}")
            print(f"  Index:       {vpn1}")
            print(f"  PTE Address: 0x{l1_pa + vpn1 * 8:X}")
        
        pte_l1 = self._read_pte(l1_pa, vpn1)
        
        if not pte_l1.valid:
            if verbose:
                print(f"  ❌ Page Fault: Level 1 PTE not valid")
            self.page_faults += 1
            return None
        
        if verbose:
            print(f"  PPN:         0x{pte_l1.ppn:X}")
            print(f"  Leaf?        {'Yes' if pte_l1.is_leaf else 'No'}")
        
        if pte_l1.is_leaf:
            # 2MB megapage
            pa = (pte_l1.ppn << 21) | (va & 0x1FFFFF)
            if verbose:
                print(f"  ✅ 2MB Megapage!")
                print(f"\nPhysical Address: 0x{pa:X}")
            return pa
        
        # Level 0 lookup
        l0_pa = pte_l1.ppn << 12
        
        if verbose:
            print()
            print(f"Step 3: Level 0 Lookup")
            print(f"  Table PA:    0x{l0_pa:X}")
            print(f"  Index:       {vpn0}")
            print(f"  PTE Address: 0x{l0_pa + vpn0 * 8:X}")
        
        pte_l0 = self._read_pte(l0_pa, vpn0)
        
        if not pte_l0.valid:
            if verbose:
                print(f"  ❌ Page Fault: Level 0 PTE not valid")
            self.page_faults += 1
            return None
        
        if verbose:
            print(f"  PPN:         0x{pte_l0.ppn:X}")
            print(f"  Permissions: R={'✅' if pte_l0.readable else '❌'} "
                  f"W={'✅' if pte_l0.writable else '❌'} "
                  f"X={'✅' if pte_l0.executable else '❌'}")
        
        # Check permissions
        if is_write and not pte_l0.writable:
            if verbose:
                print(f"  ❌ Page Fault: Write permission denied")
            self.page_faults += 1
            return None
        
        # Construct PA
        pa = (pte_l0.ppn << 12) | offset
        
        if verbose:
            print(f"  ✅ Translation Complete!")
            print()
            print(f"Physical Address: 0x{pa:X}")
        
        return pa
    
    def print_stats(self) -> None:
        """Print statistics"""
        print(f"\n{'=' * 70}")
        print("Page Walker Statistics")
        print("=" * 70)
        print(f"Page Walks:    {self.page_walks}")
        print(f"Page Faults:   {self.page_faults}")
        if self.page_walks > 0:
            success_rate = ((self.page_walks - self.page_faults) / self.page_walks) * 100
            print(f"Success Rate:  {success_rate:.2f}%")
        print("=" * 70)


def demo_sv39_basic():
    """Demonstrate basic Sv39 page walk"""
    print("\n" + "🎯" * 35)
    print("DEMO: RISC-V Sv39 Page Walk")
    print("🎯" * 35 + "\n")
    
    walker = RISCV_Sv39_PageWalker()
    
    # Map some pages
    print("Setting up page table mappings...")
    walker.map_page(va=0x000401000, pa=0x012345000)
    walker.map_page(va=0x000402000, pa=0x023456000)
    print()
    
    # Successful translation
    walker.translate(va=0x000401234)
    
    # Access different byte in same page (would be TLB hit in real system)
    print("\n--- Accessing different offset in same page ---")
    walker.translate(va=0x000401567)
    
    # Page fault
    print("\n--- Unmapped address (page fault) ---")
    walker.translate(va=0x000500000)
    
    walker.print_stats()


def demo_comparison():
    """Compare address decomposition between architectures"""
    print("\n" + "📊" * 35)
    print("DEMO: Address Format Comparison")
    print("📊" * 35 + "\n")
    
    va = 0x7FFFF_FC0401234
    
    print(f"Virtual Address: 0x{va:012X}\n")
    
    # RISC-V Sv39
    print("RISC-V Sv39 (39-bit VA):")
    va_39 = va & 0x7FFFFFFFFF  # Mask to 39 bits
    vpn2 = (va_39 >> 30) & 0x1FF
    vpn1 = (va_39 >> 21) & 0x1FF
    vpn0 = (va_39 >> 12) & 0x1FF
    offset = va_39 & 0xFFF
    
    print(f"  VPN[2] = 0x{vpn2:03X} (bits 38:30)")
    print(f"  VPN[1] = 0x{vpn1:03X} (bits 29:21)")
    print(f"  VPN[0] = 0x{vpn0:03X} (bits 20:12)")
    print(f"  Offset = 0x{offset:03X} (bits 11:0)")
    print(f"  Levels = 3")
    print()
    
    # x86-64
    print("x86-64 (48-bit VA):")
    va_48 = va & 0xFFFFFFFFFFFF  # Mask to 48 bits
    pml4 = (va_48 >> 39) & 0x1FF
    pdpt = (va_48 >> 30) & 0x1FF
    pd = (va_48 >> 21) & 0x1FF
    pt = (va_48 >> 12) & 0x1FF
    offset = va_48 & 0xFFF
    
    print(f"  PML4   = 0x{pml4:03X} (bits 47:39)")
    print(f"  PDPT   = 0x{pdpt:03X} (bits 38:30)")
    print(f"  PD     = 0x{pd:03X} (bits 29:21)")
    print(f"  PT     = 0x{pt:03X} (bits 20:12)")
    print(f"  Offset = 0x{offset:03X} (bits 11:0)")
    print(f"  Levels = 4")


def main():
    """Main entry point"""
    demo_sv39_basic()
    demo_comparison()
    
    print("\n" + "=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("1. Multi-level page tables save memory (sparse address space)")
    print("2. Each level requires one memory access (expensive without TLB!)")
    print("3. RISC-V Sv39: 3 levels, 39-bit VA")
    print("4. x86-64: 4 levels, 48-bit VA")
    print("5. Large pages reduce page table depth")
    print("=" * 70)


if __name__ == "__main__":
    main()

