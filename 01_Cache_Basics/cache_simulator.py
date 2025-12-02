"""
Cache Simulator - Educational Implementation
============================================

This module implements a configurable cache simulator with:
- Direct-mapped, N-way set-associative, and fully-associative support
- LRU (Least Recently Used) replacement policy
- Write-back policy with dirty bit tracking
- Detailed visualization of cache operations

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class AccessType(Enum):
    """Type of memory access"""
    READ = "READ"
    WRITE = "WRITE"


@dataclass
class CacheLine:
    """
    Represents a single cache line (block).
    
    Attributes:
        valid: Whether this line contains valid data
        dirty: Whether this line has been modified (needs write-back)
        tag: Tag portion of the address
        lru_counter: Counter for LRU replacement (lower = older)
    """
    valid: bool = False
    dirty: bool = False
    tag: int = 0
    lru_counter: int = 0


class Cache:
    """
    A configurable cache simulator with detailed statistics and visualization.
    
    Cache organization:
        - size: Total cache size in bytes
        - block_size: Size of each cache line in bytes
        - associativity: Number of ways (1 = direct-mapped, size = fully associative)
    
    Address decomposition:
        [   Tag   |  Index  | Offset ]
        Tag: Identifies which block
        Index: Selects the set
        Offset: Byte within the block
    """
    
    def __init__(
        self,
        size: int = 4096,           # Total cache size in bytes (default: 4KB)
        block_size: int = 64,       # Cache line size in bytes (default: 64B)
        associativity: int = 4,     # Number of ways (default: 4-way)
        address_bits: int = 32      # Address bus width (default: 32-bit)
    ):
        """
        Initialize the cache simulator.
        
        Args:
            size: Total cache size in bytes
            block_size: Size of each cache line in bytes
            associativity: Number of ways per set
            address_bits: Number of bits in address
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validation
        if size <= 0 or block_size <= 0 or associativity <= 0:
            raise ValueError("Size, block_size, and associativity must be positive")
        if size % block_size != 0:
            raise ValueError(f"Cache size must be multiple of block_size")
        if not self._is_power_of_2(block_size):
            raise ValueError("block_size must be power of 2")
        
        self.size = size
        self.block_size = block_size
        self.associativity = associativity
        self.address_bits = address_bits
        
        # Calculate cache organization
        self.num_blocks = size // block_size
        self.num_sets = self.num_blocks // associativity
        
        if not self._is_power_of_2(self.num_sets):
            raise ValueError("Number of sets must be power of 2")
        
        # Calculate bit field sizes
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(self.num_sets))
        self.tag_bits = address_bits - self.index_bits - self.offset_bits
        
        # Initialize cache storage: [set][way] -> CacheLine
        self.cache: List[List[CacheLine]] = [
            [CacheLine() for _ in range(associativity)]
            for _ in range(self.num_sets)
        ]
        
        # Statistics
        self.read_hits = 0
        self.read_misses = 0
        self.write_hits = 0
        self.write_misses = 0
        self.evictions = 0
        self.dirty_evictions = 0
        
        # Global LRU counter
        self.global_lru_counter = 0
        
        self._print_config()
    
    @staticmethod
    def _is_power_of_2(n: int) -> bool:
        """Check if n is a power of 2"""
        return n > 0 and (n & (n - 1)) == 0
    
    def _print_config(self) -> None:
        """Print cache configuration"""
        print("=" * 70)
        print("Cache Configuration")
        print("=" * 70)
        print(f"Total Size:        {self.size:,} bytes ({self.size // 1024} KB)")
        print(f"Block Size:        {self.block_size} bytes")
        print(f"Associativity:     {self.associativity}-way")
        print(f"Number of Sets:    {self.num_sets}")
        print(f"Number of Blocks:  {self.num_blocks}")
        print()
        print(f"Address Decomposition ({self.address_bits} bits):")
        print(f"  Tag:     {self.tag_bits} bits")
        print(f"  Index:   {self.index_bits} bits")
        print(f"  Offset:  {self.offset_bits} bits")
        print("=" * 70)
        print()
    
    def _decompose_address(self, address: int) -> Tuple[int, int, int]:
        """
        Decompose address into tag, index, and offset.
        
        Args:
            address: Memory address
        
        Returns:
            Tuple of (tag, index, offset)
        """
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = (address >> (self.offset_bits + self.index_bits)) & ((1 << self.tag_bits) - 1)
        return tag, index, offset
    
    def _find_line(self, set_idx: int, tag: int) -> Optional[int]:
        """
        Search for a cache line with matching tag in a set.
        
        Args:
            set_idx: Set index
            tag: Tag to search for
        
        Returns:
            Way index if found, None otherwise
        """
        for way in range(self.associativity):
            line = self.cache[set_idx][way]
            if line.valid and line.tag == tag:
                return way
        return None
    
    def _find_victim(self, set_idx: int) -> int:
        """
        Find victim line for replacement using LRU policy.
        
        Args:
            set_idx: Set index
        
        Returns:
            Way index of victim line
        """
        # First, check for invalid (empty) lines
        for way in range(self.associativity):
            if not self.cache[set_idx][way].valid:
                return way
        
        # All valid: use LRU
        lru_way = 0
        min_lru = self.cache[set_idx][0].lru_counter
        for way in range(1, self.associativity):
            if self.cache[set_idx][way].lru_counter < min_lru:
                min_lru = self.cache[set_idx][way].lru_counter
                lru_way = way
        
        return lru_way
    
    def _update_lru(self, set_idx: int, way: int) -> None:
        """
        Update LRU counters for a set after accessing a way.
        
        Args:
            set_idx: Set index
            way: Way that was just accessed
        """
        self.global_lru_counter += 1
        self.cache[set_idx][way].lru_counter = self.global_lru_counter
    
    def access(self, address: int, access_type: AccessType, verbose: bool = True) -> bool:
        """
        Simulate a cache access (read or write).
        
        Args:
            address: Memory address to access
            access_type: READ or WRITE
            verbose: Whether to print detailed output
        
        Returns:
            True if hit, False if miss
        """
        tag, index, offset = self._decompose_address(address)
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"Cache Access: {access_type.value} 0x{address:08X}")
            print(f"{'=' * 70}")
            print(f"Tag:    0x{tag:0{(self.tag_bits + 3) // 4}X}    (bits {self.address_bits-1}:{self.offset_bits + self.index_bits})")
            print(f"Index:  0x{index:0{(self.index_bits + 3) // 4}X}    (bits {self.offset_bits + self.index_bits - 1}:{self.offset_bits})")
            print(f"Offset: 0x{offset:0{(self.offset_bits + 3) // 4}X}    (bits {self.offset_bits - 1}:0)")
            print()
        
        # Search for the line
        way = self._find_line(index, tag)
        
        if way is not None:
            # Cache HIT
            hit = True
            if access_type == AccessType.READ:
                self.read_hits += 1
            else:
                self.write_hits += 1
                self.cache[index][way].dirty = True
            
            self._update_lru(index, way)
            
            if verbose:
                print(f"Result: HIT (Set {index}, Way {way})")
                if access_type == AccessType.WRITE:
                    print(f"Action: Mark dirty bit")
        
        else:
            # Cache MISS
            hit = False
            if access_type == AccessType.READ:
                self.read_misses += 1
            else:
                self.write_misses += 1
            
            # Find victim
            victim_way = self._find_victim(index)
            victim_line = self.cache[index][victim_way]
            
            if verbose:
                print(f"Result: MISS")
                if victim_line.valid:
                    print(f"Action: Evict Set {index}, Way {victim_way} (Tag 0x{victim_line.tag:X})")
                    if victim_line.dirty:
                        print(f"        └─ Dirty line → Write back to memory")
                        self.dirty_evictions += 1
                else:
                    print(f"Action: Load into Set {index}, Way {victim_way} (cold start)")
            
            # Evict if necessary
            if victim_line.valid:
                self.evictions += 1
                # In real cache: if dirty, write back to memory here
            
            # Load new line
            victim_line.valid = True
            victim_line.tag = tag
            victim_line.dirty = (access_type == AccessType.WRITE)
            self._update_lru(index, victim_way)
        
        if verbose:
            self._print_set_state(index)
        
        return hit
    
    def read(self, address: int, verbose: bool = True) -> bool:
        """Perform a cache read"""
        return self.access(address, AccessType.READ, verbose)
    
    def write(self, address: int, verbose: bool = True) -> bool:
        """Perform a cache write"""
        return self.access(address, AccessType.WRITE, verbose)
    
    def _print_set_state(self, set_idx: int) -> None:
        """Print the state of a specific set"""
        print(f"\nCache State (Set {set_idx}):")
        print(f"{'Way':<5} {'Valid':<7} {'Dirty':<7} {'Tag':<12} {'LRU Counter':<12}")
        print("-" * 50)
        for way in range(self.associativity):
            line = self.cache[set_idx][way]
            valid_str = "1" if line.valid else "0"
            dirty_str = "1" if line.dirty else "0"
            tag_str = f"0x{line.tag:X}" if line.valid else "-"
            lru_str = str(line.lru_counter) if line.valid else "-"
            print(f"{way:<5} {valid_str:<7} {dirty_str:<7} {tag_str:<12} {lru_str:<12}")
    
    def print_stats(self) -> None:
        """Print cache statistics"""
        total_reads = self.read_hits + self.read_misses
        total_writes = self.write_hits + self.write_misses
        total_accesses = total_reads + total_writes
        total_hits = self.read_hits + self.write_hits
        total_misses = self.read_misses + self.write_misses
        
        print(f"\n{'=' * 70}")
        print("Cache Statistics")
        print("=" * 70)
        print(f"Total Accesses:    {total_accesses:,}")
        print(f"  Reads:           {total_reads:,}  (Hits: {self.read_hits:,}, Misses: {self.read_misses:,})")
        print(f"  Writes:          {total_writes:,}  (Hits: {self.write_hits:,}, Misses: {self.write_misses:,})")
        print()
        print(f"Total Hits:        {total_hits:,}")
        print(f"Total Misses:      {total_misses:,}")
        
        if total_accesses > 0:
            hit_rate = (total_hits / total_accesses) * 100
            miss_rate = (total_misses / total_accesses) * 100
            print(f"Hit Rate:          {hit_rate:.2f}%")
            print(f"Miss Rate:         {miss_rate:.2f}%")
        
        print()
        print(f"Evictions:         {self.evictions:,}")
        print(f"  Dirty Evictions: {self.dirty_evictions:,}")
        print("=" * 70)
    
    def reset_stats(self) -> None:
        """Reset all statistics counters"""
        self.read_hits = 0
        self.read_misses = 0
        self.write_hits = 0
        self.write_misses = 0
        self.evictions = 0
        self.dirty_evictions = 0


