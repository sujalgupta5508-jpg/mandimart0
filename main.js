// ============================================
// MANDIMART - COMPLETE JAVASCRIPT
// All interactive features for the marketplace
// ============================================

// ===== DATA STORAGE (Simulated Database) =====
let mandis = [
    {crop:'Tomato', mandi:'Azadpur Mandi', min:1200, max:1800, modal:1500, trend:'up', dist:2.3},
    {crop:'Tomato', mandi:'Ghazipur Mandi', min:1100, max:1700, modal:1400, trend:'down', dist:5.1},
    {crop:'Onion', mandi:'Azadpur Mandi', min:2100, max:2600, modal:2350, trend:'up', dist:2.3},
    {crop:'Onion', mandi:'Keshopur Mandi', min:2000, max:2500, modal:2250, trend:'flat', dist:8.4},
    {crop:'Potato', mandi:'Ghazipur Mandi', min:1400, max:1900, modal:1650, trend:'up', dist:5.1},
    {crop:'Potato', mandi:'Okhla Mandi', min:1350, max:1850, modal:1600, trend:'flat', dist:9.0},
    {crop:'Wheat', mandi:'Narela Mandi', min:2200, max:2450, modal:2325, trend:'up', dist:14.2},
    {crop:'Wheat', mandi:'Karnal Mandi', min:2250, max:2500, modal:2375, trend:'up', dist:120},
    {crop:'Brinjal', mandi:'Azadpur Mandi', min:800, max:1200, modal:1000, trend:'down', dist:2.3},
    {crop:'Carrot', mandi:'Keshopur Mandi', min:1500, max:2000, modal:1750, trend:'up', dist:8.4},
    {crop:'Cauliflower', mandi:'Ghazipur Mandi', min:1800, max:2400, modal:2100, trend:'flat', dist:5.1},
    {crop:'Mango', mandi:'Okhla Mandi', min:3000, max:4500, modal:3750, trend:'up', dist:9.0}
];

let crops = [
    {id:1, name:'Tomato', qty:50, grade:'A', price:1500, img:'🍅', seller:'Ramesh Kumar', rating:4.8},
    {id:2, name:'Onion', qty:120, grade:'B', price:2250, img:'🧅', seller:'Sunita Devi', rating:4.5},
    {id:3, name:'Potato', qty:200, grade:'A', price:1650, img:'🥔', seller:'Gurpreet Singh', rating:4.9},
    {id:4,name:'Tomato', qty:100, grade:'B', price:1500 , img:'🍅',seller:'Sujal Gupta', rating:5.0}
];

let auctions = [];
let nextCropId = 4;
let nextAuctionId = 1;
let bidTimers = {};

// ===== NAVIGATION =====
function showPage(pageId) {
    const pages = ['home', 'mandi', 'crops', 'auctions', 'compare', 'aicompare', 'admin', 'login'];
    pages.forEach(p => {
        const el = document.getElementById('page-' + p);
        if (el) el.style.display = (p === pageId) ? 'block' : 'none';
    });
}

// ===== MANDI PRICES =====
function loadMandiData() {
    const tbody = document.getElementById('mandiBody');
    if (!tbody) return;
    renderMandiTable(mandis);
}

function renderMandiTable(data) {
    const tbody = document.getElementById('mandiBody');
    if (!tbody) return;
    
    tbody.innerHTML = data.map(m => {
        const icon = m.trend === 'up' ? '<i class="bi bi-arrow-up-right text-danger"></i>' :
                    m.trend === 'down' ? '<i class="bi bi-arrow-down-right text-success"></i>' :
                    '<i class="bi bi-dash text-secondary"></i>';
        return `<tr>
            <td>${m.crop}</td>
            <td>${m.mandi}</td>
            <td>₹${m.min}</td>
            <td>₹${m.max}</td>
            <td><strong>₹${m.modal}</strong></td>
            <td>${icon}</td>
            <td>${m.dist} km</td>
        </tr>`;
    }).join('');
}

function filterMandi() {
    const q = document.getElementById('mandiSearch').value.toLowerCase();
    const filtered = mandis.filter(m => 
        m.crop.toLowerCase().includes(q) || 
        m.mandi.toLowerCase().includes(q)
    );
    renderMandiTable(filtered);
}

function findNearby() {
    const msg = document.getElementById('nearbyMsg');
    msg.style.display = 'block';
    msg.innerHTML = '<i class="bi bi-geo-alt-fill"></i> Nearest mandis: <strong>Azadpur (2.3 km)</strong>, <strong>Ghazipur (5.1 km)</strong>, <strong>Keshopur (8.4 km)</strong>. <em>(Google Maps API in production)</em>';
}

