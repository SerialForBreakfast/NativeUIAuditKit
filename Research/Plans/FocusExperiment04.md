# FOCUS-EXPERIMENT-04 — changed-data comparison

## SYN-10 implementation scope — 2026-10-01

Add a separate `focus-native-body-full-fit-v1` execution protocol, not an executable
reinterpretation of the diagnostic assembly. Revalidate the sealed native assembly,
reuse both FDR021 baseline caches (original features plus reviewed-human extension),
append only exactly admitted native controls and preserve evaluation order, labels,
selection and optimizer. Ordinary dataset loading must reject this protocol.

Encoding approval binds the pre-cache protocol, exact output directory and explicit
limits: at most300seconds, at most2048new controls, fixed32-image batches and a
bounded tensor output size. The batch bound limits input tensors, not total process
memory. Record end-of-encoding MPS allocation snapshots, not peak-memory or hard
memory-limit claims.
The deadline is cooperative (checked around batches and before publication), not
an operating-system kill timer for a hung framework import or accelerator call.
Reuse the existing frozen encoder implementation and normalization. Refuse changed
encoder state, receipt membership, tensor dimensions/dtypes/labels, nonfinite values,
cache hashes or feature digest. Training never silently re-encodes absent features.

After encoding, a new protocol binds that cache and needs a separate one-run
approval and experiment-log entry. Tests may use generated tensors and fake encoder
dependencies; they do not authorize actual inference, admission or training.
Retained unadmitted data exercises the blocked CLI path. Current human-review and
source-role decisions remain pending, independent of software readiness.

Status: configuration proposal prepared for review, 2026-09-30 PDT.
Execution blocked on eligible changed corpus and exact run approval. No run ID is
allocated and no approval file is created. This assignment prepares the experiment;
it does not launch training, encode new features or operate TTR.

## Question and comparator

Does coverage-driven native training data improve real-screen focus detection with
the existing representation? Compare against FDR021 selected update775, not an
unchanged rerun. Baseline evidence:
[FDR021 handoff](../../reports/work/FOCUS-REVIEW-CONTINUE-16/execution-handoff.md).
The baseline head requires its pinned encoder; it is not a standalone model.

Baseline at fixed0.85:16/27focused controls,3/288false positives,12/14unique-correct
complete frames,0wrong/0multiple-focus,18/18retention. Artwork2/12hits with3FP;
buttons3/3with0FP;tabs2/3with0FP;rows7/7with0FP;other2/2with0FP.
These are development results, not independent qualification.

## First arm: data only

| Setting | Proposed binding |
| --- | --- |
| Inputs | Existing986training controls plus explicitly admitted new training members; exact additions/count pending FOCUS-CORPUS-03 |
| Evaluation | Exact315development and18retention IDs, labels, pixels, weights and frame completeness from FDR021;14complete frames only |
| Representation | Same pinned ImageNet MobileNetV3-small frozen encoder,576features; frozen batch norm; fresh577parameter linear head |
| Initialization | Seed42, fresh head; no FDR021 warm start |
| Pixels | Existing production16% expansion,256×256, straight-RGB contract and existing ImageNet normalization; no center crop or augmentation |
| Optimizer | Existing AdamW,lr0.01,weight decay0.01 |
| Updates | At most1,000 full-batch head updates; existing evaluation every25updates |
| Early stopping | Preserve existing five-consecutive-confident-fit rule and its implementation |
| Budget | Head training at most300seconds, as FDR021; no automatic retry or deadline extension |
| Compute | Resident Apple Silicon/MPS and pinned local environment; no CUDA/cloud/download assumption |
| Features | Reuse verified unchanged feature caches; new members require separately bound encoding receipt and approved encoding budget |
| Selection | Existing minimum-balanced-real-BCE guarded selection, earliest exact tie; no threshold sweep |

Full-batch size is the admitted training count, not hardcoded986. If expanded
features cannot fit within the existing mechanism, stop for a separately reviewed
batching change; do not silently alter the experiment. Encoding time/memory/output
limits must be set from exact admitted membership before execution approval.

Preserve the native80%/human20% loss allocation and current within-source weighting
algorithm. Recompute weights deterministically from training membership only, and
report the changes: adding examples changes effective weighting, so this compares
a data-plus-weighting intervention, not a proven causal effect of pixels alone.
The existing reviewed-human extension is not presumed to admit arbitrary new native
exports. Verify the actual assembly/feature-cache path accepts their provenance;
any required adapter implementation/tests must precede execution, not bypass admission.

## Predeclared comparison decision (proposal, not a release gate)

Use the existing checkpoint selector unchanged. Evaluate its selected checkpoint
against FDR021 with these proposed additional **post-selection** acceptance criteria:

- Artwork focused hits strictly improve above2/12.
- Overall true positives at least16/27; false positives at most3/288.
- Unique-correct complete frames at least12/14; no wrong or multiple-focus frames.
- Retention remains18/18 under the existing retention definition.
- Buttons,tabs,rows,other do not lose true-positive counts or gain false positives
  relative to the baseline values above.

These proposed development comparison criteria require approval with the run
contract; they neither change existing production gates nor claim significance.
Do not search other checkpoints after a selected candidate fails these criteria.
Preserve rejected outcomes and stop; no automatic second arm. Report both aggregate
and per-control gains/regressions, no-focus counts, BCE, timing and peak memory.
Check exact prediction membership before computing any comparison. Incomplete frames
remain unavailable for full-frame accuracy, not treated as easy negatives.

## Data and execution checklist

1. FOCUS-CORPUS-03 supplies exact changed membership, source/layout reservations,
   dispositions, native labels, integrity and production crop QA. No matched24 or
   protected challenge conversion. Unknown independence remains explicit.
2. Record the admitted addition and weighting deltas, native/human counts and family
   coverage. Reject zero-change assembly. Check related-source and duplicate overlap.
3. Bind exact encoder/cache/runtime identities and new encoding limits. Verify actual
   importer→assembly→encoding→trainer integration with positive and negative tests;
   run required offline checks for any implementation changes.
4. Freeze a new executable protocol and fresh output path; preflight must pass data
   and configuration checks. Historical approval cannot authorize the new protocol.
5. Present exact members/counts, configuration, budgets and proposed decision rule
   for run approval; log the next available experiment ID before executing once.
6. Preserve selected/terminal predictions, errors and rejected trials. Pass/fail the
   comparison without changing rules after observing scores. Export is separate.

SYN-10 supplies the native-assembly execution adapter, bounded encoding interface
and executable protocol software; actual data/encoding/run approvals remain absent.
Current missing bindings: exact eligible members with sampled geometry/source-role
acceptance, approved encoding limits/cache receipt, and one-run approval.
Software completion does not satisfy them. A smaller explicitly approved
development experiment need not claim production corpus qualification; it still
requires eligible changed data and cannot waive the existing release gates.

## Later arms, not queued for automatic execution

Only after the data-only decision: propose either expanded context or partial
backbone fine-tuning, one factor at a time, on identical membership and evaluation.
Context changes require separate preprocessing/crop parity and cache identities.
Backbone changes require separate initialization, optimizer, memory and time budgets.
No35%margin, end-to-end training or unified detector replacement is adopted here.

Coordination is not applicable to this preparation: existing TTR corpus request
already specifies the missing producer work. No additional peer action or runtime
test is requested. FDR021 observer testing remains a separate assignable lane.
