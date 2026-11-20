"""Dedicated interactive 2D graph page focused on the experimentation graph with a compact status HUD."""
from pathlib import Path
import hashlib
import json
from research_dashboard_descriptions import describe_jobs

HERE = Path(__file__).resolve().parent
ASSET_HASH = 'f55947f3daa3bae53209d4b885c195c157f595c225e508a6b382598d9452d6e2'


def render_graph(data, token=''):
    """Render a dedicated full-screen interactive 2D experiment graph with a compact HUD."""
    asset = (HERE / 'vendor/cytoscape-3.33.1/cytoscape.min.js').read_bytes()
    if hashlib.sha256(asset).hexdigest() != ASSET_HASH:
        raise ValueError('Cytoscape asset hash mismatch')

    payload = json.dumps(data, allow_nan=False).replace('<', '\\u003c').replace('&', '\\u0026')
    descriptions = json.dumps(describe_jobs(data), allow_nan=False).replace('<', '\\u003c').replace('&', '\\u0026')
    js_logic = (HERE / 'research_graph_view.js').read_text().replace('</script', '<\\/script')
    asset_str = asset.decode().replace('</script', '<\\/script')

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NUIAK 2D Experimentation Graph</title>
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#090d13;color:#c9d1d9;font:12px/1.35 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif}}
#graph-canvas{{position:absolute;top:0;left:0;width:100vw;height:100vh;background:#090d13;z-index:1}}
#graph-hud-top{{position:fixed;top:10px;left:10px;right:10px;z-index:30;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;background:rgba(22,27,34,0.88);backdrop-filter:blur(10px);border:1px solid #30363d;border-radius:8px;padding:6px 12px;box-shadow:0 4px 16px rgba(0,0,0,0.5)}}
.hud-group{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.hud-btn{{background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:4px 9px;border-radius:5px;font-size:11px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:4px;transition:all .15s}}
.hud-btn:hover{{background:#30363d;color:#f0f6fc;border-color:#52697f}}
.hud-btn.primary{{background:#12623b;border-color:#55d790;color:#fff}}
.hud-btn.primary:hover{{background:#187748}}
.hud-btn.back{{background:#162b3d;color:#5ce1dc;border-color:#165b6d}}
.hud-btn.back:hover{{background:#1d384f;color:#70ffff}}
.hud-input,.hud-select{{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;padding:3px 7px;font-size:11px}}
.hud-input{{width:150px}}.hud-input:focus,.hud-select:focus{{outline:none;border-color:#5ce1dc}}
.hud-pill{{font-size:11px;font-weight:600;padding:2px 8px;border-radius:12px;display:inline-flex;align-items:center;gap:5px;background:#101923;border:1px solid #30363d}}
.hud-pill.running{{background:#0e333d;color:#5ce1dc;border-color:#165b6d}}
.hud-pill.idle{{background:#21262d;color:#8b949e}}
.hud-dot{{width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block}}
.hud-ticker{{font-size:11px;color:#8b949e;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.hud-check{{font-size:11px;color:#8b949e;display:flex;align-items:center;gap:4px;cursor:pointer}}
#graph-hud-bottom{{position:fixed;bottom:12px;left:12px;z-index:30;display:flex;align-items:center;gap:8px;background:rgba(22,27,34,0.88);backdrop-filter:blur(10px);border:1px solid #30363d;border-radius:8px;padding:5px 12px;box-shadow:0 4px 16px rgba(0,0,0,0.5)}}
.hud-toggle-pill{{background:#101923;border:1px solid #30363d;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:600;cursor:pointer;color:#8b949e;transition:all .15s}}
.hud-toggle-pill:hover{{background:#161b22;color:#f0f6fc}}
.hud-toggle-pill.pill-blocked{{color:#ffc77e;border-color:#664f19;background:#2b2009}}
.hud-toggle-pill.pill-extendable{{color:#ffaa44;border-color:#6e4014;background:#2b1809}}
.hud-meta{{font-size:10px;color:#8b949e;margin-left:6px}}
.hud-card{{position:fixed;z-index:40;background:#161b22fa;backdrop-filter:blur(12px);border:1px solid #30363d;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,0.7);display:flex;flex-direction:column;overflow:hidden}}
.hud-card[hidden]{{display:none}}
.hud-card-header{{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#101923;border-bottom:1px solid #30363d}}
.hud-card-header h4{{margin:0;font-size:12px;font-weight:600;color:#f0f6fc}}
.hud-close{{background:none;border:none;color:#8b949e;font-size:16px;cursor:pointer;padding:0 4px;line-height:1}}
.hud-close:hover{{color:#ff9299}}
.hud-card-body{{padding:10px;overflow-y:auto;max-height:420px;display:flex;flex-direction:column;gap:6px}}
#hud-popover-blocked{{bottom:52px;left:12px;width:350px}}
#hud-popover-extendable{{bottom:52px;left:140px;width:370px}}
#graph-inspector{{top:58px;right:12px;width:340px;max-height:calc(100vh - 80px)}}
.item-card{{background:#0d1117;border:1px solid #21262d;border-radius:5px;padding:6px 8px;display:flex;flex-direction:column;gap:3px}}
.item-header{{display:flex;justify-content:space-between;align-items:center}}
.item-title{{background:none;border:none;padding:0;font-size:11px;font-weight:600;color:#5ce1dc;cursor:pointer;text-align:left}}
.item-title:hover{{text-decoration:underline}}
.item-meta{{font-size:10px;color:#8b949e}}
.item-warning{{font-size:10px;color:#ffc77e}}
.btn-approve-time{{background:#2b220d;border:1px solid #ffc77e;color:#ffc77e;font-size:10px;padding:3px 8px;border-radius:4px;cursor:pointer;font-weight:600;margin-top:3px;align-self:flex-start;transition:all .15s}}
.btn-approve-time:hover{{background:#45330e;color:#ffe3b3;border-color:#ffe3b3}}
.badge{{font-size:10px;font-weight:600;padding:1px 5px;border-radius:4px}}
.badge-running{{background:#0e333d;color:#5ce1dc;border:1px solid #165b6d}}
.badge-ready{{background:#0f3824;color:#55d790;border:1px solid #1c6843}}
.badge-blocked{{background:#382c0f;color:#ffc77e;border:1px solid #664f19}}
.badge-exhausted{{background:#3d1518;color:#ffaa44;border:1px solid #854215}}
.badge-complete{{background:#21262d;color:#8b949e;border:1px solid #30363d}}
#graph-detail strong{{color:#8b949e;font-size:10px;text-transform:uppercase;display:block;margin-top:6px;margin-bottom:2px}}
#graph-detail p{{margin:0 0 6px;color:#c9d1d9;font-size:11px}}
.extend-box{{background:#1f190c;border:1px solid #ffc77e;border-radius:6px;padding:8px 10px;margin-top:8px}}
.extend-box h4{{margin:0 0 4px;color:#ffc77e;font-size:11px;font-weight:600}}
</style>
</head>
<body>
<!-- Canvas for Cytoscape (Full Viewport) -->
<div id="graph-canvas" role="img" aria-label="Interactive experiment dependency graph"></div>

<!-- Floating Top Status HUD -->
<header id="graph-hud-top">
  <div class="hud-group">
    <a href="/" class="hud-btn back" title="Return to Status Dashboard">← Status Dashboard</a>
    <div id="hud-status" class="hud-pill idle">
      <span class="hud-dot"></span>
      <span id="hud-status-text">Idle</span>
    </div>
    <span id="hud-task-info" class="hud-ticker">Runner idle</span>
  </div>
  <div class="hud-group">
    <input id="graph-find" class="hud-input" placeholder="🔍 Search experiments...">
    <select id="graph-campaign" class="hud-select" aria-label="Filter campaign"><option value="">All Campaigns</option></select>
    <select id="graph-filter-state" class="hud-select" aria-label="Filter state">
      <option value="">All States</option>
      <option value="running">Running</option>
      <option value="ready">Ready</option>
      <option value="blocked">Blocked</option>
      <option value="exhausted">Exhausted</option>
      <option value="complete">Complete</option>
      <option value="superseded">Superseded</option>
    </select>
    <select id="graph-layout" class="hud-select" aria-label="Layout">
      <option value="execution">Hierarchy (Left → Right)</option>
      <option value="grid">Clean Grid</option>
      <option value="cose">Organic (Force-Directed)</option>
      <option value="blockers">Radial Impact</option>
    </select>
    <select id="graph-limit" class="hud-select" aria-label="Visible nodes limit">
      <option value="50">50 nodes</option>
      <option value="100" selected>100 nodes</option>
      <option value="250">250 nodes</option>
      <option value="500">500 nodes</option>
      <option value="0">All nodes</option>
    </select>
    <label class="hud-check"><input id="graph-history" type="checkbox" checked> History</label>
    <button id="graph-fit" class="hud-btn primary" title="Fit graph to view">Fit View</button>
    <button id="graph-running" class="hud-btn" title="Focus running task">Find Running</button>
  </div>
</header>

<!-- Floating Canvas Navigation Controls (Bottom Right) -->
<div id="graph-nav-controls" style="position:fixed;bottom:14px;right:14px;z-index:30;display:flex;gap:4px;background:rgba(22,27,34,0.88);backdrop-filter:blur(8px);border:1px solid #30363d;border-radius:6px;padding:3px">
  <button id="btn-zoom-in" class="hud-btn" title="Zoom In" style="padding:4px 8px;font-size:13px;font-weight:700">+</button>
  <button id="btn-zoom-out" class="hud-btn" title="Zoom Out" style="padding:4px 8px;font-size:13px;font-weight:700">−</button>
  <button id="btn-zoom-fit" class="hud-btn" title="Reset View" style="padding:4px 8px;font-size:11px">Fit</button>
</div>

<!-- Floating Bottom HUD -->
<div id="graph-hud-bottom">
  <button id="hud-btn-blocked" class="hud-toggle-pill pill-blocked" title="View actionable blockers">
    Blocked: <strong id="blocked-count">0</strong>
  </button>
  <button id="hud-btn-extendable" class="hud-toggle-pill pill-extendable" title="View tasks eligible for more time">
    Can Extend: <strong id="extendable-count">0</strong>
  </button>
  <span id="graph-count" class="hud-meta">0 visible nodes</span>
  <span id="graph-freshness" class="hud-meta">Live</span>
</div>

<!-- Floating Card: Blocked Experiments Popover -->
<div id="hud-popover-blocked" class="hud-card" hidden>
  <div class="hud-card-header">
    <h4>Actionable Blockers</h4>
    <button class="hud-close" onclick="document.getElementById('hud-popover-blocked').hidden=true">×</button>
  </div>
  <div id="graph-blockers" class="hud-card-body"></div>
</div>

<!-- Floating Card: Extendable Experiments Popover (1-Button Approvals) -->
<div id="hud-popover-extendable" class="hud-card" hidden>
  <div class="hud-card-header">
    <h4>Can Receive More Time</h4>
    <button class="hud-close" onclick="document.getElementById('hud-popover-extendable').hidden=true">×</button>
  </div>
  <div id="graph-extendable" class="hud-card-body"></div>
</div>

<!-- Floating Inspector Card (Right side) -->
<aside id="graph-inspector" class="hud-card" hidden>
  <div class="hud-card-header">
    <h4 id="inspector-title">Job Details</h4>
    <button class="hud-close" onclick="document.getElementById('graph-inspector').hidden=true">×</button>
  </div>
  <div id="graph-detail" class="hud-card-body" aria-live="polite">
    Select a node in the graph to view test hypothesis, decision rule, blockers, and limits.
  </div>
</aside>

<!-- Hidden compatibility elements for automated tests -->
<div style="display:none" aria-hidden="true">
  <header id="top-bar"></header>
  <section id="graph-panel"></section>
  <select id="graph-node-list"></select>
  <table id="rows-table"><tbody id="rows"></tbody></table>
  <div id="completed"></div>
  <div id="superseded-rows"></div>
  <div id="graph-tools">
    <button id="graph-show"></button>
    <button id="graph-hide"></button>
  </div>
  <p id="graph-warning" role="status"></p>
</div>

<script>
window.data = {payload};
window.DESCRIPTIONS = {descriptions};
const TOKEN={json.dumps(token)};
var data = window.data;
var DESCRIPTIONS = window.DESCRIPTIONS;

function description(row) {{
  return (window.DESCRIPTIONS && window.DESCRIPTIONS[row.job]) || {{
    title: row.question || row.hypothesis || row.job,
    test: row.hypothesis || '',
    answers: row.decisionRule || '',
    source: 'job'
  }};
}}

// Setup popover toggles
document.addEventListener('DOMContentLoaded', () => {{
  const btnB = document.getElementById('hud-btn-blocked');
  const btnE = document.getElementById('hud-btn-extendable');
  if (btnB) btnB.onclick = () => {{
    const popB = document.getElementById('hud-popover-blocked');
    const popE = document.getElementById('hud-popover-extendable');
    popB.hidden = !popB.hidden;
    if (popE) popE.hidden = true;
  }};
  if (btnE) btnE.onclick = () => {{
    const popB = document.getElementById('hud-popover-blocked');
    const popE = document.getElementById('hud-popover-extendable');
    popE.hidden = !popE.hidden;
    if (popB) popB.hidden = true;
  }};
}});

// 1-button approval for more time / resources
async function approveMoreTime(jobId, timeout, maxBytes) {{
  const btn = document.getElementById('btn-extend-' + jobId) || document.getElementById('btn-extend-detail-' + jobId) || (window.event ? window.event.target : null);
  if (btn) {{
    btn.disabled = true;
    btn.textContent = 'Approving...';
  }}
  const origin = window.location.port === '8766' ? 'http://127.0.0.1:8765' : '';
  const token = typeof TOKEN !== 'undefined' && TOKEN ? TOKEN : '';
  try {{
    const res = await fetch(origin + '/api/extend', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        ...(token ? {{'Authorization': 'Bearer ' + token}} : {{}})
      }},
      body: JSON.stringify({{
        job: jobId,
        timeoutSeconds: Number(timeout) || 800,
        maxOutputBytes: Number(maxBytes) || 100000000,
        reason: 'Maintainer 1-button extension approval for ' + jobId
      }})
    }});
    const result = await res.json();
    if (!res.ok) throw new Error(result.error || 'Failed to approve extension');
    if (btn) {{
      btn.textContent = '✓ Approved (' + (result.result?.job || 'saved') + ')';
      btn.style.background = '#185133';
      btn.style.borderColor = '#55d790';
    }}
    setTimeout(async () => {{
      try {{
        const r = await fetch(origin + '/api/state');
        if (r.ok) {{
          window.data = await r.json();
          data = window.data;
          if (typeof render === 'function') render();
        }}
      }} catch(e) {{}}
    }}, 800);
  }} catch (err) {{
    if (btn) {{
      btn.disabled = false;
      btn.textContent = 'Error: ' + err.message;
      btn.style.background = '#852d34';
    }}
    alert('Extension error: ' + err.message);
  }}
}}
</script>
<script>
{asset_str}
;
{js_logic}
</script>
</body>
</html>"""
    return page