// ===== CROPS =====
function loadCrops() {
    renderCrops();
}

function renderCrops() {
    const list = document.getElementById('cropList');
    if (!list) return;
    
    list.innerHTML = crops.map(c => `
        <div class="col-md-6">
            <div class="card crop-card">
                <div class="crop-emoji">${c.img}</div>
                <div class="crop-info">
                    <div class="fw-bold">${c.name} <span class="crop-grade">${c.grade} Grade</span></div>
                    <div class="small text-muted">${c.qty} quintals · ₹${c.price}/q</div>
                    <div class="small">Seller: ${c.seller} ⭐${c.rating}</div>
                    <div class="mt-2 d-flex gap-2">
                        <button class="btn btn-sm btn-mandi" onclick="contactSeller('${c.seller}')">
                            <i class="bi bi-chat"></i> Contact
                        </button>
                        <button class="btn btn-sm btn-outline-mandi" onclick="placeOrder('${c.name}')">Buy</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function addCrop(event) {
    event.preventDefault();
    const name = document.getElementById('cropName').value;
    const qty = document.getElementById('cropQty').value;
    const grade = document.getElementById('cropGrade').value;
    const price = document.getElementById('cropPrice').value;
    
    if (!name || !qty || !price) {
        alert('Please fill all required fields');
        return false;
    }
    
    crops.push({
        id: nextCropId++,
        name: name,
        qty: parseFloat(qty),
        grade: grade,
        price: parseFloat(price),
        img: '🌿',
        seller: 'You',
        rating: 5.0
    });
    
    renderCrops();
    document.getElementById('cropForm').reset();
    alert('✅ Crop listed successfully!');
    return false;
}

function contactSeller(seller) {
    toggleChat();
    setTimeout(() => {
        addChatMessage('bot', `Connecting you to ${seller}... 📞 Call: +91 98XXXXXX21 | 💬 Chat available.`);
    }, 400);
}

function placeOrder(cropName) {
    alert(`✅ Order placed for ${cropName}! The farmer will be notified.`);
}

// ===== AUCTIONS =====
function loadAuctions() {
    renderAuctions();
}

function createAuction(event) {
    event.preventDefault();
    const crop = document.getElementById('aucCrop').value;
    const qty = document.getElementById('aucQty').value;
    const base = document.getElementById('aucBase').value;
    const dur = document.getElementById('aucDur').value;
    
    if (!crop || !qty || !base || !dur) {
        alert('Fill all auction fields');
        return false;
    }
    
    const id = nextAuctionId++;
    const endTime = Date.now() + (parseInt(dur) * 60000);
    
    auctions.push({
        id: id,
        crop: crop,
        qty: parseFloat(qty),
        base: parseFloat(base),
        current: parseFloat(base),
        ends: endTime,
        bids: 0,
        winner: null,
        status: 'live'
    });
    
    startBidTimer(id);
    renderAuctions();
    document.getElementById('auctionForm').reset();
    alert('🎉 Auction started! Buyers can now bid.');
    return false;
}

function startBidTimer(id) {
    bidTimers[id] = setInterval(() => {
        const a = auctions.find(x => x.id === id);
        if (!a) { clearInterval(bidTimers[id]); return; }
        
        if (Date.now() >= a.ends && a.status === 'live') {
            a.status = 'ended';
            clearInterval(bidTimers[id]);
            if (a.winner) {
                alert(`🏆 Auction #${id} ended! Winner: ${a.winner} @ ₹${a.current}/q`);
            }
        }
        renderAuctions();
    }, 1000);
}

function placeBid(id) {
    const a = auctions.find(x => x.id === id);
    if (!a || a.status !== 'live') {
        alert('Auction ended');
        return;
    }
    
    const increment = Math.round(a.current * 0.05);
    a.current += increment;
    a.bids++;
    a.winner = 'Buyer ' + Math.floor(Math.random() * 900 + 100);
    renderAuctions();
}

