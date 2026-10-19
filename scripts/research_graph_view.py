"""Read-only graph views for the existing queue dashboard."""
from pathlib import Path
import hashlib
from generate_research_dashboard import render_html

HERE = Path(__file__).resolve().parent
ASSET_HASH = 'f55947f3daa3bae53209d4b885c195c157f595c225e508a6b382598d9452d6e2'


def render_graph(data):
    """Keep the original list and add local graph assets. Never expose a mutation token."""
    asset = (HERE / 'vendor/cytoscape-3.33.1/cytoscape.min.js').read_bytes()
    if hashlib.sha256(asset).hexdigest() != ASSET_HASH:
        raise ValueError('Cytoscape asset hash mismatch')
    page = render_html(data)
    page = page.replace('Read-only snapshot. Start the local dashboard server for controls.',
                        'Read-only companion. Use the original dashboard for execution controls.')
    style = '''<style>
    #graph-tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:12px 0}
    #graph-panel{border:1px solid #52697f;border-radius:10px;background:#101923;padding:14px;margin-bottom:16px}
    #graph-panel[hidden]{display:none}
    #graph-panel h2{margin:0;font-size:18px;color:#f0f6fc}
    #graph-toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}
    #graph-toolbar label{display:flex;gap:6px;align-items:center}
    #graph-workspace{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:14px}
    #graph-canvas{height:580px;min-width:0;background:#0d1117;border:1px solid #30363d;border-radius:8px}
    #graph-detail{max-height:580px;overflow:auto;padding:12px;background:#161b22;border-radius:8px;overflow-wrap:anywhere}
    #graph-detail p{margin:4px 0 12px}#graph-detail h3{color:#f0f6fc}
    #graph-blockers{max-height:180px;overflow:auto;padding:8px;border-left:3px solid #ffc77e}
    #graph-blockers p{margin:4px 0 12px;overflow-wrap:anywhere;color:#ffc77e}
    #graph-blockers button,#graph-tools button,#graph-toolbar button{background:#24394c;color:#f0f6fc;border:1px solid #52697f;border-radius:5px;padding:7px;cursor:pointer}
    #graph-warning,#graph-freshness{color:#ffc77e;margin:8px 0}
    #active-title{font-size:16px;white-space:normal}#active-step{font-size:13px;color:#c9d1d9}
    #active{padding:14px}#active:not(.idle){border-width:2px}
    #graph-node-list{max-width:100%}
    @media(max-width:800px){#graph-workspace{grid-template-columns:1fr}#graph-canvas{height:420px}#graph-detail{max-height:300px}}
    </style>'''
    markup = '''<nav id="graph-tools" aria-label="Queue views">
    <button id="graph-show" aria-pressed="false" aria-controls="graph-panel">Open 2D graph</button>
    <button id="graph-running">Find running task</button>
    <span>The list stays below. This view cannot change execution.</span>
    <a href="http://127.0.0.1:8765/">Original dashboard and controls</a>
    </nav>
    <section id="graph-panel" hidden aria-label="Experiment dependency graph">
    <h2>Experiment map <span id="graph-count"></span></h2>
    <div id="graph-freshness" role="status"></div>
    <div id="graph-toolbar">
      <label>Campaign <select id="graph-campaign"></select></label>
      <label>View <select id="graph-layout"><option value="execution">Execution — left to right</option><option value="blockers">Blockers — radial impact</option></select></label>
      <label><input id="graph-history" type="checkbox">Include completed history</label>
      <input id="graph-find" aria-label="Find graph job" placeholder="Highlight ID or title">
      <button id="graph-fit">Fit graph</button><button id="graph-hide">Close graph</button>
    </div>
    <details open><summary>Actionable blockers in this campaign</summary><div id="graph-blockers"></div></details>
    <p id="graph-warning" role="status"></p>
    <p>Bright border: running · Hexagon: needs action · Green: ready · Gray: history. Arrows point to dependent jobs.</p>
    <label>Keyboard inspection <select id="graph-node-list"></select></label>
    <div id="graph-workspace"><div id="graph-canvas" role="img" aria-label="Dependency map. Use keyboard inspection for job details."></div>
    <aside id="graph-detail" aria-live="polite">Select a node to see its test, decision, and required action.</aside></div>
    </section>'''
    page = page.replace('</style>', '</style>'+style, 1)
    page = page.replace('<div class="toolbar">', markup+'<div class="toolbar">', 1)
    scripts = asset.decode()+'\n;\n'+(HERE/'research_graph_view.js').read_text()
    # Prevent an asset comment from ending the script element.
    scripts = scripts.replace('</script', '<\\/script')
    return page.replace('</html>', '<script>'+scripts+'</script></html>')
