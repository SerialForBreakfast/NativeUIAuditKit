# Optional NUIAK shadow integration — validation addendum 110

This is a portable **synthetic conformance harness**, not a new TTR wire schema,
model delivery, execution attestation or training corpus. Keep TTR's existing
capture, prediction, independent-label and evaluation records; map them into these
normalized test observations. No public NUIAK library API change is required.

## What DTM025 means

DTM025 estimates focused **control identity change** from ordered screenshots.
It is not merely highlight-box displacement or arbitrary image change. NUIAK's
`focus_direct_transition.py` compares observed fixture focus IDs, and its reviewed
Settings path compares matched controls; `evaluate_collection102.py` uses the same
identity relation. The training collector's native callbacks are evidence, not
model inputs. The delivered artifact, preprocessing and thresholds are unchanged.

- Stationary highlight + scrolling + changed focused control: target **changed**.
- Same focused identity with animation/content changes: target **unchanged**.
- Uncertain identity/association: label **unknown**, not unchanged.

The eight reported scrolling cases are currently **native-hint disagreements**, not
eight independently verified visual-model errors. Confirm action/frame association,
stable control identity (not recycled/transient accessibility IDs), and review
before counting misses. If confirmed, unchanged predictions are misses: do not
relabel them to make DTM025 pass. Stationary-highlight scrolling remains unqualified;
the images may not always contain enough information to resolve identity reliably.
Neither model may drive navigation or provide its own ground truth.

## Two independent optional capabilities

FDR021 is single-frame, candidate-crop visual focus scoring (production 16% expansion,
256×256 crop); DTM025 is ordered full-frame change-only scoring. DTM025 does not
localize the destination. Neither capability should make the other mandatory.
Use their existing pinned delivery manifests, not a latest-model fallback.

TTR-owned acceptance matrix:

| Case | Required evidence |
| --- | --- |
| Module absent; flag off | Core app builds/runs; zero pixel reads, model loads and inference; navigation unchanged |
| Module present; flag off | Same zero-access behavior; no eager model initialization |
| Explicit enabled; module/model missing | Typed unavailable outcome, not an empty/unchanged success; core app remains usable |
| FDR021 only / DTM025 only / both | Separate lazy capability initialization and independently identified results |
| Bad bytes, stale observation, queue saturation, cancellation | Typed failed/stale/dropped/cancelled records, bounded queue of8; no navigation authority |
| Scored | Exact artifact/preprocessing/threshold identities; prediction and truth remain separate |

The Python optional-module checks validate reported observations only. TTR must
also exercise actual builds without its optional module, initialization/access spies,
failure injection and identical before/after navigation traces. Live hooks need
their own evidence; retained replay does not prove subscription behavior.

## Feedback and accounting

Join predictions to separately reviewed labels by exact case/action, both observation
IDs and both image SHA256 values. Never pass a reviewed label or native focus hint
into model inference. Preserve raw probability and pinned decisions: changed≥0.85,
unchanged≤0.15, otherwise uncertain. Probabilities are not calibrated confidence.

Report all cases, confident reviewed decisions, correct decisions, abstentions,
missing truth, native-hint disagreements and each execution failure separately.
Accuracy on confident reviewed decisions is **selective accuracy**, not all-case
accuracy; always include abstention/coverage counts. Failed/off/dropped inference
is not a negative prediction. Native-hint agreement is not independent accuracy.
Every harness result remains training-ineligible and non-independent, even when a
caller marks its input non-synthetic. Admission/review is a separate process.

## Run locally, without model/device/network dependencies

Extract the named archive into a new project-local directory, verify each member
against `manifest.json`, then from that directory (Python3.9+):

```sh
mkdir -p .build
env PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build" python3 -m unittest test_shadow_feedback_contract
env PYTHONDONTWRITEBYTECODE=1 python3 shadow_feedback_contract.py --input synthetic-cases.json
```

Compare parsed output to `synthetic-expected.json`. Tests include rejected corrupt
bindings, fabricated failure-as-unchanged, unsupported model/version, invalid
probabilities, duplicate JSON keys, navigation interference and off-mode access.
`normalize_cli` also verifies existing DTM025 request/reply metadata before joining
separate labels; it does not independently verify screenshot bytes or review quality.

Return source/build IDs, capability matrix results and exact executed artifact hash.
Keep private images local unless separately approved. A tiny permitted byte-bound
export can support NUIAK independent intake later. This request grants no capture,
training, promotion or screenshot-egress authority.
