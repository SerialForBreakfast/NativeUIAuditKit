# Approved human development comparison

2026-09-28. Maintainer: “I approve it”, referring to
Research/Plans/HumanFocusAdmissionDecision.md. Owner: current NUIAK review-tool worker.

One execution of shipped FocusRing CoreML CPU versus selected FDR-009 epoch3
PyTorch CPU.113 human-reviewed controls,8 Office frames,2 explicit Photos pairs.
No training use, training run, capture, export, promotion or protected scoring.
The entire correlated session is reserved as development regression evidence.

`approval.json` pins revision/crops, ordered membership, human/source binding,
exact model identities and the single output directory `comparison/`.
`protocol.json` additionally pins code/runtime and the actual role-index audit.
Protocol seal: `85f7f64644044206ace027ababdd97ca35d3cad4d529b701b0a0c92c234b3f0f`.
The exclusive `approval.started.json` marker prevents relaunch with that approval.

Runtime: resident focus-export-01 Python3.12.9, torch2.7.0, numpy1.26.4,
Pillow11.3.0; two CPU threads for PyTorch, batch32; shipped CoreML cpuOnly with
production16-item/80M-pixel batching. Identical retained crop-helper/source/host
identity,16% expansion,256×256, fixed0.85 threshold, original human boxes.
The existing helper returns probabilities in infer mode, not PNGs: crop identity
is bound through unchanged production code/helper and prior actual crop-QA evidence.
No latency/export-parity assertion between these backends.

Configured logs, caches and temp are project-local. No installations/downloads or
device services. Required offline Swift build/test uses its established scoped host
execution context; model execution also uses a scoped host invocation. No security
changes, HOME overrides or external dataset writes.

Coordination: not applicable; no TTR request or contract changed by this local test.
