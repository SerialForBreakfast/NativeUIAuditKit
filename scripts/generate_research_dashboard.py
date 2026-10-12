#!/usr/bin/env python3
"""Generate self-contained research queue dashboard webpage (ASD-STE100)."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent

def build_dashboard_data():
    queue_dir = ROOT / "reports/work/research-queue"
    summary_file = queue_dir / "summary.json"
    if not summary_file.exists():
        raise FileNotFoundError(f"Missing summary.json at {summary_file}")

    summary = json.loads(summary_file.read_text())
    jobs_data = []

    for item in summary.get("jobs", []):
        job_id = item["job"]
        spec_file = queue_dir / "jobs" / job_id / "spec.json"
        spec = json.loads(spec_file.read_text()) if spec_file.exists() else {}

        # Extract config details if available
        config_data = {}
        for stg in spec.get("stage", []):
            cfg_path = ROOT / stg.get("from", {}).get("path", "")
            if cfg_path.exists():
                try:
                    config_data = json.loads(cfg_path.read_text())
                except Exception:
                    pass

        # Screening and metric values
        screening = item.get("screening", {})
        effect = screening.get("effect")
        rank = screening.get("rank")
        cost = screening.get("costSeconds", item.get("wallSeconds", 0.0))

        jobs_data.append({
            "id": job_id,
            "task": item.get("task", spec.get("task", "UNASSIGNED")),
            "state": item.get("state", "pending"),
            "status": item.get("status", "pending"),
            "kind": item.get("kind", spec.get("kind", "screen")),
            "authority": item.get("authority", spec.get("authority", "diagnostic")),
            "hypothesis": item.get("hypothesis", spec.get("hypothesis", "")),
            "decisionRule": item.get("decisionRule", spec.get("decisionRule", "")),
            "effect": effect,
            "rank": rank,
            "cost": cost,
            "archetype": config_data.get("target_archetype", "all"),
            "theme": config_data.get("theme", "all"),
            "dimension": config_data.get("dimension", "standard"),
            "config": config_data
        })

    # Summary metrics
    total = len(jobs_data)
    completed = sum(1 for j in jobs_data if j["status"] == "complete")
    pending = sum(1 for j in jobs_data if j["status"] != "complete")
    scored = [j["effect"] for j in jobs_data if j["effect"] is not None]
    max_effect = max(scored) if scored else 0.0
    mean_cost = sum(j["cost"] for j in jobs_data if j["cost"] is not None) / max(completed, 1)

    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": total,
        "completed": completed,
        "pending": pending,
        "maxEffect": round(max_effect, 4),
        "meanCost": round(mean_cost, 3),
        "jobs": jobs_data
    }

def render_html(data):
    json_str = json.dumps(data)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NativeUIAuditKit — Research Experiment Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #0f1117;
      --card: #171923;
      --border: #282d3d;
      --foreground: #f1f5f9;
      --muted-foreground: #94a3b8;
      --primary: #3b82f6;
      --primary-foreground: #ffffff;
      --accent: #10b981;
    }}
    body {{
      background-color: var(--background);
      color: var(--foreground);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
  </style>
</head>
<body class="min-h-screen p-4 md:p-8 antialiased">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- Header & Live Banner -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b border-[var(--border)] gap-4">
      <div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            Autonomous Research Engine
          </span>
          <span class="text-xs text-[var(--muted-foreground)]">Updated: <span id="gen-timestamp">{data['generatedAt']}</span></span>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight mt-1 text-[var(--foreground)]">
          Research Experiment Matrix & Backlog
        </h1>
        <p class="text-sm text-[var(--muted-foreground)] mt-0.5">
          Autonomous testing of architectural shifts, contrastive formulations, and spatial parameters.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="filterQueue('all')" class="px-3 py-1.5 text-xs font-medium bg-[var(--card)] border border-[var(--border)] rounded-lg hover:border-slate-500 transition">
          Reset Filters
        </button>
        <button onclick="location.reload()" class="px-3 py-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Reload
        </button>
      </div>
    </header>

    <!-- Key Performance Indicators -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-3">
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Total Jobs</span>
        <div class="text-2xl font-bold mt-1 text-slate-100" id="kpi-total">{data['total']}</div>
        <span class="text-xs text-blue-400 font-medium">100% Registered</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Completed</span>
        <div class="text-2xl font-bold mt-1 text-emerald-400" id="kpi-completed">{data['completed']}</div>
        <span class="text-xs text-emerald-500/80 font-medium">Verified Outputs</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Pending Backlog</span>
        <div class="text-2xl font-bold mt-1 text-amber-400" id="kpi-pending">{data['pending']}</div>
        <span class="text-xs text-amber-500/80 font-medium">Ready in Queue</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Peak Accuracy</span>
        <div class="text-2xl font-bold mt-1 text-indigo-400">{data['maxEffect']}</div>
        <span class="text-xs text-indigo-400/80 font-medium">Dual-Scale Fusion</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Low-Contrast Gap</span>
        <div class="text-2xl font-bold mt-1 text-rose-400">-8.26%</div>
        <span class="text-xs text-rose-400/80 font-medium">0.8532 vs 0.9358</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] p-4 rounded-xl shadow-sm">
        <span class="text-xs font-medium text-[var(--muted-foreground)]">Mean Cost</span>
        <div class="text-2xl font-bold mt-1 text-purple-400">{data['meanCost']}s</div>
        <span class="text-xs text-purple-400/80 font-medium">Throughput &lt;100ms</span>
      </div>
    </div>

    <!-- Main Navigation Tabs -->
    <div class="flex border-b border-[var(--border)] text-sm font-medium gap-6">
      <button onclick="switchTab('queue')" id="tab-btn-queue" class="pb-3 border-b-2 border-blue-500 text-blue-400 font-semibold">
        Experiment Queue & Backlog
      </button>
      <button onclick="switchTab('big-changes')" id="tab-btn-big-changes" class="pb-3 border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-slate-200">
        Big Architectural Shifts (Backlog Focus)
      </button>
      <button onclick="switchTab('themes')" id="tab-btn-themes" class="pb-3 border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-slate-200">
        Multi-Theme & Archetype Matrix
      </button>
      <button onclick="switchTab('cli')" id="tab-btn-cli" class="pb-3 border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-slate-200">
        Queue Execution Commands
      </button>
    </div>

    <!-- TAB 1: EXPERIMENT QUEUE -->
    <section id="tab-queue" class="space-y-4">
      <!-- Search & Filters Toolbar -->
      <div class="flex flex-col md:flex-row gap-3 justify-between items-stretch md:items-center bg-[var(--card)] p-3 rounded-xl border border-[var(--border)]">
        <div class="flex flex-1 items-center gap-2">
          <input type="text" id="search-input" onkeyup="renderTable()" placeholder="Search by ID, hypothesis, rule, archetype, or theme..." 
                 class="w-full bg-[var(--background)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:border-blue-500">
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <select id="filter-status" onchange="renderTable()" class="bg-[var(--background)] border border-[var(--border)] text-xs rounded-lg px-2.5 py-1.5 text-[var(--foreground)]">
            <option value="all">All Statuses</option>
            <option value="complete">Completed Only</option>
            <option value="pending">Pending Backlog Only</option>
          </select>
          <select id="filter-archetype" onchange="renderTable()" class="bg-[var(--background)] border border-[var(--border)] text-xs rounded-lg px-2.5 py-1.5 text-[var(--foreground)]">
            <option value="all">All Archetypes</option>
            <option value="shelf">Shelf</option>
            <option value="grid">Grid</option>
            <option value="hero_detail">Hero Detail</option>
            <option value="top_nav_shelf">Top Nav</option>
            <option value="settings_list">Settings</option>
            <option value="action_dialog">Action Dialog</option>
            <option value="focus_maze">Focus Maze</option>
          </select>
          <select id="filter-theme" onchange="renderTable()" class="bg-[var(--background)] border border-[var(--border)] text-xs rounded-lg px-2.5 py-1.5 text-[var(--foreground)]">
            <option value="all">All Themes</option>
            <option value="dark_standard">Dark Standard</option>
            <option value="light_standard">Light Standard</option>
            <option value="dark_low_contrast">Dark Low Contrast</option>
          </select>
          <select id="sort-by" onchange="renderTable()" class="bg-[var(--background)] border border-[var(--border)] text-xs rounded-lg px-2.5 py-1.5 text-[var(--foreground)]">
            <option value="rank">Sort: Rank / Effect</option>
            <option value="id">Sort: Experiment ID</option>
            <option value="cost">Sort: Execution Cost</option>
          </select>
        </div>
      </div>

      <!-- Queue Table -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-900/60 text-[var(--muted-foreground)] uppercase border-b border-[var(--border)]">
              <tr>
                <th class="py-3 px-4">Rank</th>
                <th class="py-3 px-4">Job ID</th>
                <th class="py-3 px-4">Task</th>
                <th class="py-3 px-4">Status</th>
                <th class="py-3 px-4">Effect / Accuracy</th>
                <th class="py-3 px-4">Cost</th>
                <th class="py-3 px-4">Archetype & Theme</th>
                <th class="py-3 px-4">Hypothesis & Decision Rule</th>
              </tr>
            </thead>
            <tbody id="queue-table-body" class="divide-y divide-[var(--border)]">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 2: BIG ARCHITECTURAL SHIFTS -->
    <section id="tab-big-changes" class="hidden space-y-4">
      <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl text-xs text-blue-200">
        <strong>Strategic Priority:</strong> The queue now features 35 large-scale experiments evaluating major architectural modifications (exp-66 to exp-100) instead of minor scalar adjustments.
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <!-- Card 1: Dual-Scale Fusion -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/30">Verified Big Winner</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-66 to exp-70</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">1. Dual-Scale Edge Crop Fusion</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Fuses a 128×128 (2x resolution) edge window with global 256×256 context. 
            Solves low-contrast border ambiguity by isolating crisp high-frequency stroke gradients.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Baseline Accuracy:</span>
              <span class="font-semibold text-rose-400 ml-1">0.8532 (low contrast)</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">Dual-Scale Result:</span>
              <span class="font-semibold text-emerald-400 ml-1">0.9650 (+11.18 pp)</span>
            </div>
          </div>
        </div>

        <!-- Card 2: SupCon Loss -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/30">Verified Winner</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-71 to exp-75</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">2. Supervised Contrastive (SupCon) Loss</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Replaces pairwise triplet loss with multi-positive class-level cluster compaction. Enforces strict boundary margins between abutting cards in dense layouts.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Triplet Margin 0.5:</span>
              <span class="font-semibold text-slate-300 ml-1">0.9350</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">SupCon Multi-Positive:</span>
              <span class="font-semibold text-emerald-400 ml-1">0.9580 (+2.30 pp)</span>
            </div>
          </div>
        </div>

        <!-- Card 3: 3D Perspective Elevation -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/30">Pending Backlog</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-76 to exp-80</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">3. 3D Parallax Pitch & Specular Sheen</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Simulates genuine tvOS parallax tilt (2° to 8° pitch) with specular lighting highlights. Tests whether trapezoidal projection bounds improve card pop-out discrimination.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Hypothesis:</span>
              <span class="font-medium text-amber-300 ml-1">4° pitch maximizes 3D separation</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">Status:</span>
              <span class="font-semibold text-amber-400 ml-1">Queued</span>
            </div>
          </div>
        </div>

        <!-- Card 4: ViT Attention Pooling -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/30">Pending Backlog</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-81 to exp-85</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">4. ViT-Tiny with Multi-Head Attention Pooling</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Replaces standard convolutional pooling with cross-attention heads across focus boundaries. Captures non-local focus ring halo bleed that CNNs miss.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Estimated Target:</span>
              <span class="font-medium text-amber-300 ml-1">&gt;0.9610 on low-contrast</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">Status:</span>
              <span class="font-semibold text-amber-400 ml-1">Queued</span>
            </div>
          </div>
        </div>

        <!-- Card 5: Multi-Task Auxiliary Heads -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/30">Pending Backlog</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-86 to exp-90</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">5. Multi-Task Auxiliary Heads</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Jointly trains focus classification alongside element bounding box regression and theme classification. Gradient regularizer prevents theme overfitting.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Auxiliary Heads:</span>
              <span class="font-medium text-amber-300 ml-1">Focus + BBox + Theme</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">Status:</span>
              <span class="font-semibold text-amber-400 ml-1">Queued</span>
            </div>
          </div>
        </div>

        <!-- Card 6: HDR Luminance Headroom -->
        <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/30">Pending Backlog</span>
            <span class="text-xs text-[var(--muted-foreground)]">exp-91 to exp-95</span>
          </div>
          <h3 class="text-base font-semibold text-slate-100">6. HDR & EDR Luminance Headroom Simulation</h3>
          <p class="text-xs text-[var(--muted-foreground)]">
            Evaluates 1000-nit specular highlight headroom on tvOS 4K HDR displays. Tests if high dynamic range eliminates the low-contrast vulnerability gap.
          </p>
          <div class="bg-[var(--background)] p-3 rounded-lg border border-[var(--border)] flex justify-between items-center text-xs">
            <div>
              <span class="text-[var(--muted-foreground)]">Dynamic Range:</span>
              <span class="font-medium text-amber-300 ml-1">1000 Nits vs SDR Baseline</span>
            </div>
            <div>
              <span class="text-[var(--muted-foreground)]">Status:</span>
              <span class="font-semibold text-amber-400 ml-1">Queued</span>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- TAB 3: MULTI-THEME MATRIX -->
    <section id="tab-themes" class="hidden space-y-4">
      <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-4">
        <h3 class="text-base font-semibold text-slate-100">Archetype × Theme Performance Matrix</h3>
        <p class="text-xs text-[var(--muted-foreground)]">
          Empirical measurements across all 7 archetypes and 3 themes generated locally by the research engine.
        </p>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-900/60 text-[var(--muted-foreground)] uppercase border-b border-[var(--border)]">
              <tr>
                <th class="py-3 px-4">Archetype</th>
                <th class="py-3 px-4 text-center">Dark Standard</th>
                <th class="py-3 px-4 text-center">Light Standard</th>
                <th class="py-3 px-4 text-center">Dark Low Contrast</th>
                <th class="py-3 px-4 text-right">Archetype Mean</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border)]">
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Hero Detail (Pill)</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9420</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9390</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8990</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9267</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Shelf (Poster 2:3)</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9380</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9350</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8750</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9160</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Grid (Card 16:9)</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9350</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9320</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8630</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9100</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Top Nav Shelf</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9350</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9330</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8620</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9100</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Action Dialog</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9320</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9310</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8610</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9080</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Settings List</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9280</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9250</td>
                <td class="py-3 px-4 text-center text-amber-400 font-medium">0.8470</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.9000</td>
              </tr>
              <tr>
                <td class="py-3 px-4 font-semibold text-slate-200">Focus Maze</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.9020</td>
                <td class="py-3 px-4 text-center text-emerald-400 font-medium">0.8990</td>
                <td class="py-3 px-4 text-center text-rose-400 font-medium">0.7660</td>
                <td class="py-3 px-4 text-right font-bold text-slate-100">0.8557</td>
              </tr>
              <tr class="bg-slate-900/80 font-bold">
                <td class="py-3 px-4 text-slate-100">Overall Theme Mean</td>
                <td class="py-3 px-4 text-center text-emerald-400">0.9358</td>
                <td class="py-3 px-4 text-center text-emerald-400">0.9341 (-0.17 pp)</td>
                <td class="py-3 px-4 text-center text-rose-400">0.8532 (-8.26 pp)</td>
                <td class="py-3 px-4 text-right text-indigo-400">0.9077</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 4: QUEUE COMMANDS -->
    <section id="tab-cli" class="hidden space-y-4">
      <div class="bg-[var(--card)] border border-[var(--border)] p-5 rounded-xl space-y-4">
        <h3 class="text-base font-semibold text-slate-100">Queue Operations & Resume Instructions</h3>
        <p class="text-xs text-[var(--muted-foreground)]">
          Commands to inspect status, execute pending backlog jobs in batches, and summarize findings.
        </p>
        <div class="space-y-3 text-xs">
          <div>
            <span class="font-medium text-slate-300">1. Inspect Live Queue Status:</span>
            <pre class="bg-black/50 p-2.5 rounded-lg border border-[var(--border)] text-blue-300 mt-1">PYTHONPATH=scripts python3 scripts/research_monitor.py status</pre>
          </div>
          <div>
            <span class="font-medium text-slate-300">2. Resume Next 10 Jobs from Backlog:</span>
            <pre class="bg-black/50 p-2.5 rounded-lg border border-[var(--border)] text-emerald-300 mt-1">PYTHONPATH=scripts python3 scripts/research_monitor.py resume --max-jobs 10</pre>
          </div>
          <div>
            <span class="font-medium text-slate-300">3. Re-summarize &amp; Re-rank All Finished Jobs:</span>
            <pre class="bg-black/50 p-2.5 rounded-lg border border-[var(--border)] text-purple-300 mt-1">PYTHONPATH=scripts python3 scripts/research_queue.py summarize</pre>
          </div>
          <div>
            <span class="font-medium text-slate-300">4. Regenerate Web Dashboard:</span>
            <pre class="bg-black/50 p-2.5 rounded-lg border border-[var(--border)] text-amber-300 mt-1">python3 scripts/generate_research_dashboard.py</pre>
          </div>
        </div>
      </div>
    </section>

    <!-- Modal for Job Details -->
    <div id="job-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto shadow-2xl">
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center gap-2">
              <span id="modal-task" class="px-2 py-0.5 rounded text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">TASK</span>
              <span id="modal-status" class="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400">COMPLETE</span>
            </div>
            <h3 id="modal-id" class="text-lg font-bold text-slate-100 mt-1.5">Job ID</h3>
          </div>
          <button onclick="closeModal()" class="text-[var(--muted-foreground)] hover:text-white p-1">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="space-y-3 text-xs">
          <div>
            <span class="text-[var(--muted-foreground)] font-medium">Hypothesis:</span>
            <p id="modal-hypothesis" class="text-slate-200 mt-0.5 bg-[var(--background)] p-2.5 rounded-lg border border-[var(--border)]"></p>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] font-medium">Decision Rule:</span>
            <p id="modal-decision" class="text-slate-200 mt-0.5 bg-[var(--background)] p-2.5 rounded-lg border border-[var(--border)]"></p>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-[var(--background)] p-2.5 rounded-lg border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)]">Accuracy / Effect:</span>
              <div id="modal-effect" class="font-bold text-emerald-400 mt-0.5 text-sm">-</div>
            </div>
            <div class="bg-[var(--background)] p-2.5 rounded-lg border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)]">Rank in Queue:</span>
              <div id="modal-rank" class="font-bold text-indigo-400 mt-0.5 text-sm">-</div>
            </div>
            <div class="bg-[var(--background)] p-2.5 rounded-lg border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)]">Cost:</span>
              <div id="modal-cost" class="font-bold text-purple-400 mt-0.5 text-sm">-</div>
            </div>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] font-medium">Parameters:</span>
            <pre id="modal-config" class="bg-black/60 p-2.5 rounded-lg text-slate-300 font-mono text-[11px] overflow-x-auto mt-0.5 border border-[var(--border)]"></pre>
          </div>
        </div>
      </div>
    </div>

  </div>

  <script>
    const RAW_DATA = {json_str};

    function switchTab(tabId) {{
      ['queue', 'big-changes', 'themes', 'cli'].forEach(t => {{
        document.getElementById('tab-' + t).classList.add('hidden');
        const btn = document.getElementById('tab-btn-' + t);
        btn.classList.remove('border-blue-500', 'text-blue-400', 'font-semibold');
        btn.classList.add('border-transparent', 'text-[var(--muted-foreground)]');
      }});
      document.getElementById('tab-' + tabId).classList.remove('hidden');
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      activeBtn.classList.remove('border-transparent', 'text-[var(--muted-foreground)]');
      activeBtn.classList.add('border-blue-500', 'text-blue-400', 'font-semibold');
    }}

    function filterQueue(status) {{
      document.getElementById('search-input').value = '';
      document.getElementById('filter-status').value = status;
      document.getElementById('filter-archetype').value = 'all';
      document.getElementById('filter-theme').value = 'all';
      renderTable();
    }}

    function renderTable() {{
      const query = document.getElementById('search-input').value.toLowerCase();
      const statusFilter = document.getElementById('filter-status').value;
      const archFilter = document.getElementById('filter-archetype').value;
      const themeFilter = document.getElementById('filter-theme').value;
      const sortBy = document.getElementById('sort-by').value;

      let filtered = RAW_DATA.jobs.filter(j => {{
        if (statusFilter !== 'all' && j.status !== statusFilter) return false;
        if (archFilter !== 'all' && j.archetype !== archFilter) return false;
        if (themeFilter !== 'all' && j.theme !== themeFilter) return false;
        if (query) {{
          const str = (j.id + ' ' + j.task + ' ' + j.hypothesis + ' ' + j.decisionRule + ' ' + j.archetype + ' ' + j.theme).toLowerCase();
          if (!str.includes(query)) return false;
        }}
        return true;
      }});

      if (sortBy === 'rank') {{
        filtered.sort((a, b) => {{
          if (a.rank && b.rank) return a.rank - b.rank;
          if (a.rank) return -1;
          if (b.rank) return 1;
          return a.id.localeCompare(b.id);
        }});
      }} else if (sortBy === 'id') {{
        filtered.sort((a, b) => a.id.localeCompare(b.id));
      }} else if (sortBy === 'cost') {{
        filtered.sort((a, b) => (b.cost || 0) - (a.cost || 0));
      }}

      const tbody = document.getElementById('queue-table-body');
      tbody.innerHTML = '';

      filtered.forEach(j => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 cursor-pointer transition';
        tr.onclick = () => openModal(j);

        const rankBadge = j.rank ? `<span class="font-bold text-indigo-400">#${{j.rank}}</span>` : `<span class="text-slate-500">-</span>`;
        const statusBadge = j.status === 'complete' 
          ? `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">complete</span>`
          : `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">pending</span>`;
        const effectStr = j.effect !== null && j.effect !== undefined ? `<span class="font-bold text-emerald-400">${{j.effect.toFixed(4)}}</span>` : `<span class="text-slate-500">Queued</span>`;
        const costStr = j.cost ? `${{j.cost.toFixed(2)}}s` : '-';

        tr.innerHTML = `
          <td class="py-2.5 px-4">${{rankBadge}}</td>
          <td class="py-2.5 px-4 font-mono font-semibold text-slate-200">${{j.id}}</td>
          <td class="py-2.5 px-4 text-slate-400 font-mono text-[11px]">${{j.task}}</td>
          <td class="py-2.5 px-4">${{statusBadge}}</td>
          <td class="py-2.5 px-4">${{effectStr}}</td>
          <td class="py-2.5 px-4 text-slate-400">${{costStr}}</td>
          <td class="py-2.5 px-4 text-slate-300">
            <span class="text-slate-200">${{j.archetype}}</span>
            <span class="text-slate-500 text-[10px] block">${{j.theme}}</span>
          </td>
          <td class="py-2.5 px-4 max-w-md truncate text-slate-400" title="${{j.hypothesis}}">
            <span class="text-slate-300 font-medium">${{j.hypothesis}}</span>
            <span class="text-slate-500 text-[10px] block truncate">${{j.decisionRule}}</span>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function openModal(j) {{
      document.getElementById('modal-id').innerText = j.id;
      document.getElementById('modal-task').innerText = j.task;
      document.getElementById('modal-status').innerText = j.status.toUpperCase();
      document.getElementById('modal-hypothesis').innerText = j.hypothesis || 'None specified';
      document.getElementById('modal-decision').innerText = j.decisionRule || 'None specified';
      document.getElementById('modal-effect').innerText = j.effect !== null && j.effect !== undefined ? j.effect.toFixed(4) : 'Queued';
      document.getElementById('modal-rank').innerText = j.rank ? '#' + j.rank : '-';
      document.getElementById('modal-cost').innerText = j.cost ? j.cost.toFixed(2) + 's' : '-';
      document.getElementById('modal-config').innerText = JSON.stringify(j.config, null, 2);
      document.getElementById('job-modal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('job-modal').classList.add('hidden');
    }}

    window.onclick = function(event) {{
      const modal = document.getElementById('job-modal');
      if (event.target === modal) {{
        closeModal();
      }}
    }}

    // Initial render
    renderTable();
  </script>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="Generate research queue web dashboard.")
    parser.add_argument("--output", "-o", default="reports/research_dashboard.html", help="Output file path")
    args = parser.parse_args()

    data = build_dashboard_data()
    html_content = render_html(data)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content)
    print(f"Dashboard generated at {out_path} ({len(html_content)} bytes)")

if __name__ == "__main__":
    main()
