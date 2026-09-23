# APPEAR-B1 evaluation reservation correction

2026-09-23; NUIAK architect. Integrated offline scope complete for review.

| Outcome | Result |
|---|---|
| Software verified | Passed:59 affected Python tests and offline package checks |
| Data eligible | Not assessed: no new independent evaluation data |
| Integration qualified | Synthetic assembly/trainer-preflight only; new TTR families not qualified |
| Model gate passed | Not assessed; no inference/training/export/promotion |

## Delivered

Research contract updated first; existing adapter now requires evaluation reservation
v2 to bind the exact source record and canonical source-row SHA256. Old reservation-v1
evaluation inputs reject explicitly. No actual evaluation corpus existed under v1;
the sealed real B1 protocol has no evaluation entries and remains unchanged.
No trainer/cropper duplication or producer-wire change. Existing lineage, source
eligibility, prior-use and two-independent-group checks remain in force.

Regression tests demonstrate changed membership, changed source, reused declaration,
old version and ordering invariance. Complete synthetic inputs exercise existing
assembly and trainer preflight, exclude challenge rows from training loaders, and
retain explicit launch authorization. The independent reuse/leakage tests still run
after deliberately resealing synthetic reservations, proving binding does not replace
those guards. Existing source-row validation is reused, not bypassed for real intake.

Changed `scripts/focus_appearance_experiment.py`, its existing tests and linked
research/queue documents. Preserved pre-existing dirty work, data, historical reports,
models and other packets. Real B1 corpus evidence is reused from its parent handoff:
no evaluation rows were added, so rerunning the unchanged multi-minute corpus audit
would not test this new evaluation-only branch.

## Verification

Approved Python environment: focus-export-01, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONPATH=scripts`; no model import or execution.

- `python -m unittest test_focus_appearance_experiment -v`: exit0,11 tests/1.076s
  in focused-tests.log (before final additional reuse/order test).
- `python -m unittest test_focus_appearance_experiment test_focus_appearance_proposal
  test_focus_mixed_assembly test_focus_learning_experiment
  test_focus_development_experiment -v`: exit0,59 tests/2.875s in integration-tests.log.
- `swift build` and `swift test` with `--disable-automatic-resolution` and project
  cache/config/security paths: exit0, logs alongside this handoff. Scoped normal-host
  permission covers nested-sandbox compilation and normal CoreML test caches.
  Explicit outputs/temp remain project-local. Full suite:14 XCTest +93 Swift tests.
- `git diff --check`: exit0. No git writes.

## External dependency and next action

Read verified Sillycon SMB peer snapshot: APPEAR-VISUAL-20260922 still reports
06:13:24Z, no newer acknowledgment/artifact. Local producer checkout remains0e43ab3;
its three-preset contract lacks the requested new family schema, hash vectors and
independent-appearance-families report. Checked both known local checkout paths;
did not fetch, operate a simulator or write the producer repository.

Existing NUA request `nuiak-20260923T053700Z-independent-appearance-families`
already contains the exact missing handoff. No duplicate request or unrelated local
software noise published. Last publication/readback is the corrected replay's
coordination.md; acknowledgment of that follow-up remains unknown.

Resume real family qualification when the source-backed contract and representative
artifact arrive. Then validate consumer compatibility, review real visual independence
and reserve untouched evaluation membership; separate capture/training authority
still applies. No additional offline scaffolding is proposed to stand in for this
genuine-artifact dependency. No running jobs remain.
