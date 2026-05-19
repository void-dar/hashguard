HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HashGuard — File Integrity Monitor</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:      #060a0f;
    --surface: #0d1520;
    --surface2:#111d2b;
    --border:  #1a2a3a;
    --accent:  #00e5ff;
    --accent2: #ff3d71;
    --warn:    #ffaa00;
    --ok:      #00e096;
    --purple:  #bb88ff;
    --text:    #c8d8e8;
    --muted:   #4a6070;
    --mono:    'Space Mono', monospace;
    --sans:    'Syne', sans-serif;
  }
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* subtle grid background */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .wrap { position: relative; z-index: 1; max-width: 1000px; margin: 0 auto; padding: 40px 24px 80px; }

  /* ── Header ── */
  header {
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 40px;
  }
  .logo {
    width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #005f77 0%, #003344 100%);
    border: 1px solid rgba(0,229,255,.25);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 24px rgba(0,229,255,.15);
  }
  .logo-text h1 { font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
  .logo-text p  { font-family: var(--mono); font-size: 0.7rem; color: var(--muted); margin-top: 2px; }
  .ai-badge {
    margin-left: auto;
    font-family: var(--mono); font-size: 0.6rem; letter-spacing: 2px;
    padding: 5px 12px; border-radius: 4px;
    background: rgba(0,229,255,.06);
    border: 1px solid rgba(0,229,255,.18);
    color: var(--accent);
  }

  /* ── Grid ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
  @media (max-width: 660px) { .grid-2 { grid-template-columns: 1fr; } }

  /* ── Cards ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px;
    transition: border-color .25s;
  }
  .card:hover { border-color: rgba(0,229,255,.12); }

  .card-label {
    font-family: var(--mono); font-size: 0.65rem;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
  }
  .card-label.purple { color: var(--purple); }
  .card-label::before {
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
    flex-shrink: 0;
  }

  /* ── Drop zone ── */
  .drop {
    border: 2px dashed var(--border);
    border-radius: 10px;
    padding: 28px 16px;
    text-align: center;
    cursor: pointer;
    position: relative;
    transition: all .2s;
    background: var(--bg);
  }
  .drop:hover, .drop.over { border-color: var(--accent); background: rgba(0,229,255,.03); }
  .drop.purple-drop:hover, .drop.purple-drop.over { border-color: var(--purple); background: rgba(187,136,255,.03); }
  .drop input[type=file] { position: absolute; inset: 0; opacity: 0; width: 100%; cursor: pointer; }
  .drop .drop-icon { font-size: 26px; margin-bottom: 8px; }
  .drop .drop-hint { font-family: var(--mono); font-size: 0.75rem; color: var(--muted); }
  .drop .drop-name { font-family: var(--mono); font-size: 0.8rem; color: var(--accent); margin-top: 6px; min-height: 1.2em; }
  .drop.purple-drop .drop-name { color: var(--purple); }

  /* ── Inputs ── */
  .field { margin-top: 12px; }
  .field input[type=text] {
    width: 100%;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 7px; color: var(--text);
    font-family: var(--mono); font-size: 0.78rem;
    padding: 9px 12px; outline: none;
    transition: border-color .2s;
  }
  .field input[type=text]:focus { border-color: rgba(0,229,255,.4); }
  .field input[type=text]::placeholder { color: var(--muted); }

  /* ── Buttons ── */
  .btn {
    display: block; width: 100%; margin-top: 14px;
    padding: 11px; border-radius: 8px; border: none;
    font-family: var(--mono); font-size: 0.78rem; font-weight: 700;
    letter-spacing: 1.5px; cursor: pointer; transition: all .15s;
  }
  .btn:disabled { opacity: .35; cursor: not-allowed; }
  .btn-teal {
    background: linear-gradient(135deg, #004f60 0%, #007080 100%);
    color: var(--accent);
    border: 1px solid rgba(0,229,255,.25);
  }
  .btn-teal:not(:disabled):hover { filter: brightness(1.15); }
  .btn-purple {
    background: linear-gradient(135deg, #2a1040 0%, #4a1a70 100%);
    color: var(--purple);
    border: 1px solid rgba(187,136,255,.25);
  }
  .btn-purple:not(:disabled):hover { filter: brightness(1.15); }

  /* ── Result boxes ── */
  .result {
    display: none; margin-top: 14px;
    border-radius: 9px; padding: 14px 16px;
    font-family: var(--mono); font-size: 0.76rem; line-height: 1.8;
    border: 1px solid;
    animation: pop .25s ease;
  }
  .result.show { display: block; }

  .r-clean            { background: rgba(0,224,150,.07);  border-color: rgba(0,224,150,.3);  color: #55ffcc; }
  .r-registered       { background: rgba(0,229,255,.07);  border-color: rgba(0,229,255,.3);  color: var(--accent); }
  .r-already          { background: rgba(255,170,0,.07);  border-color: rgba(255,170,0,.3);  color: var(--warn); }
  .r-altered          { background: rgba(255,170,0,.07);  border-color: rgba(255,170,0,.3);  color: var(--warn); }
  .r-anomaly          { background: rgba(255,61,113,.07); border-color: rgba(255,61,113,.3); color: var(--accent2); }
  .r-unknown          { background: rgba(74,96,112,.08);  border-color: var(--border);        color: var(--muted); }

  .verdict { font-size: 0.95rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 8px; }
  .kv { display: flex; gap: 8px; }
  .kv .k { color: var(--muted); min-width: 100px; }
  .ebar-wrap { margin-top: 4px; }
  .ebar-label { font-size: 0.7rem; color: var(--muted); margin-bottom: 3px; }
  .ebar-bg { background: var(--border); border-radius: 3px; height: 4px; overflow: hidden; }
  .ebar    { height: 4px; border-radius: 3px; background: linear-gradient(90deg, var(--accent), #0066cc); transition: width .5s; }

  /* ── Registry table ── */
  .registry-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
  }
  .count-badge {
    font-family: var(--mono); font-size: 0.65rem;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.15);
    color: var(--accent); padding: 3px 9px; border-radius: 4px;
  }
  .refresh-btn {
    margin-left: auto;
    background: transparent; border: 1px solid var(--border);
    color: var(--muted); font-family: var(--mono); font-size: 0.7rem;
    padding: 4px 10px; border-radius: 5px; cursor: pointer; transition: all .2s;
  }
  .refresh-btn:hover { border-color: var(--accent); color: var(--accent); }

  .file-row {
    display: flex; align-items: center; gap: 10px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px;
    transition: border-color .2s;
    animation: pop .2s ease;
  }
  .file-row:hover { border-color: rgba(0,229,255,.12); }
  .fr-name { font-size: 0.85rem; color: #e0eeff; font-weight: 600; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .fr-hash { font-family: var(--mono); font-size: 0.68rem; color: var(--muted); }
  .fr-meta { font-family: var(--mono); font-size: 0.68rem; color: var(--muted); display: flex; flex-direction: column; align-items: flex-end; gap: 2px; flex-shrink: 0; }
  .tag-pill {
    font-family: var(--mono); font-size: 0.62rem;
    padding: 2px 8px; border-radius: 4px; flex-shrink: 0;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.18);
    color: var(--accent);
  }
  .del {
    background: transparent; border: 1px solid rgba(255,61,113,.2);
    color: var(--accent2); font-family: var(--mono); font-size: 0.65rem;
    padding: 4px 9px; border-radius: 5px; cursor: pointer; flex-shrink: 0;
    transition: all .15s; letter-spacing: 0;
  }
  .del:hover { background: rgba(255,61,113,.1); }
  .file-rows { display: flex; flex-direction: column; gap: 7px; }
  .empty-state { text-align: center; padding: 36px; font-family: var(--mono); font-size: 0.78rem; color: var(--muted); }

  .ai-note {
    margin-top: 12px; padding: 10px 14px;
    background: rgba(187,136,255,.05); border: 1px solid rgba(187,136,255,.15);
    border-radius: 7px; font-family: var(--mono); font-size: 0.7rem; color: #9966cc;
    display: flex; gap: 8px; align-items: flex-start;
  }

  @keyframes pop { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="logo">🔐</div>
    <div class="logo-text">
      <h1>HashGuard</h1>
      <p>sha-256 · isolation forest · file integrity</p>
    </div>
    <div class="ai-badge">AI-ENHANCED</div>
  </header>

  <div class="grid-2">

    <!-- ── Register ── -->
    <div class="card">
      <div class="card-label">01 / Register File</div>

      <div class="drop" id="regDrop">
        <input type="file" id="regFile" onchange="onRegPick()">
        <div class="drop-icon">📁</div>
        <div class="drop-hint">drop file or click to select</div>
        <div class="drop-name" id="regName"></div>
      </div>

      <div class="field">
        <input type="text" id="regTag" placeholder="tag  (optional) — e.g. original, v1, pre-deploy">
      </div>

      <button class="btn btn-teal" id="regBtn" onclick="doRegister()" disabled>REGISTER FILE</button>
      <div class="result" id="regResult"></div>
    </div>

    <!-- ── Verify ── -->
    <div class="card">
      <div class="card-label purple">02 / Verify File</div>

      <div class="drop purple-drop" id="verDrop">
        <input type="file" id="verFile" onchange="onVerPick()">
        <div class="drop-icon">🔍</div>
        <div class="drop-hint">drop file or click to select</div>
        <div class="drop-name" id="verName"></div>
      </div>

      <button class="btn btn-purple" id="verBtn" onclick="doVerify()" disabled style="margin-top:26px">VERIFY FILE</button>
      <div class="result" id="verResult"></div>

      <div class="ai-note">
        <span>⚡</span>
        <span>AI anomaly detection activates once ≥5 files are registered in the corpus.</span>
      </div>
    </div>

  </div>

  <!-- ── Registry ── -->
  <div class="card">
    <div class="registry-header">
      <div class="card-label" style="margin:0">03 / Registry</div>
      <span class="count-badge" id="countBadge">0 files</span>
      <button class="refresh-btn" onclick="loadFiles()">↻ refresh</button>
    </div>
    <div id="fileRows" class="file-rows">
      <div class="empty-state">loading registry…</div>
    </div>
  </div>

</div>

<script>
// ── file pick handlers ────────────────────────────────────────────────────────
function onRegPick() {
  const f = document.getElementById('regFile').files[0];
  document.getElementById('regName').textContent = f?.name ?? '';
  document.getElementById('regBtn').disabled = !f;
}
function onVerPick() {
  const f = document.getElementById('verFile').files[0];
  document.getElementById('verName').textContent = f?.name ?? '';
  document.getElementById('verBtn').disabled = !f;
}

// drag styling
['regDrop','verDrop'].forEach(id => {
  const el = document.getElementById(id);
  el.addEventListener('dragover', e => { e.preventDefault(); el.classList.add('over'); });
  el.addEventListener('dragleave', () => el.classList.remove('over'));
  el.addEventListener('drop',      () => el.classList.remove('over'));
});

// ── register ─────────────────────────────────────────────────────────────────
async function doRegister() {
  const file = document.getElementById('regFile').files[0];
  const tag  = document.getElementById('regTag').value.trim();
  if (!file) return;
  const btn = document.getElementById('regBtn');
  btn.disabled = true; btn.textContent = 'REGISTERING…';

  const fd = new FormData();
  fd.append('file', file);
  if (tag) fd.append('tag', tag);

  try {
    const r = await fetch('/register', { method: 'POST', body: fd });
    showRegResult(await r.json());
    loadFiles();
  } catch { showBox('regResult', 'unknown', '<div class="verdict">⚠ ERROR</div>Network error.'); }
  finally { btn.disabled = false; btn.textContent = 'REGISTER FILE'; }
}

function showRegResult(d) {
  const isNew = d.status === 'registered';
  const cls   = isNew ? 'registered' : 'already';
  const icon  = isNew ? '✅' : '⚠️';
  showBox('regResult', cls, `
    <div class="verdict">${icon} ${isNew ? 'REGISTERED' : 'ALREADY REGISTERED'}</div>
    <div class="kv"><span class="k">file</span><span>${d.filename}</span></div>
    <div class="kv"><span class="k">sha256</span><span>${d.sha256.slice(0,20)}…</span></div>
    <div class="kv"><span class="k">size</span><span>${fmtSize(d.file_size)}</span></div>
    <div class="kv"><span class="k">entropy</span><span>${d.entropy.toFixed(3)}</span></div>
    ${d.mime_guess ? `<div class="kv"><span class="k">mime</span><span>${d.mime_guess}</span></div>` : ''}
    ${d.tag ? `<div class="kv"><span class="k">tag</span><span>${d.tag}</span></div>` : ''}
    <div class="kv" style="margin-top:6px;opacity:.6"><span class="k">id</span><span>#${d.record_id}</span></div>
  `);
}

// ── verify ────────────────────────────────────────────────────────────────────
async function doVerify() {
  const file = document.getElementById('verFile').files[0];
  if (!file) return;
  const btn = document.getElementById('verBtn');
  btn.disabled = true; btn.textContent = 'VERIFYING…';

  const fd = new FormData();
  fd.append('file', file);

  try {
    const r = await fetch('/verify', { method: 'POST', body: fd });
    showVerResult(await r.json());
  } catch { showBox('verResult', 'unknown', '<div class="verdict">⚠ ERROR</div>Network error.'); }
  finally { btn.disabled = false; btn.textContent = 'VERIFY FILE'; }
}

function showVerResult(d) {
  const v = d.verdict;
  const icons = { CLEAN:'✅', ALTERED:'⚠️', ANOMALY:'🚨', UNKNOWN:'❓' };
  const cls   = v.toLowerCase();
  const pct   = Math.min(100, (d.entropy / 8) * 100).toFixed(1);

  showBox('verResult', cls, `
    <div class="verdict">${icons[v]??'❓'} ${v}</div>
    <div style="opacity:.75;margin-bottom:10px;font-size:.72rem;line-height:1.6">${d.message}</div>
    <div class="kv"><span class="k">sha256</span><span>${d.sha256.slice(0,20)}…</span></div>
    <div class="kv"><span class="k">size</span><span>${fmtSize(d.file_size)}</span></div>
    <div class="ebar-wrap">
      <div class="ebar-label">entropy  ${d.entropy.toFixed(3)} / 8.000</div>
      <div class="ebar-bg"><div class="ebar" style="width:${pct}%"></div></div>
    </div>
    ${d.anomaly_score != null ? `<div class="kv" style="margin-top:6px"><span class="k">AI score</span><span>${d.anomaly_score.toFixed(4)}</span></div>` : ''}
    ${d.matched_record ? `
      <div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.06)">
        <div class="kv"><span class="k">matched</span><span>${d.matched_record.filename}</span></div>
        <div class="kv"><span class="k">reg. at</span><span>${fmtDate(d.matched_record.registered_at)}</span></div>
        ${d.matched_record.tag ? `<div class="kv"><span class="k">tag</span><span>${d.matched_record.tag}</span></div>` : ''}
      </div>` : ''}
  `);
}

// ── registry ──────────────────────────────────────────────────────────────────
async function loadFiles() {
  try {
    const r = await fetch('/files');
    renderFiles(await r.json());
  } catch { /* silent */ }
}

function renderFiles(files) {
  const wrap = document.getElementById('fileRows');
  document.getElementById('countBadge').textContent = files.length + ' file' + (files.length !== 1 ? 's' : '');
  if (!files.length) {
    wrap.innerHTML = '<div class="empty-state">No files registered yet — upload one on the left.</div>';
    return;
  }
  wrap.innerHTML = files.map(f => `
    <div class="file-row">
      <div style="flex:1;min-width:0">
        <div class="fr-name">${f.filename}</div>
        <div class="fr-hash">${f.sha256_preview}</div>
      </div>
      <div class="fr-meta">
        <span>${fmtSize(f.file_size)}</span>
        <span>H=${f.entropy.toFixed(2)}</span>
        ${f.mime_guess ? `<span style="opacity:.6">${f.mime_guess.split('/')[1]??f.mime_guess}</span>` : ''}
      </div>
      ${f.tag ? `<span class="tag-pill">${f.tag}</span>` : ''}
      <button class="del" onclick="doDelete(${f.id})">✕</button>
    </div>
  `).join('');
}

async function doDelete(id) {
  await fetch('/files/' + id, { method: 'DELETE' });
  loadFiles();
}

// ── utils ─────────────────────────────────────────────────────────────────────
function showBox(id, cls, html) {
  const el = document.getElementById(id);
  el.className = 'result show r-' + cls;
  el.innerHTML = html;
}
function fmtSize(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  return (b/1048576).toFixed(2) + ' MB';
}
function fmtDate(iso) {
  return new Date(iso).toLocaleString();
}

loadFiles();
</script>
</body>
</html>
"""
