# Module 06: Web-Based Visualizer 🌐

## Overview

This module provides a **fully functional web-based interactive visualizer** for cache, TLB, page walk, and VIPT concepts. The web application provides an intuitive graphical interface for exploring memory hierarchy concepts.

---

## Features

### ✅ Implemented Features

1. **Interactive Cache Simulator**
   - Visual representation of cache sets and ways
   - Real-time address decomposition (tag/index/offset)
   - Hit/miss detection with visual feedback
   - Configurable cache parameters (size, associativity, block size)
   - Cache structure visualization

2. **VIPT Safety Analyzer**
   - Side-by-side comparison of cache and page configurations
   - Validates VIPT safety rule (index_bits ≤ page_offset_bits)
   - Visual indication of safe/unsafe configurations
   - Supports multiple page sizes (4KB, 2MB, 1GB)

3. **TLB Simulator**
   - Virtual-to-physical address translation
   - Multi-page-size support
   - TLB hit/miss statistics
   - TLB reach calculation

4. **Page Walk Simulator**
   - RISC-V Sv39 page table walk
   - Address decomposition visualization
   - Step-by-step translation process

5. **Performance Analyzer**
   - EMAT (Effective Memory Access Time) calculation
   - Interactive parameter adjustment
   - Formula visualization

---

## Technology Stack

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Python Simulators**: Integrates all existing simulators

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **Vanilla JavaScript**: No framework dependencies
- **REST API**: Communication with backend

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. **Install dependencies**:

```bash
cd 06_WebApp
pip install -r requirements.txt
```

2. **Start the server**:

```bash
python app.py
```

3. **Open in browser**:

Navigate to: `http://localhost:5000`

---

## Usage

### Starting the Application

```bash
# From the 06_WebApp directory
python app.py
```

The server will start on `http://localhost:5000` and you'll see:

```
======================================================================
Memory Hierarchy Educational Web Application
======================================================================
Starting server on http://localhost:5000
Open http://localhost:5000 in your browser
======================================================================
```

### Using the Web Interface

1. **Cache Simulator Tab**:
   - Configure cache parameters (size, associativity, block size)
   - Enter a virtual address in hex format (e.g., `0x401000`)
   - Select read or write access
   - Click "Access Cache" to see hit/miss and cache state
   - Click "Show Structure" to see address decomposition

2. **VIPT Analyzer Tab**:
   - Configure cache and page size
   - Click "Analyze VIPT Safety"
   - See if configuration is safe (index_bits ≤ page_offset_bits)

3. **TLB Simulator Tab**:
   - Configure TLB size and page size
   - Enter virtual address
   - Click "Translate" to see VA→PA translation

4. **Page Walk Tab**:
   - Enter virtual address
   - Click "Translate" to see page walk process

5. **Performance Tab**:
   - Enter hit time, miss rate, and miss penalty
   - Click "Calculate EMAT" to see average memory access time

---

## API Endpoints

The Flask backend provides the following REST API endpoints:

### Cache API

- `POST /api/cache/configure` - Configure cache parameters
- `POST /api/cache/access` - Simulate cache access
- `POST /api/cache/structure` - Get cache structure breakdown

### VIPT API

- `POST /api/vipt/analyze` - Analyze VIPT safety

### TLB API

- `POST /api/tlb/translate` - Translate VA to PA using TLB

### Page Walk API

- `POST /api/pagewalk/translate` - Translate VA to PA using page walk

### Performance API

- `POST /api/performance/emat` - Calculate EMAT

---

## Example API Usage

### Using curl

```bash
# Configure cache
curl -X POST http://localhost:5000/api/cache/configure \
  -H "Content-Type: application/json" \
  -d '{"size": 4096, "associativity": 4, "block_size": 64}'

# Access cache
curl -X POST http://localhost:5000/api/cache/access \
  -H "Content-Type: application/json" \
  -d '{"size": 4096, "associativity": 4, "block_size": 64, "address": "0x401000", "type": "read"}'

# Analyze VIPT
curl -X POST http://localhost:5000/api/vipt/analyze \
  -H "Content-Type: application/json" \
  -d '{"cache_size": 32768, "associativity": 4, "block_size": 64, "page_size": 4096}'
```

---

## Project Structure

```
06_WebApp/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── static/               # Frontend files
    ├── index.html        # Main HTML page
    ├── style.css         # Styling
    └── app.js            # Frontend JavaScript
```

---

## Development

### Running in Debug Mode

The Flask app runs in debug mode by default, which provides:
- Automatic reloading on code changes
- Detailed error messages
- Interactive debugger

### Customizing

- **Port**: Change `port=5000` in `app.py` to use a different port
- **Host**: Change `host='0.0.0.0'` to `host='127.0.0.1'` for localhost only
- **Styling**: Modify `static/style.css` to customize appearance
- **Functionality**: Add new endpoints in `app.py` and corresponding UI in `static/app.js`

---

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```python
# Edit app.py, change:
app.run(debug=True, host='0.0.0.0', port=5000)
# To:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### CORS Errors

If you see CORS errors, ensure `flask-cors` is installed:

```bash
pip install flask-cors
```

### Module Import Errors

Make sure you're running from the `06_WebApp` directory and that all simulator modules are in their respective folders.

---

## Future Enhancements

Potential improvements:
- [ ] Real-time cache state visualization with animations
- [ ] Step-by-step page walk visualization
- [ ] Cache line eviction animation
- [ ] Export results as images/PDF
- [ ] Save/load configurations
- [ ] Comparison mode (side-by-side different configs)
- [ ] Performance graphs and charts

---

## Contributing

To add new features:
1. Add API endpoint in `app.py`
2. Add UI elements in `static/index.html`
3. Add JavaScript handlers in `static/app.js`
4. Style with `static/style.css`

---

**Ready to explore memory hierarchy interactively!** 🚀

Start the server and open `http://localhost:5000` in your browser.