function renderAuctions() {
    const list = document.getElementById('auctionList');
    if (!list) return;
    
    list.innerHTML = auctions.map(a => {
        const left = Math.max(0, Math.ceil((a.ends - Date.now()) / 1000));
        const mm = String(Math.floor(left / 60)).padStart(2, '0');
        const ss = String(left % 60).padStart(2, '0');
        const statusBadge = a.status === 'live' 
            ? '<span class="auction-live">LIVE</span>' 
            : '<span class="auction-ended">ENDED</span>';
        
        return `<div class="col-md-6">
            <div class="card auction-card">
                <div class="d-flex justify-content-between">
                    <span class="fw-bold">${a.crop} (${a.qty} q)</span>
                    ${statusBadge}
                </div>
                <div class="small text-muted">Base ₹${a.base}/q · Current: <strong class="text-success">₹${a.current}/q</strong></div>
                <div class="small">Bids: ${a.bids} ${a.winner ? '· Winner: ' + a.winner : ''}</div>
                <div class="progress mt-2">
                    <div class="progress-bar" style="width:${a.status === 'live' ? 60 : 100}%"></div>
                </div>
                <div class="timer mb-2">⏱ ${mm}:${ss}</div>
                ${a.status === 'live' 
                    ? `<button class="btn btn-mandi btn-sm" onclick="placeBid(${a.id})">Place Bid (+5%)</button>`
                    : '<span class="text-muted small">Auction closed</span>'}
            </div>
        </div>`;
    }).join('');
}

// ===== PRODUCT COMPARISON =====
function populateCompare() {
    const selectA = document.getElementById('compA');
    const selectB = document.getElementById('compB');
    if (!selectA || !selectB) return;
    
    const options = crops.map(c => `<option value="${c.id}">${c.name} — ${c.seller}</option>`).join('');
    selectA.innerHTML = '<option>Select Product A</option>' + options;
    selectB.innerHTML = '<option>Select Product B</option>' + options;
    
    if (crops.length > 1) {
        selectB.selectedIndex = 2;
    }
    compareProducts();
}

/**
 * ============================================
 * AI VEGETABLE COMPARISON
 * Connects directly to Python Flask API
 * Running on http://localhost:5000
 * ============================================
 */

