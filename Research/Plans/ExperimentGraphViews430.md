# GRAPH430 — internal graph viewer implementation

Status: planned, not implemented. Decision: [ADR-0030](../ADR-0030-Read-Only-Experiment-Graph-Views.md).
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

This change delivers the ADR, layout specifications, and implementation tasks only.
No dashboard assets are downloaded. No graph view is deployed. No current experiment is restarted.