def demo_basic_usage():
    """Demonstrate basic cache usage"""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Cache Usage")
    print("=" * 70)
    
    cache = Cache(size=4096, associativity=4, block_size=64)
    
    # Cold miss
    cache.read(0x00401000)
    
    # Hit (same cache line)
    cache.read(0x00401004)
    
    # Write hit
    cache.write(0x00401008)
    
    # New cache line (cold miss)
    cache.read(0x00402000)
    
    cache.print_stats()


def demo_conflict_misses():
    """Demonstrate conflict misses in direct-mapped cache"""
    print("\n" + "=" * 70)
    print("DEMO 2: Conflict Misses (Direct-Mapped)")
    print("=" * 70)
    
    # Direct-mapped cache (1-way)
    cache = Cache(size=1024, associativity=1, block_size=64)
    
    # Two addresses that map to the same set
    addr1 = 0x00001000
    addr2 = 0x00001400  # Different tag, same index
    
    cache.read(addr1, verbose=False)  # Miss
    cache.read(addr1, verbose=False)  # Hit
    cache.read(addr2, verbose=False)  # Miss (conflict!)
    cache.read(addr1, verbose=False)  # Miss (evicted by addr2!)
    
    cache.print_stats()


def demo_spatial_locality():
    """Demonstrate spatial locality benefits"""
    print("\n" + "=" * 70)
    print("DEMO 3: Spatial Locality")
    print("=" * 70)
    
    cache = Cache(size=4096, associativity=4, block_size=64)
    
    base = 0x00400000
    print("Accessing consecutive addresses (same cache line)...")
    
    for i in range(0, 64, 4):  # Access every 4 bytes in same line
        cache.read(base + i, verbose=False)
    
    cache.print_stats()


def demo_lru_replacement():
    """Demonstrate LRU replacement policy"""
    print("\n" + "=" * 70)
    print("DEMO 4: LRU Replacement Policy")
    print("=" * 70)
    
    # 4-way cache, accessing 5 different lines that map to same set
    cache = Cache(size=1024, associativity=4, block_size=64)
    
    # These addresses map to set 0 with different tags
    addresses = [0x0000, 0x0400, 0x0800, 0x0C00, 0x1000]
    
    print("Filling all 4 ways of set 0...")
    for addr in addresses[:4]:
        cache.read(addr, verbose=False)
    
    print("\nAccessing 5th address (will evict LRU)...")
    cache.read(addresses[4])
    
    cache.print_stats()


def main():
    """Main entry point for demonstrations"""
    demo_basic_usage()
    demo_conflict_misses()
    demo_spatial_locality()
    demo_lru_replacement()
    
    print("\n" + "=" * 70)
    print("All demos completed! Explore the code and try your own scenarios.")
    print("=" * 70)


if __name__ == "__main__":
    main()

