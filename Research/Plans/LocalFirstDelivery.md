# Local-first delivery: five substantial tranches

Established 2026-09-30 from the maintainer's approved breakdown. This is the scope
and acceptance contract, not a second task board. Execution state/ownership lives
in [Tasks.md](../../Tasks.md). Tranche 1 is complete; the maintainer assigned tranche 2
next, including bounded retained-image inference, CLI/MCP implementation and offline
verification. No training, capture or candidate promotion is included.

## 1 — Workflow and ADR reconciliation (LOCAL-FIRST-01)

Scope: ADR-0012 through ADR-0015, operational instructions, current snapshot and
queue. Correct stale baselines and unsupported claims; separate design decisions
from hypotheses and execution authority. Adopt one concise report, automatic batch
checks and asynchronous TTR intake. No software, capture, inference or training.

Acceptance:
- All four ADRs distinguish verified evidence, proposed work and non-claims.
- AGENTS, WorkerWorkflow, worker skill and iteration guidance agree on proportional
  reporting while retaining automated data, split and parity safeguards.
- One queue gives the sequence, dependencies, scope and measurable completion tests.
- Documentation link/content/diff checks pass; no package/model run is needed.

## 2 — Existing-model CLI and MCP (LOCAL-TOOLS-02)

Depends on the reconciled contract, not a TTR build. Implement doctor, scan and
scan-batch over NativeUIDetectionRequest/session, then a thin stdio MCP wrapper.
Assignment must explicitly include bounded retained-image inference for real smoke
and timing checks; no training, new models or navigation. Missing resident model
dependencies block runtime checks, not deterministic interface tests.

Acceptance:
- Actual CLI calls use production preprocessing, OCR, focus and audit logic.
- Versioned output records model identity, capabilities, uncertainty, timing and
  every batch input's success/failure. Logs do not corrupt MCP protocol output.
- Tests cover valid/corrupt/missing inputs, unavailable models, unauthorized paths,
  malformed requests and batch partial failures; strict errors are defined, not
  inferred from every heuristic warning.
- A retained-image runtime smoke and cold/warm timings are recorded, separately
  from mocks. Focused tests and offline Swift build/test pass; usage examples work.

## 3 — Coverage-driven focus corpus (FOCUS-CORPUS-03)

Focus is the model priority. Inventory existing pixels, labels and reservations
before generating more. This work need not wait for CLI completion if separately
assigned, and local preparation does not wait for TTR delivery. Confirm native
capture target, runtime and bounded generation scope before execution.

Acceptance:
- Coverage matrix separates present, absent and unsupported buttons, tabs, artwork,
  rows and keyboard cases, with selected-but-unfocused parents and hard negatives.
- Source/layout relationships determine splits before generation. Development,
  retention and protected challenge roles are preserved; missing independence is
  explicit, not silently eligible.
- Native focus/geometry correlation, settling, image integrity, duplicates and
  production crops are checked automatically for every admitted member.
- Representative recipes and exceptions receive visual review; no manual tracing
  of every automatically verified control. Requested variations are checked in pixels.
- Corpus counts and diversity are measured against a frozen coverage contract;
  5,000+ pairs is a proposed collection target, not a substitute for existing gates.
- Final output is a reproducible assembly with complete accepted/rejected/blocked
  accounting and a trainer preflight. No training launched in this tranche.

## 4 — Controlled focus experiments (FOCUS-EXPERIMENT-04)

Depends on eligible corpus and a separately approved exact run contract: initialization,
seeds, membership, optimizer, compute/time cap, selection rule, retention requirements
and predefined improvement criteria. No guessed numeric release thresholds.

Acceptance:
- Preserve FDR021 as baseline; first compare changed data with the same representation.
- Isolate subsequent context and partial-backbone arms, with versioned preprocessing.
  Do not perform an unbounded sweep or replace the production crop contract.
- Use identical real development/retention membership and metrics. Report per-stratum
  support, misses, FP and unique-correct/wrong/no/multiple-focus decisions, plus MPS/CPU
  time and memory. Incomplete sets cannot establish unique-selection accuracy.
- Select only if predefined criteria pass. Otherwise hand off a rejected hypothesis
  and next decision; no automatic retraining, promotion or final-test reuse.

## 5 — CoreML and TTR observer delivery (FOCUS-DELIVERY-05)

Depends on a selected candidate and separately scoped export/runtime testing.
Local export/parity can proceed independently; TTR loading proof is a genuine
consumer dependency. Preserve the working handoff flow and shipped rollback.

Acceptance:
- Pin complete model artifact, preprocessing and runtime; pass production input and
  score parity with documented tolerances and decision-flip accounting.
- Explicit candidate selection rejects unsupported contracts; shipped/default path
  and rollback remain testable.
- Verify TTR's actual loaded identity and observer results on agreed cases, not just
  resource presence or producer acknowledgment. Record limits and failure evidence.
- Report software, data eligibility, integration and model qualification separately.
  Observer delivery is not production promotion or autonomous navigation approval.

## Deferred research and dependency rules

ADR-0014 hierarchical iOS and ADR-0015 unified-detector research are not prerequisites
for these tranches. No threshold relaxation, taxonomy rewrite or new hardware is
implied. Capture does not wait for a better model; training does wait for eligible
data and approved experiments. Producer outage blocks only producer-dependent work.
Use one concise evidence report per tranche, with links to unchanged evidence.
