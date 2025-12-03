// Memory Hierarchy Educational Web Application - Frontend
// JavaScript for interactive visualizations

const API_BASE = 'http://localhost:5000/api';

// Tab management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Cache Simulator Functions
async function configureCache() {
    const size = parseInt(document.getElementById('cache-size').value);
    const associativity = parseInt(document.getElementById('cache-assoc').value);
    const blockSize = parseInt(document.getElementById('cache-block').value);
    
    try {
        const response = await fetch(`${API_BASE}/cache/configure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size, associativity, block_size: blockSize })
        });
        
        const data = await response.json();
        if (data.success) {
            displayCacheConfig(data.config);
        } else {
            showError('cache-results', data.error);
        }
    } catch (error) {
        showError('cache-results', `Error: ${error.message}`);
    }
}

function displayCacheConfig(config) {
    const results = document.getElementById('cache-results');
    results.innerHTML = `
        <div class="result-item">
            <h4>Cache Configuration</h4>
            <p><strong>Total Size:</strong> ${config.size.toLocaleString()} bytes (${config.size / 1024} KB)</p>
            <p><strong>Associativity:</strong> ${config.associativity}-way</p>
            <p><strong>Block Size:</strong> ${config.block_size} bytes</p>
            <p><strong>Number of Sets:</strong> ${config.num_sets}</p>
            <p><strong>Number of Blocks:</strong> ${config.num_blocks}</p>
        </div>
        <div class="result-item">
            <h4>Address Decomposition</h4>
            <p><strong>Tag Bits:</strong> ${config.tag_bits}</p>
            <p><strong>Index Bits:</strong> ${config.index_bits}</p>
            <p><strong>Offset Bits:</strong> ${config.offset_bits}</p>
        </div>
    `;
}

async function accessCache() {
    const size = parseInt(document.getElementById('cache-size').value);
    const associativity = parseInt(document.getElementById('cache-assoc').value);
    const blockSize = parseInt(document.getElementById('cache-block').value);
    const address = document.getElementById('cache-addr').value;
    const accessType = document.getElementById('cache-type').value;
    
    try {
        const response = await fetch(`${API_BASE}/cache/access`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                size,
                associativity,
                block_size: blockSize,
                address,
                type: accessType
            })
        });
        
        const data = await response.json();
        if (data.success) {
            displayCacheAccess(data);
        } else {
            showError('cache-results', data.error);
        }
    } catch (error) {
        showError('cache-results', `Error: ${error.message}`);
    }
}

function displayCacheAccess(data) {
    const results = document.getElementById('cache-results');
    const hitClass = data.hit ? 'success' : 'error';
    const hitText = data.hit ? 'HIT' : 'MISS';
    
    results.innerHTML = `
        <div class="result-item">
            <h4>Access Result: <span class="${hitClass}">${hitText}</span></h4>
            <p><strong>Address:</strong> ${data.address}</p>
        </div>
        <div class="result-item">
            <h4>Address Decomposition</h4>
            <div class="decomposition">
                <div class="decomp-part">Tag: ${data.decomposition.tag}</div>
                <div class="decomp-separator">|</div>
                <div class="decomp-part">Index: ${data.decomposition.index}</div>
                <div class="decomp-separator">|</div>
                <div class="decomp-part">Offset: ${data.decomposition.offset}</div>
            </div>
            <p><strong>Tag Bits:</strong> ${data.decomposition.tag_bits}</p>
            <p><strong>Index Bits:</strong> ${data.decomposition.index_bits}</p>
            <p><strong>Offset Bits:</strong> ${data.decomposition.offset_bits}</p>
        </div>
        <div class="result-item">
            <h4>Cache Set ${data.decomposition.index} State</h4>
            <div class="cache-state">
                ${data.set_state.map(line => `
                    <div class="cache-line ${line.valid ? 'valid' : ''}">
                        <p><strong>Way ${line.way}</strong></p>
                        <p>Valid: ${line.valid ? 'Yes' : 'No'}</p>
                        <p>Dirty: ${line.dirty ? 'Yes' : 'No'}</p>
                        <p>Tag: ${line.tag || '-'}</p>
                        <p>LRU: ${line.lru_counter || '-'}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        <div class="result-item">
            <h4>Statistics</h4>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">${data.stats.read_hits + data.stats.write_hits}</div>
                    <div class="stat-label">Total Hits</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.stats.read_misses + data.stats.write_misses}</div>
                    <div class="stat-label">Total Misses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.stats.evictions}</div>
                    <div class="stat-label">Evictions</div>
                </div>
            </div>
        </div>
    `;
}

async function showCacheStructure() {
    const size = parseInt(document.getElementById('cache-size').value);
    const associativity = parseInt(document.getElementById('cache-assoc').value);
    const blockSize = parseInt(document.getElementById('cache-block').value);
    
    try {
        const response = await fetch(`${API_BASE}/cache/structure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size, associativity, block_size: blockSize })
        });
        
        const data = await response.json();
        if (data.success) {
            displayCacheStructure(data);
        } else {
            showError('cache-results', data.error);
        }
    } catch (error) {
        showError('cache-results', `Error: ${error.message}`);
    }
}

function displayCacheStructure(data) {
    const results = document.getElementById('cache-results');
    results.innerHTML = `
        <div class="result-item">
            <h4>Cache Structure</h4>
            <p><strong>Total Size:</strong> ${data.config.size.toLocaleString()} bytes</p>
            <p><strong>Associativity:</strong> ${data.config.associativity}-way</p>
            <p><strong>Block Size:</strong> ${data.config.block_size} bytes</p>
            <p><strong>Number of Sets:</strong> ${data.config.num_sets}</p>
        </div>
        <div class="result-item">
            <h4>Bit Field Breakdown</h4>
            <p><strong>Tag Bits:</strong> ${data.config.tag_bits} (range: 0x0 to 0x${(1 << data.config.tag_bits - 1).toString(16).toUpperCase()})</p>
            <p><strong>Index Bits:</strong> ${data.config.index_bits} (range: 0x0 to 0x${(data.config.num_sets - 1).toString(16).toUpperCase()})</p>
            <p><strong>Offset Bits:</strong> ${data.config.offset_bits} (range: 0x0 to 0x${(data.config.block_size - 1).toString(16).toUpperCase()})</p>
        </div>
        <div class="result-item">
            <h4>Example Address Decompositions</h4>
            ${data.examples.map(ex => `
                <div class="code-block">
Address: ${ex.address}
  Tag:    ${ex.tag} (bits ${data.config.tag_bits + data.config.index_bits + data.config.offset_bits - 1}:${data.config.index_bits + data.config.offset_bits})
  Index:  ${ex.index} (bits ${data.config.index_bits + data.config.offset_bits - 1}:${data.config.offset_bits})
  Offset: ${ex.offset} (bits ${data.config.offset_bits - 1}:0)
                </div>
            `).join('')}
        </div>
    `;
}

// VIPT Analyzer Functions
async function analyzeVIPT() {
    const cacheSize = parseInt(document.getElementById('vipt-cache-size').value);
    const associativity = parseInt(document.getElementById('vipt-assoc').value);
    const blockSize = parseInt(document.getElementById('vipt-block').value);
    const pageSize = parseInt(document.getElementById('vipt-page-size').value);
    
    try {
        const response = await fetch(`${API_BASE}/vipt/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cache_size: cacheSize,
                associativity,
                block_size: blockSize,
                page_size: pageSize
            })
        });
        
        const data = await response.json();
        if (data.success) {
            displayVIPTResults(data);
        } else {
            showError('vipt-results', data.error);
        }
    } catch (error) {
        showError('vipt-results', `Error: ${error.message}`);
    }
}

function displayVIPTResults(data) {
    const results = document.getElementById('vipt-results');
    const safeClass = data.is_safe ? 'success' : 'error';
    const safeIcon = data.is_safe ? '✓' : '✗';
    
    results.innerHTML = `
        <div class="result-item">
            <h4>VIPT Safety Analysis</h4>
            <p><strong>Status:</strong> <span class="${safeClass}">${safeIcon} ${data.message}</span></p>
        </div>
        <div class="result-item">
            <h4>Configuration</h4>
            <p><strong>Cache Size:</strong> ${data.cache_size.toLocaleString()} bytes</p>
            <p><strong>Associativity:</strong> ${data.associativity}-way</p>
            <p><strong>Block Size:</strong> ${data.block_size} bytes</p>
            <p><strong>Page Size:</strong> ${(data.page_size / 1024).toLocaleString()} KB</p>
            <p><strong>Number of Sets:</strong> ${data.num_sets}</p>
        </div>
        <div class="result-item">
            <h4>Bit Analysis</h4>
            <p><strong>Index Bits:</strong> ${data.index_bits}</p>
            <p><strong>Page Offset Bits:</strong> ${data.page_offset_bits}</p>
            <p><strong>Comparison:</strong> ${data.index_bits} ${data.is_safe ? '≤' : '>'} ${data.page_offset_bits}</p>
            ${!data.is_safe ? '<p class="warning">⚠️ Warning: Index bits exceed page offset bits. Synonym problem possible!</p>' : ''}
        </div>
    `;
}

// TLB Functions
async function translateTLB() {
    const numEntries = parseInt(document.getElementById('tlb-entries').value);
    const va = document.getElementById('tlb-va').value;
    const pageSize = document.getElementById('tlb-page-size').value;
    
    try {
        const response = await fetch(`${API_BASE}/tlb/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_entries: numEntries,
                va,
                page_size: pageSize
            })
        });
        
        const data = await response.json();
        if (data.success) {
            displayTLBResults(data);
        } else {
            showError('tlb-results', data.error);
        }
    } catch (error) {
        showError('tlb-results', `Error: ${error.message}`);
    }
}

function displayTLBResults(data) {
    const results = document.getElementById('tlb-results');
    const hitClass = data.hit ? 'success' : 'error';
    const hitText = data.hit ? 'TLB HIT' : 'TLB MISS';
    
    results.innerHTML = `
        <div class="result-item">
            <h4>Translation Result: <span class="${hitClass}">${hitText}</span></h4>
            <p><strong>Virtual Address:</strong> ${data.va}</p>
            <p><strong>Physical Address:</strong> ${data.pa || 'N/A (Page Fault)'}</p>
        </div>
        <div class="result-item">
            <h4>TLB Statistics</h4>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">${data.stats.hits}</div>
                    <div class="stat-label">Hits</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.stats.misses}</div>
                    <div class="stat-label">Misses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${(data.stats.reach / 1024).toFixed(0)} KB</div>
                    <div class="stat-label">TLB Reach</div>
                </div>
            </div>
        </div>
    `;
}

// Page Walk Functions
async function translatePageWalk() {
    const va = document.getElementById('pw-va').value;
    
    try {
        const response = await fetch(`${API_BASE}/pagewalk/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ va })
        });
        
        const data = await response.json();
        if (data.success) {
            displayPageWalkResults(data);
        } else {
            showError('pagewalk-results', data.error);
        }
    } catch (error) {
        showError('pagewalk-results', `Error: ${error.message}`);
    }
}