async function runAICompare() {
    const file1 = document.getElementById('file1');
    const file2 = document.getElementById('file2');
    const resultDiv = document.getElementById('aiResult');

    // Check both images
    if (!file1 || !file2 || !file1.files[0] || !file2.files[0]) {
        alert('Please upload BOTH vegetable images first.');
        return;
    }

    // Validate image types
    const allowedTypes = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/webp'
    ];

    if (!allowedTypes.includes(file1.files[0].type)) {
        alert('Vegetable 1 must be JPG, PNG or WEBP.');
        return;
    }

    if (!allowedTypes.includes(file2.files[0].type)) {
        alert('Vegetable 2 must be JPG, PNG or WEBP.');
        return;
    }

    // Maximum 5 MB
    if (file1.files[0].size > 5 * 1024 * 1024) {
        alert('Vegetable 1 image must be smaller than 5MB.');
        return;
    }

    if (file2.files[0].size > 5 * 1024 * 1024) {
        alert('Vegetable 2 image must be smaller than 5MB.');
        return;
    }

    // Loading screen
    resultDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-success"
                 style="width:3rem;height:3rem;">
            </div>

            <p class="mt-3">
                <strong>AI is comparing the vegetables...</strong>
            </p>

            <p class="small text-muted">
                Connecting to AI server on port 5000
            </p>
        </div>
    `;

    // Create FormData
    const formData = new FormData();

    formData.append('image1', file1.files[0]);
    formData.append('image2', file2.files[0]);

    try {

        /*
         * ============================================
         * PYTHON FLASK API
         * ============================================
         *
         * Python server:
         * http://localhost:5000
         *
         * API endpoint:
         * POST /compare
         */

        const response = await fetch(
            'http://localhost:5000/compare',
            {
                method: 'POST',
                body: formData
            }
        );

        // Check HTTP status
        if (!response.ok) {
            throw new Error(
                `AI server returned HTTP ${response.status}`
            );
        }

        const data = await response.json();

        console.log('AI API Response:', data);

        if (data.success) {

            // Display dynamic AI results
            displayAIResults(data.data);

        } else {

            resultDiv.innerHTML = `
                <div class="alert alert-danger">

                    <i class="bi bi-exclamation-triangle"></i>

                    <strong>AI Comparison Failed</strong>

                    <br>

                    ${data.message || 'Unable to analyze images.'}

                </div>
            `;
        }

    } catch (error) {

        console.error('AI Connection Error:', error);

        resultDiv.innerHTML = `
            <div class="alert alert-danger">

                <i class="bi bi-wifi-off"></i>

                <strong>Cannot connect to AI server</strong>

                <p class="mb-1 mt-2">
                    Make sure your Python API is running on:
                </p>

                <code>
                    http://localhost:5000
                </code>

                <hr>

                <strong>Possible reasons:</strong>

                <ul class="mb-0">
                    <li>Python server is not running</li>
                    <li>Port 5000 is incorrect</li>
                    <li>API endpoint is incorrect</li>
                    <li>CORS is not enabled</li>
                    <li>Flask server crashed</li>
                </ul>

                <small class="text-muted">
                    Error: ${error.message}
                </small>

            </div>
        `;
    }
}

// ===== AI COMPARE =====
function loadImage(fileId, imgId, dzId) {
    const file = document.getElementById(fileId).files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = document.getElementById(imgId);
        const dz = document.getElementById(dzId);
        img.src = e.target.result;
        img.style.display = 'block';
        dz.querySelector('.upload-icon').style.display = 'none';
        dz.querySelector('div:not(:has(img))').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function runAICompare() {
    const img1 = document.getElementById('img1');
    const img2 = document.getElementById('img2');
    const result = document.getElementById('aiResult');
    
    if (!img1.src || !img2.src || img1.style.display === 'none' || img2.style.display === 'none') {
        alert('Please upload BOTH vegetable images first.');
        return;
    }
    
    result.innerHTML = '<div class="text-center"><div class="spinner-border text-success"></div><p class="mt-2">Analyzing with CNN + OpenCV...</p></div>';
    
    setTimeout(() => {
        const scores = [
            {name:'Vegetable 1', fresh:94, grade:'A', defects:'None', score:92},
            {name:'Vegetable 2', fresh:79, grade:'B', defects:'Minor spots', score:74}
        ];
        const winner = scores[0];
        
        result.innerHTML = `
            <div class="row g-3">
                ${scores.map(s => `
                <div class="col-md-6">
                    <div class="result-card">
                        <div class="fw-bold mb-2">${s.name}</div>
                        <div class="d-flex justify-content-between"><span>Freshness</span><strong>${s.fresh}%</strong></div>
                        <div class="progress"><div class="progress-bar" style="width:${s.fresh}%"></div></div>
                        <div class="d-flex justify-content-between"><span>Grade</span><span class="badge bg-${s.grade==='A'?'success':'warning'}">${s.grade}</span></div>
                        <div class="d-flex justify-content-between"><span>Defects</span><span>${s.defects}</span></div>
                        <div class="d-flex justify-content-between mt-2"><span>Score</span><strong class="text-success">${s.score}/100</strong></div>
                    </div>
                </div>`).join('')}
            </div>
            <div class="alert alert-success mt-3">
                <i class="bi bi-trophy-fill"></i> <strong>AI Recommendation:</strong> 
                ${winner.name} is recommended — higher freshness (${winner.fresh}%), better color, no defects.
            </div>
        `;
    }, 1500);
}

// ===== LOGIN / REGISTER =====
function showTab(tab, el) {
    document.querySelectorAll('.nav-pills-mandi .nav-link').forEach(x => x.classList.remove('active'));
    if (el) el.classList.add('active');
    
    document.getElementById('loginTab').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('registerTab').style.display = tab === 'register' ? 'block' : 'none';
}

function doLogin(event) {
    event.preventDefault();
    const form = document.getElementById('loginForm');
    const formData = new FormData(form);
    
    fetch('../backend/login.php', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('✅ Login successful!');
            window.location.href = 'index.html';
        } else {
            alert('❌ ' + data.message);
        }
    })
    .catch(err => {
        // Demo mode - no backend
        alert('🔐 Demo Login: Welcome back!');
        window.location.href = 'index.html';
    });
    return false;
}

function doRegister(event) {
    event.preventDefault();
    const form = document.getElementById('registerForm');
    const formData = new FormData(form);
    
    fetch('../backend/register.php', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('✅ Account created! Please login.');
            showTab('login', null);
        } else {
            alert('❌ ' + data.message);
        }
    })
    .catch(err => {
        alert('📝 Demo Register: Account created!');
        showTab('login', null);
    });
    return false;
}

function logout() {
    fetch('../backend/logout.php')
    .then(() => {
        alert('👋 Logged out successfully');
        window.location.href = 'index.html';
    })
    .catch(() => {
        window.location.href = 'index.html';
    });
}

// ===== ADMIN =====
function loadAdminData() {
    updateAdminStats();
    adminTab('users', document.querySelector('.nav-pills-mandi .nav-link'));
}

function updateAdminStats() {
    const usersEl = document.getElementById('adUsers');
    const cropsEl = document.getElementById('adCrops');
    const auctionsEl = document.getElementById('adAuctions');
    const valueEl = document.getElementById('adValue');
    
    if (usersEl) usersEl.textContent = (1200 + crops.length * 7).toLocaleString();
    if (cropsEl) cropsEl.textContent = crops.length;
    if (auctionsEl) auctionsEl.textContent = auctions.length;
    if (valueEl) valueEl.textContent = '₹' + (21000000 + crops.reduce((s, c) => s + c.price * c.qty, 0)).toLocaleString('en-IN');
}

function adminTab(tab, el) {
    document.querySelectorAll('.nav-pills-mandi .nav-link').forEach(x => x.classList.remove('active'));
    if (el) el.classList.add('active');
    renderAdminTable(tab);
}

function renderAdminTable(tab) {
    const container = document.getElementById('adminTable');
    if (!container) return;
    
    if (tab === 'users') {
        container.innerHTML = `
            <table class="table table-striped">
                <thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Status</th><th>Action</th></tr></thead>
                <tbody>
                    <tr><td>1</td><td>Ramesh Kumar</td><td>Farmer</td><td><span class="badge bg-success">Active</span></td><td><button class="btn btn-sm btn-outline-danger">Suspend</button></td></tr>
                    <tr><td>2</td><td>Sunita Devi</td><td>Farmer</td><td><span class="badge bg-success">Active</span></td><td><button class="btn btn-sm btn-outline-danger">Suspend</button></td></tr>
                    <tr><td>3</td><td>Gurpreet Singh</td><td>Farmer</td><td><span class="badge bg-warning">Pending</span></td><td><button class="btn btn-sm btn-outline-success">Verify</button></td></tr>
                </tbody>
            </table>`;
    } else if (tab === 'crops') {
        container.innerHTML = `
            <table class="table table-striped">
                <thead><tr><th>Crop</th><th>Qty</th><th>Grade</th><th>Price</th><th>Status</th></tr></thead>
                <tbody>
                    ${crops.map(c => `<tr><td>${c.name}</td><td>${c.qty} q</td><td>${c.grade}</td><td>₹${c.price}</td><td><span class="badge bg-success">Listed</span></td></tr>`).join('')}
                </tbody>
            </table>`;
    } else {
        container.innerHTML = `
            <table class="table table-striped">
                <thead><tr><th>ID</th><th>Type</th><th>Amount</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>
                    <tr><td>TX-1001</td><td>Tomato Sale</td><td>₹75,000</td><td><span class="badge bg-success">Completed</span></td><td>2026-09-02</td></tr>
                    <tr><td>TX-1002</td><td>Onion Sale</td><td>₹2,70,000</td><td><span class="badge bg-success">Completed</span></td><td>2026-09-01</td></tr>
                </tbody>
            </table>`;
    }
}

// ===== CHATBOT =====
function toggleChat() {
    const box = document.getElementById('chatBox');
    if (box) box.classList.toggle('open');
}

function addChatMessage(who, text) {
    const body = document.getElementById('chatBody');
    if (!body) return;
    body.innerHTML += `<div class="msg ${who}">${text}</div>`;
    body.scrollTop = body.scrollHeight;
}

function getBotReply(q) {
    q = q.toLowerCase();
    if (q.includes('price') || q.includes('rate') || q.includes('mandi'))
        return '📊 Today\'s Tomato at Azadpur: <strong>₹1,500/q</strong>. Onion: ₹2,350/q. Check <a href="mandi.html">Mandi Prices</a>!';
    if (q.includes('auction'))
        return '🔨 Visit <a href="auctions.html">Auctions</a>. Farmers create, buyers bid +5%, highest wins!';
    if (q.includes('crop') || q.includes('list'))
        return '🌾 Go to <a href="crops.html">Crops</a> to list produce with quantity, grade, and price.';
    if (q.includes('quality') || q.includes('compare'))
        return '🧪 Use <a href="aicompare.html">AI Compare</a> to upload vegetable images for quality scoring.';
    if (q.includes('tip') || q.includes('farm'))
        return '🌱 Tip: Store tomatoes at 12°C, 85% humidity. Grade before listing for better prices!';
    if (q.includes('hello') || q.includes('hi') || q.includes('namaste'))
        return '🙏 Namaste! Ask about prices, auctions, crops, or farming tips.';
    return '🤖 I can help with prices, auctions, crops, quality compare, and farming tips. Try "tomato price"!';
}

function sendChat() {
    const input = document.getElementById('chatInput');
    const q = input.value.trim();
    if (!q) return;
    
    addChatMessage('user', q);
    input.value = '';
    
    setTimeout(() => {
        addChatMessage('bot', getBotReply(q));
    }, 500);
}

// ===== DRAG & DROP =====
document.addEventListener('DOMContentLoaded', () => {
    ['dz1', 'dz2'].forEach(id => {
        const dz = document.getElementById(id);
        if (!dz) return;
        
        dz.addEventListener('dragover', (e) => {
            e.preventDefault();
            dz.classList.add('drag');
        });
        
        dz.addEventListener('dragleave', () => {
            dz.classList.remove('drag');
        });
        
        dz.addEventListener('drop', (e) => {
            e.preventDefault();
            dz.classList.remove('drag');
            // Handle file drop
        });
    });
});

// ===== INITIALIZE =====
console.log('🌾 MandiMart loaded successfully!');


// ============================================
// AI VEGETABLE COMPARISON - UPDATED FUNCTIONS
// Connects to PHP backend which proxies to Python API
// ============================================

/**
 * Load image preview when file is selected
 */
function loadImage(fileId, imgId, dzId) {
    const fileInput = document.getElementById(fileId);
    const img = document.getElementById(imgId);
    const dropZone = document.getElementById(dzId);
    
    if (!fileInput.files || fileInput.files.length === 0) return;
    
    const file = fileInput.files[0];
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a valid image (JPG, PNG, GIF, WEBP)');
        fileInput.value = '';
        return;
    }
    
    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        alert('Image must be less than 5MB');
        fileInput.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        img.src = e.target.result;
        img.style.display = 'block';
        
        // Hide upload icon and text
        const icon = dropZone.querySelector('.upload-icon');
        const text = dropZone.querySelector('div:not(:has(img))');
        if (icon) icon.style.display = 'none';
        if (text && text !== dropZone) text.style.display = 'none';
        
        dropZone.classList.add('has-image');
    };
    reader.readAsDataURL(file);
}

/**
 * Run AI Comparison - Send to PHP backend
 */
async function runAICompare() {
    const file1 = document.getElementById('file1');
    const file2 = document.getElementById('file2');
    const img1 = document.getElementById('img1');
    const img2 = document.getElementById('img2');
    const resultDiv = document.getElementById('aiResult');
    
    // Validate both images present
    if (!file1.files[0] || !file2.files[0]) {
        alert('Please upload BOTH vegetable images first.');
        return;
    }
    
    // Show loading state
    resultDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
            <p class="mt-3 text-muted">Analyzing images with AI...</p>
            <p class="small text-muted">This may take 5-15 seconds</p>
        </div>
    `;
    
    // Build form data
    const formData = new FormData();
    formData.append('image1', file1.files[0]);
    formData.append('image2', file2.files[0]);
    
    try {
        // Send to PHP backend (which forwards to Python API)
        const response = await fetch('../backend/ai_compare.php', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAIResults(data.data);
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> 
                    ${data.message || 'Analysis failed. Please try again.'}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('AI Compare Error:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-wifi-off"></i> 
                <strong>Connection Error</strong><br>
                Could not connect to AI service. Please ensure the Python API is running on port 5000.
                <br><small>Error: ${error.message}</small>
            </div>
        `;
    }
}

/**
 * Display AI Comparison Results
 */
function displayAIResults(data) {
    const resultDiv = document.getElementById('aiResult');
    
    const veg1 = data.vegetable_1;
    const veg2 = data.vegetable_2;
    const winner = data.winner;
    const winnerName = data.winner_name;
    const margin = data.margin;
    
    // Determine winner styling
    const veg1Class = winner === 1 ? 'winner-card' : '';
    const veg2Class = winner === 2 ? 'winner-card' : '';
    const veg1Badge = winner === 1 ? '<span class="winner-badge"><i class="bi bi-trophy"></i> WINNER</span>' : '';
    const veg2Badge = winner === 2 ? '<span class="winner-badge"><i class="bi bi-trophy"></i> WINNER</span>' : '';
    
    // Grade color mapping
    const gradeColor = (grade) => {
        const colors = {
            'A+': '#28a745', 'A': '#20c997', 'B': '#6c757d',
            'C': '#fd7e14', 'D': '#ffc107', 'F': '#dc3545'
        };
        return colors[grade] || '#6c757d';
    };
    
    resultDiv.innerHTML = `
        <div class="comparison-results">
            
            <!-- Result Header -->
            <div class="result-header mb-4">
                <h4><i class="bi bi-cpu"></i> AI Analysis Complete</h4>
                <div class="winner-announcement" style="background: linear-gradient(90deg, #145a24, #2e9e4f); color: white; padding: 1rem; border-radius: 12px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 800;">
                        <i class="bi bi-trophy-fill"></i> ${winnerName} Wins!
                    </div>
                    <div style="opacity: 0.9; margin-top: 0.5rem;">
                        By ${margin}% quality margin
                    </div>
                </div>
            </div>
            
            <!-- Side by Side Comparison -->
            <div class="row g-4">
                
                <!-- Vegetable 1 -->
                <div class="col-md-6">
                    <div class="result-card ${veg1Class}" style="position: relative;">
                        ${veg1Badge}
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0">Vegetable 1</h5>
                            <span class="grade-badge" style="background: ${gradeColor(veg1.quality_grade)}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 700;">
                                Grade ${veg1.quality_grade}
                            </span>
                        </div>
                        
                        <div class="score-big" style="font-size: 3rem; font-weight: 800; color: var(--green); text-align: center; margin: 1rem 0;">
                            ${veg1.overall_score}<small style="font-size: 1rem; color: #6b7a66;">/100</small>
                        </div>
                        
                        <div class="score-breakdown">
                            ${renderScoreBar('Freshness', veg1.freshness_score, '#28a745')}
                            ${renderScoreBar('Color', veg1.color_score, '#17a2b8')}
                            ${renderScoreBar('Texture', veg1.texture_score, '#6f42c1')}
                            ${renderScoreBar('No Defects', veg1.defect_score, '#fd7e14')}
                            ${renderScoreBar('Size/Shape', veg1.size_score, '#20c997')}
                        </div>
                        
                        <div class="mt-3 small text-muted">
                            <i class="bi bi-clock-history"></i> Est. shelf life: ${veg1.estimated_shelf_life_days || '~'} days
                        </div>
                    </div>
                </div>
                
                <!-- Vegetable 2 -->
                <div class="col-md-6">
                    <div class="result-card ${veg2Class}" style="position: relative;">
                        ${veg2Badge}
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0">Vegetable 2</h5>
                            <span class="grade-badge" style="background: ${gradeColor(veg2.quality_grade)}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 700;">
                                Grade ${veg2.quality_grade}
                            </span>
                        </div>
                        
                        <div class="score-big" style="font-size: 3rem; font-weight: 800; color: var(--green); text-align: center; margin: 1rem 0;">
                            ${veg2.overall_score}<small style="font-size: 1rem; color: #6b7a66;">/100</small>
                        </div>
                        
                        <div class="score-breakdown">
                            ${renderScoreBar('Freshness', veg2.freshness_score, '#28a745')}
                            ${renderScoreBar('Color', veg2.color_score, '#17a2b8')}
                            ${renderScoreBar('Texture', veg2.texture_score, '#6f42c1')}
                            ${renderScoreBar('No Defects', veg2.defect_score, '#fd7e14')}
                            ${renderScoreBar('Size/Shape', veg2.size_score, '#20c997')}
                        </div>
                        
                        <div class="mt-3 small text-muted">
                            <i class="bi bi-clock-history"></i> Est. shelf life: ${veg2.estimated_shelf_life_days || '~'} days
                        </div>
                    </div>
                </div>
                
            </div>
            
            <!-- Recommendation -->
            <div class="alert alert-success mt-4" style="border: none; background: linear-gradient(90deg, #d4edda, #c3e6cb);">
                <i class="bi bi-lightbulb-fill" style="color: #155724;"></i>
                <strong style="color: #155724;">AI Recommendation:</strong>
                <p class="mb-0 mt-2" style="color: #155724;">${data.recommendation}</p>
                <p class="mb-0 small" style="color: #155724; opacity: 0.8;">
                    <i class="bi bi-cash-coin"></i> ${data.market_value}
                </p>
            </div>
            
            <!-- Comparison Details -->
            ${data.summary ? renderComparisonDetails(data.summary) : ''}
            
            ${data.note ? `
            <div class="alert alert-warning mt-3">
                <i class="bi bi-info-circle"></i> ${data.note}
            </div>
            ` : ''}
            
        </div>
    `;
}

/**
 * Render a score progress bar
 */
function renderScoreBar(label, score, color) {
    const percentage = Math.min(100, Math.max(0, score));
    return `
        <div class="score-row mb-2">
            <div class="d-flex justify-content-between small mb-1">
                <span>${label}</span>
                <span style="font-weight: 600;">${score}%</span>
            </div>
            <div class="progress" style="height: 8px; border-radius: 4px;">
                <div class="progress-bar" style="width: ${percentage}%; background: ${color};"></div>
            </div>
        </div>
    `;
}

/**
 * Render detailed comparison summary
 */
function renderComparisonDetails(summary) {
    if (!summary.key_differences || summary.key_differences.length === 0) return '';
    
    return `
        <div class="card mt-3 p-3">
            <h6><i class="bi bi-list-check"></i> Detailed Comparison</h6>
            <ul class="list-unstyled mb-0">
                ${summary.key_differences.map(diff => `
                    <li><i class="bi bi-check-circle text-success"></i> ${diff}</li>
                `).join('')}
            </ul>
            <div class="mt-2 p-2" style="background: #f8f9fa; border-radius: 8px;">
                <small><strong>Buyer Advice:</strong> ${summary.buyer_advice}</small>
            </div>
        </div>
    `;
}

/**
 * Reset comparison form
 */
function resetComparison() {
    document.getElementById('file1').value = '';
    document.getElementById('file2').value = '';
    document.getElementById('img1').style.display = 'none';
    document.getElementById('img2').style.display = 'none';
    document.getElementById('aiResult').innerHTML = '';
    
    // Reset drop zones
    ['dz1', 'dz2'].forEach(id => {
        const dz = document.getElementById(id);
        if (dz) {
            dz.classList.remove('has-image');
            const icon = dz.querySelector('.upload-icon');
            const text = dz.querySelector('div:not(:has(img))');
            if (icon) icon.style.display = 'block';
            if (text) text.style.display = 'block';
        }
    });
}

// ===============================
// MANDIMART AI COMPARISON API
// ===============================

// LOCAL TESTING
const API_BASE_URL =
    "https://mandimart-ai.onrender.com";

// AFTER DEPLOYING PYTHON BACKEND:
// const API_BASE_URL = "https://your-backend-url.onrender.com";


function loadImage(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    if (!input || !preview) return;

    const file = input.files[0];

    if (!file) {
        preview.style.display = "none";
        preview.src = "";
        return;
    }

    if (!file.type.startsWith("image/")) {
        alert("Please select a valid image.");
        input.value = "";
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert("Image must be smaller than 5 MB.");
        input.value = "";
        return;
    }

    const reader = new FileReader();

    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
    };

    reader.readAsDataURL(file);
}


async function runAICompare() {

    const file1Input = document.getElementById("file1");
    const file2Input = document.getElementById("file2");
    const resultBox = document.getElementById("aiResult");

    if (!file1Input || !file2Input || !resultBox) {
        console.error("AI comparison elements not found.");
        return;
    }

    const file1 = file1Input.files[0];
    const file2 = file2Input.files[0];

    // Check images
    if (!file1 || !file2) {
        alert("Please upload both vegetable images.");
        return;
    }

    if (!file1.type.startsWith("image/") ||
        !file2.type.startsWith("image/")) {

        alert("Both files must be images.");
        return;
    }

    // 5 MB limit
    if (file1.size > 5 * 1024 * 1024 ||
        file2.size > 5 * 1024 * 1024) {

        alert("Each image must be smaller than 5 MB.");
        return;
    }

    // Loading message
    resultBox.innerHTML = `
        <div class="ai-loading">
            <h3>🤖 AI is analyzing the vegetables...</h3>
            <p>Please wait while MandiMart compares freshness, color, texture and defects.</p>
        </div>
    `;

    try {

        const formData = new FormData();

        formData.append("image1", file1);
        formData.append("image2", file2);

        console.log("Sending images to:", API_BASE_URL + "/compare");

        const response = await fetch(
            `${API_BASE_URL}/compare`,
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const result = await response.json();

        console.log("AI API response:", result);

        if (!result.success) {
            throw new Error(
                result.message || "AI comparison failed."
            );
        }

        // Display AI results
        displayAIResults(result.data);

    } catch (error) {

        console.error("AI Comparison Error:", error);

        resultBox.innerHTML = `
            <div class="ai-error">
                <h3>❌ AI comparison failed</h3>

                <p>
                    Could not connect to the MandiMart AI server.
                </p>

                <p>
                    Make sure your Python backend is running on:
                </p>

                <code>${API_BASE_URL}</code>

                <br><br>

                <button onclick="runAICompare()">
                    🔄 Try Again
                </button>
            </div>
        `;
    }
}

// Add CSS for winner styling
const winnerStyles = document.createElement('style');
winnerStyles.textContent = `
    .winner-card {
        border: 3px solid #f5a623 !important;
        box-shadow: 0 0 20px rgba(245, 166, 35, 0.3) !important;
    }
    .winner-badge {
        position: absolute;
        top: -10px;
        right: 10px;
        background: linear-gradient(90deg, #f5a623, #ff8c00);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        box-shadow: 0 4px 12px rgba(245, 166, 35, 0.4);
    }
`;
document.head.appendChild(winnerStyles);
