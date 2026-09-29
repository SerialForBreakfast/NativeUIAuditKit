# Review-parallel tranche — 2026-09-28

Authorized: implement role-aware development evaluation, one-command immutable
revision→production crop QA, and offline retained recorder audit. No inference,
training, new capture, changes to open annotations, taxonomy or public Swift API.

## Contracts before implementation

Role admission is a separately approved, hash-bound `human-focus-role-admission-v1`
document. Partition every reviewed sample exactly once as candidate, auxiliary or
unresolved. Bind revision/crops and optional human completeness receipt. Enumerate
every frame with settled/disputed/unknown status and complete/incomplete/unknown
candidate coverage; require reasons for exclusions. Complete frames must be human
attested and have no unresolved sample. No inferred focusability from class names.
Roles remain distinct from detector classes. Only approved candidate frames with
one ground-truth focus can establish unique selection. Auxiliary and unresolved
samples never improve candidate metrics. No threshold sweep;0.85 is unchanged.
Wire new approval/protocol v2 through existing freeze/run/render; v1 stays supported.
Execution still needs its own existing maxRuns=1 model/runtime-bound approval.

One-command QA consumes an immutable revision, not mutable editor JSON. Validate
source snapshots; optionally validate a supplied completeness receipt, never create
one. Fresh output only; preserve staged failure receipts. Pending review blocks
qualification explicitly rather than manufacturing labels. Use existing cropper
and audit, with optional reuse of a verified existing crop report for offline replay.
No model argument, no automatic admission and no annotation writes.

Recorder audit consumes local retained schema2 metadata. Join action/dispatch/frame
by explicit IDs and hashes; no nearest-frame guess. Validate target/generation and
monotonic chronology. Report action outcomes separately from post-frame evidence,
pre-frame age, input overlap, declared settlement, missing links and repeated bytes.
Identical images do not prove no-op, and completed dispatch does not prove intended
focus. Timing is observed association latency, not UI settle ground truth. No model
or OCR inference; existing OCR metadata is not native focus identity.

Verification: generated positive/negative fixtures plus actual retained QA replay
and recorder CLI audit; legacy evaluator tests, offline Swift build/test. New
runtime/model execution approvals are not fabricated for these software tests.