function displayPageWalkResults(data) {
    const results = document.getElementById('pagewalk-results');
    
    results.innerHTML = `
        <div class="result-item">
            <h4>Page Walk Result</h4>
            <p><strong>Virtual Address:</strong> ${data.va}</p>
            <p><strong>Physical Address:</strong> ${data.pa || 'N/A'}</p>
        </div>
        <div class="result-item">
            <h4>Address Decomposition (RISC-V Sv39)</h4>
            <div class="decomposition">
                <div class="decomp-part">VPN[2]: 0x${data.decomposition.vpn2.toString(16).toUpperCase()}</div>
                <div class="decomp-separator">|</div>
                <div class="decomp-part">VPN[1]: 0x${data.decomposition.vpn1.toString(16).toUpperCase()}</div>
                <div class="decomp-separator">|</div>
                <div class="decomp-part">VPN[0]: 0x${data.decomposition.vpn0.toString(16).toUpperCase()}</div>
                <div class="decomp-separator">|</div>
                <div class="decomp-part">Offset: ${data.decomposition.offset}</div>
            </div>
        </div>
        <div class="result-item">
            <h4>Statistics</h4>
            <p><strong>Page Walks:</strong> ${data.stats.page_walks}</p>
            <p><strong>Page Faults:</strong> ${data.stats.page_faults}</p>
        </div>
    `;
}

