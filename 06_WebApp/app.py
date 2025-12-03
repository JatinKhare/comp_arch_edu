"""
Memory Hierarchy Educational Web Application
============================================

Flask backend API for interactive memory hierarchy visualizations.
Provides REST API endpoints for cache, TLB, page walk, and VIPT simulators.

Author: Memory Hierarchy Educational Repository
Python Version: 3.10+
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
from pathlib import Path

# Add parent directories to path to import simulators
sys.path.insert(0, str(Path(__file__).parent.parent / "01_Cache_Basics"))
sys.path.insert(0, str(Path(__file__).parent.parent / "02_VIPT_PIPT_VIVT"))
sys.path.insert(0, str(Path(__file__).parent.parent / "03_TLB"))
sys.path.insert(0, str(Path(__file__).parent.parent / "04_Page_Walk"))
sys.path.insert(0, str(Path(__file__).parent.parent / "05_Performance_Model"))

from cache_simulator import Cache
from tlb_simulator import TLB, PageSize
from page_walk_sim import RISCV_Sv39_PageWalker
from performance_analyzer import PerformanceAnalyzer

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for frontend


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/cache/configure', methods=['POST'])
def cache_configure():
    """Configure cache parameters"""
    try:
        data = request.json
        size = data.get('size', 4096)
        associativity = data.get('associativity', 4)
        block_size = data.get('block_size', 64)
        address_bits = data.get('address_bits', 32)
        
        cache = Cache(size=size, associativity=associativity, 
                     block_size=block_size, address_bits=address_bits)
        
        return jsonify({
            'success': True,
            'config': {
                'size': cache.size,
                'associativity': cache.associativity,
                'block_size': cache.block_size,
                'num_sets': cache.num_sets,
                'num_blocks': cache.num_blocks,
                'offset_bits': cache.offset_bits,
                'index_bits': cache.index_bits,
                'tag_bits': cache.tag_bits
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cache/access', methods=['POST'])
def cache_access():
    """Simulate cache access"""
    try:
        data = request.json
        size = data.get('size', 4096)
        associativity = data.get('associativity', 4)
        block_size = data.get('block_size', 64)
        address = int(data.get('address', '0x0'), 16)
        access_type = data.get('type', 'read')  # 'read' or 'write'
        
        cache = Cache(size=size, associativity=associativity, 
                     block_size=block_size)
        
        tag, index, offset = cache._decompose_address(address)
        
        if access_type == 'write':
            hit = cache.write(address, verbose=False)
        else:
            hit = cache.read(address, verbose=False)
        
        # Get cache state for the accessed set
        set_state = []
        for way in range(cache.associativity):
            line = cache.cache[index][way]
            set_state.append({
                'way': way,
                'valid': line.valid,
                'dirty': line.dirty,
                'tag': hex(line.tag) if line.valid else None,
                'lru_counter': line.lru_counter
            })
        
        return jsonify({
            'success': True,
            'hit': hit,
            'address': hex(address),
            'decomposition': {
                'tag': hex(tag),
                'index': index,
                'offset': hex(offset),
                'tag_bits': cache.tag_bits,
                'index_bits': cache.index_bits,
                'offset_bits': cache.offset_bits
            },
            'set_state': set_state,
            'stats': {
                'read_hits': cache.read_hits,
                'read_misses': cache.read_misses,
                'write_hits': cache.write_hits,
                'write_misses': cache.write_misses,
                'evictions': cache.evictions
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cache/structure', methods=['POST'])
def cache_structure():
    """Get cache structure breakdown"""
    try:
        data = request.json
        size = data.get('size', 4096)
        associativity = data.get('associativity', 4)
        block_size = data.get('block_size', 64)
        address_bits = data.get('address_bits', 32)
        
        cache = Cache(size=size, associativity=associativity,
                     block_size=block_size, address_bits=address_bits)
        
        # Get example address decompositions
        examples = []
        for addr in [0x00000000, 0x00401000, 0xFFFFFFFF]:
            if addr < (1 << address_bits):
                tag, index, offset = cache._decompose_address(addr)
                examples.append({
                    'address': hex(addr),
                    'tag': hex(tag),
                    'index': index,
                    'offset': hex(offset)
                })
        
        return jsonify({
            'success': True,
            'config': {
                'size': cache.size,
                'associativity': cache.associativity,
                'block_size': cache.block_size,
                'num_sets': cache.num_sets,
                'offset_bits': cache.offset_bits,
                'index_bits': cache.index_bits,
                'tag_bits': cache.tag_bits
            },
            'examples': examples
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/tlb/translate', methods=['POST'])
def tlb_translate():
    """Translate virtual address using TLB"""
    try:
        data = request.json
        num_entries = data.get('num_entries', 64)
        va = int(data.get('va', '0x401000'), 16)
        page_size_str = data.get('page_size', '4KB')
        
        # Convert page size string to enum and get offset bits
        page_size_map = {
            '4KB': (PageSize.KB_4, 12),
            '2MB': (PageSize.MB_2, 21),
            '1GB': (PageSize.GB_1, 30)
        }
        page_size, offset_bits = page_size_map.get(page_size_str, (PageSize.KB_4, 12))
        
        tlb = TLB(num_entries=num_entries)
        
        # Install a default mapping if not exists
        va_page = va & ~((1 << offset_bits) - 1)
        pa_page = (va_page | 0x10000000) & ~((1 << offset_bits) - 1)
        tlb.install_mapping(va_page, pa_page, page_size)
        
        pa = tlb.translate(va, page_size, verbose=False)
        
        return jsonify({
            'success': True,
            'va': hex(va),
            'pa': hex(pa) if pa else None,
            'hit': pa is not None,
            'stats': {
                'hits': tlb.hits,
                'misses': tlb.misses,
                'reach': tlb.hits * page_size.value if tlb.hits > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/pagewalk/translate', methods=['POST'])
def pagewalk_translate():
    """Translate virtual address using page walk"""
    try:
        data = request.json
        va = int(data.get('va', '0x401234'), 16)
        
        walker = RISCV_Sv39_PageWalker(satp_base=0x100000)
        
        # Auto-create mapping if needed
        va_page = va & ~0xFFF
        pa_page = (va_page | 0x10000000) & ~0xFFF
        walker.map_page(va_page, pa_page)
        
        pa = walker.translate(va, verbose=False)
        
        vpn2, vpn1, vpn0, offset = walker._decompose_va(va)
        
        return jsonify({
            'success': True,
            'va': hex(va),
            'pa': hex(pa) if pa else None,
            'decomposition': {
                'vpn2': vpn2,
                'vpn1': vpn1,
                'vpn0': vpn0,
                'offset': hex(offset)
            },
            'stats': {
                'page_walks': walker.page_walks,
                'page_faults': walker.page_faults
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/vipt/analyze', methods=['POST'])
def vipt_analyze():
    """Analyze VIPT safety"""
    try:
        data = request.json
        cache_size = data.get('cache_size', 32768)
        associativity = data.get('associativity', 4)
        block_size = data.get('block_size', 64)
        page_size = data.get('page_size', 4096)
        
        num_sets = cache_size // (block_size * associativity)
        offset_bits = 0
        temp = block_size
        while temp > 1:
            offset_bits += 1
            temp >>= 1
        
        index_bits = 0
        temp = num_sets
        while temp > 1:
            index_bits += 1
            temp >>= 1
        
        page_offset_bits = 0
        temp = page_size
        while temp > 1:
            page_offset_bits += 1
            temp >>= 1
        
        is_safe = index_bits <= page_offset_bits
        
        return jsonify({
            'success': True,
            'cache_size': cache_size,
            'associativity': associativity,
            'block_size': block_size,
            'page_size': page_size,
            'num_sets': num_sets,
            'index_bits': index_bits,
            'page_offset_bits': page_offset_bits,
            'is_safe': is_safe,
            'message': 'SAFE' if is_safe else 'UNSAFE (synonym possible)'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/performance/emat', methods=['POST'])
def performance_emat():
    """Calculate EMAT"""
    try:
        data = request.json
        hit_time = data.get('hit_time', 1.0)
        miss_rate = data.get('miss_rate', 0.05)
        miss_penalty = data.get('miss_penalty', 200.0)
        
        analyzer = PerformanceAnalyzer()
        emat = analyzer.emat_single_level(hit_time, miss_rate, miss_penalty)
        
        return jsonify({
            'success': True,
            'hit_time': hit_time,
            'miss_rate': miss_rate,
            'miss_penalty': miss_penalty,
            'emat': emat
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    print("=" * 70)
    print("Memory Hierarchy Educational Web Application")
    print("=" * 70)
    print("Starting server on http://localhost:5000")
    print("Open http://localhost:5000 in your browser")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)

