# HUMAN-BENCHMARK-02 — development admission and comparison complete

2026-09-29. Approved steps1–2 completed using existing admission, production crop,
CPU inference and metric components. No new evaluator/library code, training,
capture, export or promotion. **Do not release FDR-010 for autonomous use.**

| Outcome | Evidence |
|---|---|
| Software verified |23 focused tests pass; actual admission and155 predictions per model; metric replay exact; five real-artifact negative checks pass |
| Data eligible |New frozen development benchmark,8 human-reviewed frames,138 candidate controls and17 auxiliary annotations; no training or independent qualification eligibility |
| Integration qualified |Reviewed revision→production crops→CoreMLCPU/PyTorchCPU comparison completed with exact identities; not a TTR runtime or export-parity claim |
| Model gate |Not assessed as a production gate; FDR-010 misses all8 positives, no promotion justified; shipped unchanged |

## Result at fixed0.85 — identical reviewed controls

| Candidate metric | Shipped FocusRing | FDR-010 epoch29 |
|---|---:|---:|
| Focused found /8 |6|0|
| Missed focused controls |2|8|
| False positives /130 unfocused |99|2|
| Recall |75%|0%|
| Precision |5.71%|0%|
| False-positive rate |76.15%|1.54%|
| Auxiliary false positives /17 |16|0|

FDR-010's92.75% candidate accuracy is dominated by negatives; it does not find
focus. Shipped retrieves more positives but cannot reliably discriminate competing
controls. This is focus classification using human boxes, not detector recall,
end-to-end navigation success or a real-world population estimate.

| Control stratum | Positive/negative support | Shipped TP/FP | FDR-010 TP/FP |
|---|---:|---:|---:|
| Artwork/collection items |6 /74|5 /50|0 /2|
| Rows/sidebar controls |2 /52|1 /46|0 /0|
| Buttons |0 /4|0 /3|0 /0|
| Tabs |0 /0|Unavailable|Unavailable|

Button positive recall is **unavailable**, not zero. This supplement provides
button hard negatives, not proof of positive button transfer. Preserve reviewed
classification labels; the compact sidebar remains listRow as annotated.

## Per-context evidence

Each row has one human-focused target. Scores are shown as shipped / FDR-010;
FP counts exclude static auxiliary annotations.

| Frame | Context | Focused score | FP counts |
|---|---|---:|---:|
|875|Circular avatar|0.99805 /0.00300|4 /0|
|839|Expanded sidebar|1.00000 /0.00295|13 /0|
|742|First Top Stories card|0.03131 /0.35518|13 /0|
|614|Compact Home/sidebar amid tall posters|0.25269 /0.00016|11 /2|
|653|Ranked Lioness card|1.00000 /0.05263|11 /0|
|572|Landscape continue-watching card|1.00000 /0.00956|15 /0|
|771|Text-only channel tile|1.00000 /0.00364|23 /0|
|479|OS Search category tile|1.00000 /0.00138|9 /0|

Watch Now is unfocused in742, as explicitly confirmed by the maintainer. Its
persistent outline is a useful hard negative, not an excuse to reverse the label.
FDR-010's two false positives are614:new-3/new-4, bright portrait artwork; scores
0.92148/0.98176. Descriptive rankings show the true focus trails competitors in7/8
annotated subsets for FDR-010. This is not a tested alternative selection policy.
Shipped ties at1.0 in several frames; tied top rank must not imply unique selection.

## Admission and completeness decision

- `admission-v2.json` uses existing human-focus-role-admission-v1, references exact
  human revision192241Z-aabb2be6 and production QA-supplement-02 hashes. Source
  diagnostic manifests and review snapshots remain immutable/ineligible for training.
-138 annotated collectionItem/listRow/primaryButton controls are the candidate
  population.14 labels and3 decorative imageViews are auxiliary negatives. All155
  scored and accounted; no unresolved scores, silent filtering or failed predictions.
-Human settled/content approval is verified from snapshots; original producer
  postInputUnverified observations are retained, not relabeled as native evidence.
-No exhaustive-candidate attestation exists. Some visible clipped/edge controls
  are not annotated (for example479 Workplace Comedies). Full-frame selection is
  unavailable for all8, with individual reasons in admission. This does not block
  supported crop metrics and is not an invitation to burden the reviewer with
  completing every peripheral control now.
-Whole session E93B12DA-9358-4FD6-91F2-1B42AD8C9329 reserved as development-exposed
  in `source-reservation.json`; future assembly must explicitly consult it. No
  claim of a newly installed global reservation registry or training admission.
-Role audit checks644 current training/retention samples,1344 reserved samples and
  20 protected metadata rows; no exact-content/session matches detected. Eight
  historical pixel references unavailable; ancestry remains unknown, not independent.
  Protected challenge pixels were not viewed or scored. No exact frame-pixel overlap
  with32 prior reviewed frames. Seven new screens are Paramount+, one OS Search;
  screenshots and different content do not establish independent source families.