// Performance Functions
async function calculateEMAT() {
    const hitTime = parseFloat(document.getElementById('perf-hit-time').value);
    const missRate = parseFloat(document.getElementById('perf-miss-rate').value);
    const missPenalty = parseFloat(document.getElementById('perf-miss-penalty').value);
    
    try {
        const response = await fetch(`${API_BASE}/performance/emat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hit_time: hitTime,
                miss_rate: missRate,
                miss_penalty: missPenalty
            })
        });
        
        const data = await response.json();
        if (data.success) {
            displayEMATResults(data);
        } else {
            showError('performance-results', data.error);
        }
    } catch (error) {
        showError('performance-results', `Error: ${error.message}`);
    }
}

function displayEMATResults(data) {
    const results = document.getElementById('performance-results');
    const hitRate = (1 - data.miss_rate) * 100;
    
    results.innerHTML = `
        <div class="result-item">
            <h4>EMAT Calculation</h4>
            <p><strong>Formula:</strong> EMAT = Hit_Time + Miss_Rate × Miss_Penalty</p>
        </div>
        <div class="result-item">
            <h4>Parameters</h4>
            <p><strong>Hit Time:</strong> ${data.hit_time} cycles</p>
            <p><strong>Miss Rate:</strong> ${(data.miss_rate * 100).toFixed(2)}%</p>
            <p><strong>Hit Rate:</strong> ${hitRate.toFixed(2)}%</p>
            <p><strong>Miss Penalty:</strong> ${data.miss_penalty} cycles</p>
        </div>
        <div class="result-item">
            <h4>Result</h4>
            <div class="stat-box" style="max-width: 300px; margin: 0 auto;">
                <div class="stat-value">${data.emat.toFixed(2)}</div>
                <div class="stat-label">Average Memory Access Time (cycles)</div>
            </div>
            <p style="margin-top: 15px; text-align: center;">
                <strong>Calculation:</strong> ${data.hit_time} + (${data.miss_rate} × ${data.miss_penalty}) = ${data.emat.toFixed(2)} cycles
            </p>
        </div>
    `;
}

// Utility Functions
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="result-item"><p class="error">Error: ${message}</p></div>`;
}

// Initialize: Show cache structure on load
window.addEventListener('load', () => {
    showCacheStructure();
});

