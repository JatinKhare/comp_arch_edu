"""
Memory Hierarchy Performance Analyzer
======================================

This module provides tools to analyze and model memory hierarchy performance:
- EMAT (Effective Memory Access Time) calculations
- CPI (Cycles Per Instruction) analysis
- Cache configuration comparisons
- TLB performance modeling

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from typing import Dict, List
from dataclasses import dataclass
import math
import argparse


@dataclass
class CacheConfig:
    """Cache configuration"""
    name: str
    hit_time: float  # cycles
    miss_rate: float  # 0.0 to 1.0
    miss_penalty: float  # cycles (if last level, else next level time)


class PerformanceAnalyzer:
    """Analyze memory hierarchy performance"""
    
    @staticmethod
    def emat_single_level(hit_time: float, miss_rate: float, miss_penalty: float) -> float:
        """
        Calculate Effective Memory Access Time for single-level cache.
        
        EMAT = Hit_Time + Miss_Rate × Miss_Penalty
        
        Args:
            hit_time: Cache hit time in cycles
            miss_rate: Cache miss rate (0.0 to 1.0)
            miss_penalty: Miss penalty in cycles
        
        Returns:
            EMAT in cycles
        """
        return hit_time + miss_rate * miss_penalty
    
    @staticmethod
    def emat_multi_level(
        l1_hit: float, l1_miss_rate: float,
        l2_hit: float, l2_miss_rate: float,
        mem_time: float
    ) -> float:
        """
        Calculate EMAT for two-level cache hierarchy.
        
        Args:
            l1_hit: L1 hit time
            l1_miss_rate: L1 miss rate
            l2_hit: L2 hit time
            l2_miss_rate: L2 local miss rate (of L1 misses)
            mem_time: Memory access time
        
        Returns:
            EMAT in cycles
        """
        return l1_hit + l1_miss_rate * (l2_hit + l2_miss_rate * mem_time)
    
    @staticmethod
    def emat_three_level(
        l1_hit: float, l1_miss_rate: float,
        l2_hit: float, l2_miss_rate: float,
        l3_hit: float, l3_miss_rate: float,
        mem_time: float
    ) -> float:
        """Calculate EMAT for three-level cache hierarchy"""
        return l1_hit + l1_miss_rate * (
            l2_hit + l2_miss_rate * (
                l3_hit + l3_miss_rate * mem_time
            )
        )
    
    @staticmethod
    def calculate_cpi(
        base_cpi: float,
        inst_per_instr: float,  # Instructions fetches per instruction (usually 1)
        data_per_instr: float,  # Data accesses per instruction
        inst_miss_rate: float,
        data_miss_rate: float,
        miss_penalty: float
    ) -> float:
        """
        Calculate effective CPI including memory stalls.
        
        CPI = Base_CPI + Instruction_Stalls + Data_Stalls
        
        Args:
            base_cpi: Base CPI (no memory stalls)
            inst_per_instr: Instruction fetches per instruction
            data_per_instr: Data accesses per instruction
            inst_miss_rate: Instruction cache miss rate
            data_miss_rate: Data cache miss rate
            miss_penalty: Miss penalty in cycles
        
        Returns:
            Effective CPI
        """
        inst_stalls = inst_per_instr * inst_miss_rate * miss_penalty
        data_stalls = data_per_instr * data_miss_rate * miss_penalty
        return base_cpi + inst_stalls + data_stalls
    
    @staticmethod
    def tlb_overhead(
        tlb_hit_time: float,
        tlb_miss_rate: float,
        page_walk_time: float
    ) -> float:
        """
        Calculate average TLB overhead.
        
        Args:
            tlb_hit_time: TLB hit time in cycles
            tlb_miss_rate: TLB miss rate
            page_walk_time: Page walk time in cycles
        
        Returns:
            Average TLB access time in cycles
        """
        return tlb_hit_time + tlb_miss_rate * page_walk_time
    
    @staticmethod
    def combined_cache_tlb(
        tlb_hit_time: float,
        tlb_miss_rate: float,
        page_walk_time: float,
        cache_hit_time: float,
        cache_miss_rate: float,
        cache_miss_penalty: float
    ) -> float:
        """
        Calculate combined TLB + Cache access time.
        
        Considers all four cases:
        1. TLB hit, Cache hit
        2. TLB hit, Cache miss
        3. TLB miss, Cache hit
        4. TLB miss, Cache miss
        
        Args:
            tlb_hit_time: TLB hit time
            tlb_miss_rate: TLB miss rate
            page_walk_time: Page walk time
            cache_hit_time: Cache hit time
            cache_miss_rate: Cache miss rate
            cache_miss_penalty: Cache miss penalty
        
        Returns:
            Average access time in cycles
        """
        tlb_hit_rate = 1 - tlb_miss_rate
        cache_hit_rate = 1 - cache_miss_rate
        
        # Case 1: TLB hit, Cache hit
        case1_prob = tlb_hit_rate * cache_hit_rate
        case1_time = tlb_hit_time + cache_hit_time
        
        # Case 2: TLB hit, Cache miss
        case2_prob = tlb_hit_rate * cache_miss_rate
        case2_time = tlb_hit_time + cache_miss_penalty
        
        # Case 3: TLB miss, Cache hit
        case3_prob = tlb_miss_rate * cache_hit_rate
        case3_time = page_walk_time + cache_hit_time
        
        # Case 4: TLB miss, Cache miss
        case4_prob = tlb_miss_rate * cache_miss_rate
        case4_time = page_walk_time + cache_miss_penalty
        
        return (case1_prob * case1_time +
                case2_prob * case2_time +
                case3_prob * case3_time +
                case4_prob * case4_time)
    
    @staticmethod
    def speedup(time_old: float, time_new: float) -> float:
        """Calculate speedup"""
        return time_old / time_new
    
    @staticmethod
    def ipc_from_cpi(cpi: float) -> float:
        """Calculate IPC from CPI"""
        return 1.0 / cpi


def demo_emat_analysis():
    """Demonstrate EMAT calculation"""
    print("=" * 70)
    print("DEMO: Effective Memory Access Time (EMAT) Analysis")
    print("=" * 70)
    print()
    
    analyzer = PerformanceAnalyzer()
    
    # Single-level cache
    print("Single-Level Cache:")
    print("  Hit time: 1 cycle")
    print("  Miss penalty: 200 cycles")
    print()
    
    for miss_rate in [0.01, 0.02, 0.05, 0.10]:
        emat = analyzer.emat_single_level(
            hit_time=1,
            miss_rate=miss_rate,
            miss_penalty=200
        )
        print(f"  Miss rate {miss_rate*100:4.1f}%: EMAT = {emat:6.2f} cycles")
    
    print()
    
    # Multi-level cache
    print("Two-Level Cache Hierarchy:")
    emat_l1_only = analyzer.emat_single_level(1, 0.05, 200)
    emat_with_l2 = analyzer.emat_multi_level(
        l1_hit=1, l1_miss_rate=0.05,
        l2_hit=12, l2_miss_rate=0.20,
        mem_time=200
    )
    
    print(f"  L1 only:          EMAT = {emat_l1_only:.2f} cycles")
    print(f"  L1 + L2:          EMAT = {emat_with_l2:.2f} cycles")
    print(f"  Speedup from L2:  {emat_l1_only / emat_with_l2:.2f}×")
    print()


def demo_cpi_analysis():
    """Demonstrate CPI analysis"""
    print("=" * 70)
    print("DEMO: CPI Impact Analysis")
    print("=" * 70)
    print()
    
    analyzer = PerformanceAnalyzer()
    
    base_cpi = 1.0
    inst_per_instr = 1.0
    data_per_instr = 0.3
    miss_penalty = 100
    
    print(f"Configuration:")
    print(f"  Base CPI:          {base_cpi}")
    print(f"  Inst/instr:        {inst_per_instr}")
    print(f"  Data accesses:     {data_per_instr}")
    print(f"  Miss penalty:      {miss_penalty} cycles")
    print()
    
    configs = [
        ("Perfect cache", 0.00, 0.00),
        ("Excellent", 0.01, 0.01),
        ("Good", 0.02, 0.03),
        ("Average", 0.05, 0.05),
        ("Poor", 0.10, 0.10),
    ]
    
    print(f"{'Config':<15} {'I$ MR':<8} {'D$ MR':<8} {'CPI':<8} {'IPC':<8} {'vs Perfect':<10}")
    print("-" * 70)
    
    baseline_cpi = None
    for name, i_mr, d_mr in configs:
        cpi = analyzer.calculate_cpi(
            base_cpi, inst_per_instr, data_per_instr,
            i_mr, d_mr, miss_penalty
        )
        ipc = analyzer.ipc_from_cpi(cpi)
        
        if baseline_cpi is None:
            baseline_cpi = cpi
            slowdown = 1.0
        else:
            slowdown = cpi / baseline_cpi
        
        print(f"{name:<15} {i_mr*100:5.1f}%   {d_mr*100:5.1f}%   {cpi:6.2f}   {ipc:6.3f}   {slowdown:5.2f}×")
    
    print()


def demo_tlb_impact():
    """Demonstrate TLB performance impact"""
    print("=" * 70)
    print("DEMO: TLB Performance Impact")
    print("=" * 70)
    print()
    
    analyzer = PerformanceAnalyzer()
    
    tlb_hit_time = 1
    page_walk_time = 800  # 4-level page walk
    
    print(f"TLB Configuration:")
    print(f"  TLB hit time:      {tlb_hit_time} cycle")
    print(f"  Page walk time:    {page_walk_time} cycles")
    print()
    
    print(f"{'TLB Entries':<15} {'Coverage (4KB)':<20} {'Miss Rate':<12} {'Avg Time':<12}")
    print("-" * 70)
    
    working_set = 128 * 1024 * 1024  # 128 MB
    
    for num_entries in [32, 64, 128, 256, 512]:
        coverage = num_entries * 4096
        miss_rate = max(0.0, 1.0 - coverage / working_set)
        avg_time = analyzer.tlb_overhead(tlb_hit_time, miss_rate, page_walk_time)
        
        print(f"{num_entries:<15} {coverage // 1024:8} KB          {miss_rate*100:8.2f}%    {avg_time:8.1f} cycles")
    
    print()
    
    # With huge pages
    print("With 2MB Huge Pages:")
    print(f"{'TLB Entries':<15} {'Coverage (2MB)':<20} {'Miss Rate':<12} {'Avg Time':<12}")
    print("-" * 70)
    
    for num_entries in [32, 64, 128, 256, 512]:
        coverage = num_entries * 2 * 1024 * 1024
        miss_rate = max(0.0, 1.0 - coverage / working_set)
        avg_time = analyzer.tlb_overhead(tlb_hit_time, miss_rate, page_walk_time)
        
        print(f"{num_entries:<15} {coverage // (1024*1024):8} MB          {miss_rate*100:8.2f}%    {avg_time:8.1f} cycles")
    
    print()


def demo_combined_analysis():
    """Demonstrate combined cache + TLB analysis"""
    print("=" * 70)
    print("DEMO: Combined Cache + TLB Analysis")
    print("=" * 70)
    print()
    
    analyzer = PerformanceAnalyzer()
    
    scenarios = [
        ("Best case", 0.99, 0.99),
        ("Typical", 0.95, 0.95),
        ("Cache cold", 0.95, 0.50),
        ("TLB cold", 0.50, 0.95),
        ("Both cold", 0.50, 0.50),
    ]
    
    tlb_hit = 1
    page_walk = 800
    cache_hit = 1
    cache_miss = 200
    
    print(f"Configuration:")
    print(f"  TLB hit:           {tlb_hit} cycle")
    print(f"  Page walk:         {page_walk} cycles")
    print(f"  Cache hit:         {cache_hit} cycle")
    print(f"  Cache miss:        {cache_miss} cycles")
    print()
    
    print(f"{'Scenario':<15} {'TLB HR':<8} {'Cache HR':<10} {'Avg Time':<12} {'vs Best':<10}")
    print("-" * 70)
    
    best_time = None
    for name, tlb_hr, cache_hr in scenarios:
        avg_time = analyzer.combined_cache_tlb(
            tlb_hit, 1 - tlb_hr, page_walk,
            cache_hit, 1 - cache_hr, cache_miss
        )
        
        if best_time is None:
            best_time = avg_time
            relative = 1.0
        else:
            relative = avg_time / best_time
        
        print(f"{name:<15} {tlb_hr*100:5.1f}%   {cache_hr*100:6.1f}%     {avg_time:8.1f}     {relative:5.2f}×")
    
    print()


def demo_optimization_impact():
    """Demonstrate impact of various optimizations"""
    print("=" * 70)
    print("DEMO: Optimization Impact")
    print("=" * 70)
    print()
    
    analyzer = PerformanceAnalyzer()
    
    # Baseline system
    baseline_emat = analyzer.emat_single_level(1, 0.05, 200)
    
    optimizations = [
        ("Baseline", 1, 0.05, 200),
        ("Reduce miss rate 1%", 1, 0.04, 200),
        ("Reduce miss penalty 10%", 1, 0.05, 180),
        ("Faster hit (pipelined)", 0.5, 0.05, 200),
        ("All improvements", 0.5, 0.04, 180),
    ]
    
    print(f"{'Optimization':<25} {'Hit Time':<10} {'MR':<8} {'Penalty':<10} {'EMAT':<10} {'Speedup':<10}")
    print("-" * 90)
    
    for name, hit, mr, penalty in optimizations:
        emat = analyzer.emat_single_level(hit, mr, penalty)
        speedup = baseline_emat / emat
        
        print(f"{name:<25} {hit:8.1f}   {mr*100:5.1f}%   {penalty:8.0f}   {emat:8.2f}   {speedup:8.2f}×")
    
    print()


def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(
        description="Performance Analyzer - Calculate EMAT, CPI, and TLB performance metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all demos
  python performance_analyzer.py

  # Run specific demo
  python performance_analyzer.py --demo emat
  python performance_analyzer.py --demo cpi
  python performance_analyzer.py --demo tlb

  # Calculate EMAT for specific cache
  python performance_analyzer.py --emat --hit-time 1 --miss-rate 0.05 --miss-penalty 200
        """
    )
    
    parser.add_argument(
        "--demo",
        choices=["emat", "cpi", "tlb", "combined", "optimization", "all"],
        default="all",
        help="Run specific demo (default: all)"
    )
    
    # EMAT calculation arguments
    parser.add_argument(
        "--emat",
        action="store_true",
        help="Calculate EMAT for single-level cache"
    )
    
    parser.add_argument(
        "--hit-time",
        type=float,
        default=1.0,
        help="Cache hit time in cycles (for EMAT calculation)"
    )
    
    parser.add_argument(
        "--miss-rate",
        type=float,
        default=0.05,
        help="Cache miss rate (0.0 to 1.0, for EMAT calculation)"
    )
    
    parser.add_argument(
        "--miss-penalty",
        type=float,
        default=200.0,
        help="Cache miss penalty in cycles (for EMAT calculation)"
    )
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer()
    
    # Handle direct EMAT calculation
    if args.emat:
        emat = analyzer.emat_single_level(
            args.hit_time,
            args.miss_rate,
            args.miss_penalty
        )
        print(f"\nEMAT Calculation:")
        print(f"  Hit Time:     {args.hit_time} cycles")
        print(f"  Miss Rate:    {args.miss_rate * 100:.2f}%")
        print(f"  Miss Penalty: {args.miss_penalty} cycles")
        print(f"  EMAT:         {emat:.2f} cycles")
        return
    
    # Run demos
    if args.demo == "emat" or args.demo == "all":
        demo_emat_analysis()
    
    if args.demo == "cpi" or args.demo == "all":
        demo_cpi_analysis()
    
    if args.demo == "tlb" or args.demo == "all":
        demo_tlb_impact()
    
    if args.demo == "combined" or args.demo == "all":
        demo_combined_analysis()
    
    if args.demo == "optimization" or args.demo == "all":
        demo_optimization_impact()
    
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("1. Memory stalls dominate CPI for cache-intensive workloads")
    print("2. 1% miss rate reduction = 2 cycles saved (at 200cy penalty)")
    print("3. TLB misses are VERY expensive (800+ cycles)")
    print("4. Huge pages dramatically improve TLB performance")
    print("5. Combined cache+TLB effects multiply")
    print("=" * 70)


if __name__ == "__main__":
    main()

