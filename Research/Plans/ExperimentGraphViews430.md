# GRAPH430 — internal graph viewer implementation

Status: 2D views implemented. Decision: [ADR-0030](../ADR-0030-Read-Only-Experiment-Graph-Views.md).
The maintainer selects Cytoscape.js. The graph does not edit or execute experiments.

## Delivery sequence

| Task | Deliverable | Acceptance |
| --- | --- | --- |
| GRAPH430-01 | Versioned projection from queue records to graph data | Stable identities; explicit data and condition edges; missing references remain visible; no execution writes. |
| GRAPH430-02 | 2D execution map and blocker map | Matching nodes across layouts; correct unique descendant counts; running job and actionable blockers visible. |
| GRAPH430-03 | Optional 3D execution layers and dependency explorer | Same snapshot and inspector; bounded simulation; WebGL fallback; no hidden background animation. |
| GRAPH430-04 | Snapshot refresh and shared inspector | Selection persists; stale data is labelled; hostile descriptions render as text; completed branches collapse. |
| GRAPH430-05 | Runtime and integration qualification | Real campaign plus negative fixtures; measured performance; no mutation requests; no changed worker approvals. |
| GRAPH430-06 | Private maintenance boundary | Maintainer selects the private repository. Public Swift and model consumers acquire no dashboard dependency. |

Use existing snapshots rather than repeatedly reading individual jobs from the browser.
Provide a read-only source interface before moving implementation between repositories.
Use test fixtures for graph failures. Do not rerun training to test the viewer.
Do not move running tools or introduce a second scheduler.

## Blocking decisions

The private repository destination is not selected. Do not create one without explicit direction.
The 3D companion remains a proposal because Cytoscape.js alone does not provide the requested 3D renderer.
Pin and review exact dependencies before installation. The 2D source contract can proceed independently.

## Scope of this delivery

The read-only companion runs on loopback port 8766. The original list and controls remain on port 8765.
The companion also preserves the list below its optional graph panel.
It reads the existing snapshot API. It cannot dispatch, approve, stop, or cancel jobs.
The original server and runner share one process. The companion avoids restarting that process during training.

The 2D execution view uses Cytoscape's built-in breadth-first layout with rotated coordinates.
The 2D blocker view uses concentric rings by dependency distance from the selected blocker.
This replaces the planned Dagre dependency for the first delivery.
The local Cytoscape 3.33.1 asset has a checked hash and its MIT license.
No browser asset request leaves the machine.

The graph shows recorded prerequisites only. The snapshot does not expose typed decision conditions.
Unknown owners and unrecorded actions stay explicit. The viewer does not infer them from prose.
Completed records hide by default. A checkbox restores them to inspect dependency continuity.
The running panel remains visible above both views. Keyboard inspection supplies a canvas alternative.
Refresh preserves the viewport when topology is unchanged. Hidden tabs stop polling.

## Qualification bounds

- Project a 2,500-job fixture within 1 s.
- Render at most 180 nodes per selected campaign or branch.
- Read at most 32 MiB per snapshot. Cache reads for 10 s.
- Test missing references, cycles, duplicate identities, hidden history, and unique downstream counts.
- Test hostile text, refused origins, unknown paths, unavailable snapshots, and rejected POST requests.
- Keep the original runner process and code pins unchanged.

Run `node scripts/test_research_graph_view.js` for graph and layout checks.
Run `python -B -m unittest discover -s scripts -p 'test_research_graph_view.py'` for rendering and transport checks.
Start the companion with `python -B scripts/research_graph_server.py` from the project environment.

3D views and the private repository remain separate decisions. They do not block this read-only delivery.
