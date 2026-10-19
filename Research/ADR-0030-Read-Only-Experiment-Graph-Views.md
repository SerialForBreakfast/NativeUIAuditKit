# ADR-0030 — Read-only experiment graph views

Date: 2026-10-18.
Status: Cytoscape.js selected by the maintainer. The 2D companion is implemented. The 3D views remain deferred.
Scope: Internal research dashboard. This is not a public NUIAK feature or model dependency.
Related: [experiment graphs](ADR-0027-Evidence-Guided-Experiment-Graphs.md), [templates](ADR-0028-Reusable-Experiment-Templates.md), and [implementation plan](Plans/ExperimentGraphViews430.md).

## Decision

Use Cytoscape.js for the optional 2D graph view beside the existing queue list.
Keep both views read-only for graph interactions. Existing execution controls remain separate.
Use the same verified snapshot for all layouts. Do not create another scheduler or execution database.
Provide 2 useful 2D layouts and specify 2 optional 3D layouts.

Cytoscape.js does not provide these 3D views through its core renderer.
Use a separate renderer rather than describe a tilted 2D canvas as a 3D graph.
The proposed companion is 3D Force Graph, which uses Three.js/WebGL and supports directed layouts.
Qualify its pinned package and dependencies before installation and rollout. No package is installed by this ADR.

## Four views

| View | Renderer and layout | Question answered | Presentation |
| --- | --- | --- | --- |
| 2D execution map | Cytoscape.js breadth-first layout, rotated left to right | What runs next, and which prerequisites must finish? | Show recorded dependencies. Add condition labels only when the snapshot supplies them. |
| 2D blocker map | Cytoscape.js concentric layout around a selected blocker | Which work does this blocker prevent? | Show upstream requirements and downstream jobs. Count unique affected jobs. Highlight running work outside the blocked branch. |
| 3D execution layers | 3D Force Graph in directed layout mode | How do several campaign branches share preparation? | Separate dependency depths into layers. Use campaign colors and readable selection labels. Keep direction visible. |
| 3D dependency explorer | 3D Force Graph radial directed layout | What does this selected task connect to across campaigns? | Show a bounded neighborhood. Expand connections on demand. Focus the camera on selection. Do not imply distance measures priority. |

The 2D execution map is the default graph layout. The existing list remains the default dashboard view.
The 3D layouts support exploration. The 2D view remains available for precise label reading and accessibility.
Layouts change presentation only. They never change priority, approval, execution, or scientific acceptance.

## Shared data contract

Project existing queue and campaign records into one versioned, sanitized graph snapshot.
Each node has a stable job identity, title, question, decision rule, owner, and current execution state.
Include delivery, evidence verification, and model acceptance as separate fields when available.
Preserve unsupported or missing information explicitly. Do not infer an owner from a project name.

Each edge identifies its source, target, and type: data, condition, or evidence.
Dependency edges mean required outputs, not scientific approval. Condition edges retain the registered predicate and outcome.
Never invent decision branches from prose. Show malformed references and cycles as data errors.
Keep completed, superseded, rejected, exhausted, and blocked states distinct.

## Interaction and readability

- Show one campaign initially. Permit search by job identity or plain-language title.
- Keep the running job prominent, with its actual step and latest progress event.
- Select a node to show its inputs, blocker, owner, next action, and affected descendants.
- Show what the test measures and what its result will decide.
- Collapse completed and superseded branches by default. Keep dependency continuity visible through summaries.
- Use labels and shapes with colors. Do not make color the only state indicator.
- Show stale snapshots explicitly. Disconnection does not mean completion.
- Preserve selection, camera, and filters during refresh. Avoid restarting layouts for every progress update.
- Disable graph editing, deletion, priority mutation, and drag-to-connect behavior.
- Keep keyboard-accessible details and the ordinary queue list available.

Blocked-impact counts exclude archived superseded work and avoid double counting shared descendants.
Show whether the count concerns direct dependents or all descendants.
Do not display timeout ceilings as estimated work duration.

## Safety, cost, and ownership

Bundle pinned assets locally. Do not load runtime scripts from a public CDN.
Keep authentication, host checks, and loopback binding unchanged.
Do not send job records, paths, tokens, or private artifacts to hosted graph services.
Render descriptions as text, not executable HTML. Bound graph size and inspector content.
Pause rendering when the graph is hidden. Stop layout simulation after settling.
Disable continuous orbit and particle effects by default. Measure idle cost during training before rollout.
If WebGL is unavailable, retain the working 2D view and show a clear explanation.

Future dashboard implementation belongs in a maintainer-selected private repository.
Keep models, Swift products, and public consumer contracts independent from that repository.
This ADR records the boundary publicly without publishing private queue records.
Do not create a repository, migrate active tools, or rewrite public history under this decision.

## Acceptance

All 4 layouts must preserve the same node identities and edge semantics for the same selection.
Verify a real campaign and controlled fixtures containing running, blocked, failed, exhausted, superseded, and conditional jobs.
Verify shared dependencies, orphan references, cycles, missing owners, empty campaigns, and hostile labels.
Verify stale progress, snapshot refresh, selection retention, and WebGL fallback.
Confirm that graph interactions send no mutation requests and cannot start jobs.
Record render time, interaction responsiveness, memory, and idle CPU/GPU cost on the research host.
Set rollout limits before the performance test. Do not claim a speed improvement from library adoption alone.
Keep active worker code and approvals unchanged during implementation.

## Alternatives

React Flow offers rich workflow cards but adds React to the current plain-JavaScript dashboard.
Sigma.js targets large network exploration but needs more adaptation for task cards and ordered execution stages.
Neither replaces the selected Cytoscape.js 2D implementation.
Do not build a custom graph engine or a graphical workflow editor.

## Sources and visual references

These official sources describe library capabilities. They do not establish NUIAK integration performance.

- [Cytoscape.js documentation and layouts](https://js.cytoscape.org/)
- [Cytoscape Dagre extension](https://github.com/cytoscape/cytoscape.js-dagre)
- [Cytoscape interactive graph example](https://js.cytoscape.org/demos/colajs-graph/)
- [3D Force Graph source and API](https://github.com/vasturiano/3d-force-graph)
- [3D directed tree example](https://vasturiano.github.io/3d-force-graph/example/tree/)
- [3D expand-and-collapse example](https://vasturiano.github.io/3d-force-graph/example/expandable-nodes/)

Cytoscape.js core, the Dagre extension, and 3D Force Graph declare MIT licenses.
Retain required notices and inspect exact transitive dependencies when selecting package versions.