## Prior real benchmark context — reused, not rerun

`retained-real32.json` revalidates four retained protocols and model scores through
the existing FDR-010 adapter.362 scores/model,315 supported settled candidate crops.
The prior24-frame set remains shipped8/19 positives with30FP versus FDR-0103/19
with3FP; prior Home/Photos/Settings8 remains4/8 with11FP versus0/8 with4FP.
All original exclusions remain. Do not compare these different corpora as a numeric
improvement delta or pool them into an independence/qualification claim.

## Next assignment — fix source transfer before another run

1. **Receive/review the newly published bulk-corpus revision3 contract.** TTR status
   observed19:31:25Z advertises6f1093ee source378961bytes and training-only family
   proposal. Not downloaded/integrated in this evaluation tranche. Reconcile schema,
   current-runtime capability and role reservations before approving dispatch.
2. **Bind the existing96-pair matched-contrast target to measured failures.** Keep
   source-cleared artwork, native-button/native-image comparison, two backgrounds
   and two geometry profiles matched. Include circular/avatar, landscape/progress,
   portrait/ranked and text-dominant content across that design where supported;
   producer must report unsupported recipes, not silently substitute blank tiles.
   Preserve same-control focused/unfocused observations, genuine native focus,
   visible competitors, persistent-outline negatives and selected-parent cues.
   This remains a collection target, not a new gate, another pilot quota or approval
   to capture. Broader production scheduling can proceed independently of new weights.
3. **Representative selection, not retention alone.** Train only after a separately
   approved role-bound corpus/selection contract includes artwork and sidebar/row
   transfer; preserve all reviewed real sessions for regression and the18/18 retention
   floor. The reviewed supplement must not become training data to improve its score.
   Capture/assembly/preflight is the next substantial tranche; no unchanged retrain.

Evidence supports a transfer/selection problem; it does not isolate geometry,
initialization, brightness or crop stretching as its cause. Native fixtures previously
passed18/18 button/tab/row positives while these real positives all fail FDR-010.
Lower thresholds alone are not justified by the poor within-frame target rankings.

## Verification and reproducibility

`protocol.json` SHA256 fd5acf5ed3d74a1cb5da0f29f7ea0d4317e3b0c7f75bba19cacee8602977c140
pins review/crops, model selection, code, runtime, admission, prior review and role
inventories before inference. Shipped9e5ba294…; FDR-010775c3197…, actual epoch29 CPU
receipt. Production source37bfaa55… and helperc099d89f… unchanged after execution.
Python3.12.9/torch2.7.0/Pillow11.3.0, resident focus-export-01 environment; all task
caches/temp project-local. Existing e.infer receives explicit shipped/fdr010 roles;
legacy fdr009-only CLI was not misused or its role silently renamed.
Observed scoring loops3.76s CoreML and4.41s PyTorch are different pipelines, not
latency parity. `started.json` pins one execution; results and postflight complete.

Initial admission preflight rejected an omitted diagnostic-policy flag before any
inference. Rejected admission.json is preserved; valid admission-v2.json explicitly
retains h.FLAGS. Original review flags were not changed to bypass the check.

23 tests: `PYTHONPATH=scripts .venv-review/bin/python -m unittest
test_human_focus_evaluation test_human_focus_roles test_human_review_audit`.
`verification.json` adds actual-input rejection of training-manifest admission,
unattested completeness, missing/duplicate/nonfinite predictions. Existing tests
cover changed hashes/policy, empty supported subsets, ties and partial failures.
No implementation source changes; no full Swift rebuild needed for artifact-only
execution. Previous unrelated dirty source files remain untouched.

Replay without inference from repository root:

```python
import json
from pathlib import Path
from focus_representative_validation import summarize
p = Path('reports/work/HUMAN-BENCHMARK-02')
protocol = json.loads((p/'protocol.json').read_text())
for name in ('shipped', 'fdr010'):
    result = json.loads((p/(name+'.json')).read_text())
    assert summarize(protocol['samples'], result['predictions'],
                     protocol['roleAdmission']) == result['metrics']
```

Set PYTHONPATH=scripts/PYTHONDONTWRITEBYTECODE=1. Reports include all errors with exact
IDs and hashes, per-context scores, numbered miss/highest-FP sheets and the visually
checked `report/focused-overview.png`. Labels and native/source records unchanged.
No owned inference process remains. Benchmark admission/comparison complete; broad
qualification and missing candidate completeness are explicit limitations, not a
reason to repeat annotation or claim the whole system is ready.

[Coordination](coordination.md): reviewed-artifact metadata receipt and actionable
failure follow-up published/read back in owned shared status/response. Peer receipt
of this new response remains unverified; independent evaluation is complete.
