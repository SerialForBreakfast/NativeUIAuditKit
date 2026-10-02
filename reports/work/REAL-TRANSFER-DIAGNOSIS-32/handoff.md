# Transfer32 — completed, with an actionable coverage diagnosis

The maintainer's six identity/state confirmations are pinned in
[authorization](scored-clipping-aware/authorization.json). Existing labels stay
unchanged; development comparison only. Model-workflow skill fixed model identity,
membership, thresholds and native cropping; worker workflow added the independent
brightness comparison and training-coverage audit rather than stopping at scoring.

## Results

| Test | Measured outcome |
| --- | --- |
| Six new pairs, frozen FDR036 | 6/12correct;0/6focused detected at0.85 |
| Advisory0.15/0.85 | 6correct,5wrong,1uncertain |
| Four clipped-context row pairs | 4/8correct,0/4focused detected |
| Two contained tab/button pairs | 2/4correct,0/2focused detected |
| Home baseline reproduction | max score difference1.1921e-7 |
| Hide Home neighbor bodies | both negative false positives remain:0.92259/0.88984 |
| Hide Home target bodies | all4scores below0.008; all become unfocused |
| Fixed mean-brightness ordering | 8/8pairs correct versus model5/8 |

RunPID27827,2.716seconds,24crops. [Exact scores/inputs](scored-clipping-aware/result.json),
[readable results](scored-clipping-aware/result.md). Original geometry preflight
stopped before inference; [reason and correction](preflight.md) retained.
Four rows lose7–8%of requested context at the right edge; all target bodies remain
contained. The normal live advisory gate still rejects clipped context.

## What this means

The current model does not transfer reliably even to these correctly reviewed
controls. Neighbor-body masking lowers Home scores but does not repair false
positives. Target appearance strongly affects predictions, but masking creates
unnatural inputs and does not separate artwork, shading, size and shadows causally.
Both states use the same union mask; target pixels are protected in neighbor masks.

[Coverage audit](coverage-verified/coverage.md) verified all1,250source records:
1,000training pairs, all artwork-row layouts. Training body width/height is
1.084–1.761. Five new wide controls are7.140–11.049. Home is in-range, so shape
coverage cannot explain the entire failure. Native renderer/control style remains
a distinct target for investigation. Metadata provenance is verified, not new pixel
requalification of the whole corpus.

Brightness ordering is useful evidence for a paired supporting signal, not a new
deployable detector: it sees both known states, has only8related positive-change
pairs, and has no no-op/content-change negatives here. No tuning was performed.

## Verification

18real-reference/mask/coverage tests plus6existing native-transfer gate tests pass.
Offline Swift build passes;14XCTest and120SwiftTesting tests pass. Logs under
`.build/debug-output/diagnosis32/`. Actual CLI/MPS/production-crop path executed.
Software passed; data eligible for approved diagnostic only; integration/model
release qualification remains open.

## Producer state and next substantial tranche

TTR's22:06:11Z publication reports new composition4/grid-density-v1 working-tree
support,2native appearance pairs and6controlled transitions. This is producer
evidence, not local runtime qualification. It acknowledges tracking30's binding
request; field agreement remains pending. Exact earlier ACC-MAP report receipt
cleanup is now acknowledged. Source publication through Git precedes local build.

Consumer packet REAL-TRANSFER-DIAGNOSIS-32 and request
`nuiak-20261002-diagnosis32-rendered-coverage` published at22:10:24Z to
`/Volumes/SharedStatusFile/nuiak/status.yaml`; unique-key readback and preservation
of unrelated content passed. Request asks for existing recipe/source capability
mapping, not new capture/build delivery. Peer acknowledgment of this new request
has not been observed. Model release gates were not reassessed.

Recommended next outcomes:
1. Test a guarded paired-brightness baseline on existing genuine Settings moves,
   no-ops and content-change negatives, compared against the existing pixel rule.
2. Inspect/build the published TTR density source locally when available; qualify
   matched native Home style/density examples and native wide controls. Preserve
   ordinary bounds/profile bindings. Source commit/push is sufficient; no build request.
3. Run a small matched training comparison only after coverage/pair qualification,
   with related layouts held together and this failure-driven set kept development.

No further identity review is required for the six pairs. New capture/admission
and new training membership require their applicable scope; existing diagnostic
approvals do not silently turn these real frames into training data.
