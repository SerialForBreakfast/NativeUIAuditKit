# IOS189 — resolution crossover complete; no promotion

Same216fit/96development/2400retained membership scored for each cell. Reused two
existing prediction sets, inferred only the two missing arms through the unchanged
exporter. All checkpoints/source/input/settings hashes validated. Explicit resolution
differences, not a false same-preprocessing comparison. No fitting or new labels.

| Train checkpoint / inference size | Retained AP50 | Page TP / FP | Fit leading / center / trailing |
|---|---:|---:|---:|
| Run022 /640 |.899967|58 /14|68 /72 /45|
| Run022 /1280 |.190626|19 /28|31 /34 /34|
| Run024 /640 |.886342|35 /21|29 /66 /14|
| Run024 /1280 |.343954|70 /158|69 /69 /59|

Each fit stratum has72images. Page support96. Retained38supported classes; three
absent classes remain unavailable. All original14gates reported per cell; no cell
passes them all. Raw per-class counts and exact216case transitions are sealed in
`artifacts/evaluation.json`, seal
`083aaadb372b01bbcaf9c3b073e662cbf5cb111f6e3dd7e451a1fbe052a3f8bf`.

## What this changes

Higher inference resolution alone strongly harms the640-trained checkpoint.
Run024improves at1280relative to022but remains far below the640reference. At640,
024recovers aggregate retention but loses page fit (0/31old misses recover,76old hits
regress). At1280,022recovers22/31old misses but loses108old hits; inspecting only
old failures would conceal that regression.024@1280recovers21and loses9, a useful
geometry signal but not a production detector. This does not establish that1280
can never work with a different training program; it rejects this fixed schedule.

Do not add more epochs automatically. Keep022@640reference and shipped models.
Next bounded diagnostic: coordinate-only page refinement from cached024@1280
proposals, preserving022classes/confidences and one-to-one matching. Reject ambiguous
matches and keep all other classes byte-identical. This tests whether the geometry
signal is useful without importing158extra page false positives; it does not grant
deployment or a new public API. Any eventual two-pass design must measure cost.

## Verification and independent outcomes

3new focused tests, prior16unchanged resolution/contrast/replay checks retained;
offline Swift build/142tests pass (`.build/crossover189-*.log`). Actual inference and
four-arm report CLI exit0. Additional inference483.057seconds, no concurrent MPS
training. Outputs remain under512MiB and ignored; no raw weights staged or Git writes.

Software passed; original roles unchanged (no new admission); local inference/
report integration passed; model gates failed and no production promotion. TTR
coordination not applicable to this local iOS result. Companion188completed native
contrast specification; exact producer source still blocks its24-case intake only.
