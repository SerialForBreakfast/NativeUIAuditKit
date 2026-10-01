# SYN-05 offline tranche

Completed for review,2026-09-30 PDT. No capture, model execution or training admission.

## What works now

- One local CLI drives existing native intake → production crop QA → sampled/exception
  annotation preparation → Markdown geometry sheets. No new annotation application.
- Immutable per-bundle attempts retain interrupted/failed work. Completed receipts
  verify source and generated-output hashes before reuse. Changed plan, implementation
  or inputs require a new output root, not silent continuation under old identities.
- Human JSON edits and review revisions in the dedicated audit workspace are never
  overwritten on resume. Original producer bytes and current SYN-03 human workspace
  remain untouched. Completed generated crops/reports are checked, not regenerated.
- A single-writer lock blocks concurrent execution. A process killed before cleanup
  can leave `active.lock`: an operator must verify no worker is active before removing
  that exact lock. The tool does not steal locks or kill processes automatically.
- Resource limits remain bounded:32bundles,128pairs/bundle,256frames/bundle, flat
 32MiB/member inputs, existing crop batching and2GBfree-space reserve. This is the
  bounded local replay lane, not an unbounded production campaign service.

## Run or resume

From the repository root, the same command resumes the same frozen plan:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/fixture_offline_pipeline.py \
 --plan reports/work/SYN-05/replay-plan.json \
 --output reports/work/SYN-05/artifacts/final-replay
```

Exit0 means offline review preparation completed, **not geometry acceptance**.
Exit2 reports blocked/rejected work. Successful other bundles remain reusable.
Failed attempts retry into a new directory; source corrections need a newly named
plan/output. Inputs are named local bundles, not URLs or executable peer requests.

The plan is a versioned local format: bundle IDs/paths, protected metadata, optional
verified catalog/root and fixed sampling parameters. It does not invent a TTR protocol.
Campaign-level budget evidence remains in the prior verified SYN-03 campaign report;
this runner handles delivered case bundles, not unattempted runtime dispatch.

## Observed evidence

| Check | Result |
| --- | --- |
| Retained live delivery |3bundles/5captured pairs/10frames,60/60crops |
| Repeat execution |3completed bundles reused; zero batch.prepare/recrop calls; receipt hashes unchanged |
| Human burden |1unique sampled/exception frame per bundle in this replay; no request to repeat prior human review |
| Geometry |10full-frame paired overlays; blue wrapper versus orange annotation proposals; body role explicitly unavailable |
| Catalog |30recipes,60mapped slots,14theme/seed-normalized layout/content signatures,1conservative connected source group |
| New tests |11retry/grouping tests: interrupted attempt, failed bundle isolation, changed files/plan, output tamper, lock/capacity, protected input, duplicate plan, source grouping and human-edit preservation |
| Broader checks |37fixture tests;136human tests; Swift build;120Swift Testing+14XCTest; diff check |

Evidence: `artifacts/final-replay/status.json`, `resume-proof.json`, per-bundle
`completed.json`, `fixture-tests.log`, `human-tests.log`, `swift-build.log`, `swift-test.log`.
Early development replay is retained separately; final-replay is the integrated result.

## Source-role recommendation

Keep the current connected group together on the **training-candidate** side only,
subject to subsequent geometry and admission checks. Do not use its theme variants
to fill independent validation slots. No role was reserved or eligibility changed.
Shared infrastructure is conservative linkage, not proof of identical screenshots.
Still missing: explicit structure/content ancestry against retained examples and a
reviewed independent validation group.14signatures describe source configuration,
not14independent sources or14proven rendered layouts.

## Geometry gate and next step

The blue and orange boxes currently coincide because the producer provides wrapper
geometry, not a bound rendered-body role. The visible enlargement mismatch remains
clear on the second artwork tile. Uniform boxes alone do not prove a defect on
no-growth controls. No automatic pixel-based acceptance, OCR labels or guessed scale.
Optional edge/Vision assistance is not added in this tranche; the explicit visual
gate and native repair request remain authoritative.

Next is binding TTR's concrete rendered-body schema once supplied and replaying it
through these same checks, then a small human spot-check. Capture dispatch, broader
rendered-family proof, independent split acceptance and training remain separate.
Software verified; diagnostic integration verified; data admission blocked;
model gate not assessed. Local work does not change TTR's pending geometry request,
so no additional shared-status publication or runtime operation was needed.
