# REAL-TRANSFER-42 — completed

## Decision

The artwork-trained full-screen model does not transfer to the reviewed real apps.
Prioritize native control-family and scene coverage over longer unchanged training.
The independent iOS work is complete: the repaired full dataset is integrated and
verified, with original evaluation data preserved.

## Measured focus results

| Measurement | FSF001 full-screen | Retained production |
| --- | ---: | ---: |
| Focused bodies found, IoU .50 | 1/46 | 21/46 |
| Focused bodies found, IoU .70 | 1/46 | 20/46 |
| Focused bodies found, IoU .90 | 1/46 | 6/46 |
| Correct selection on completely reviewed screens | 0/7 | 4/7 |

FSF001 abstains on all seven complete screens. Across all46screens,46predictions
overlap known unfocused controls;11more are unreviewed on partial annotations.
AP on the seven complete screens is zero at all three IoUs. Partial frames are
excluded from AP rather than treating missing labels as negatives.

Operating thresholds differ (.25 FSF001, retained .5 production), so this compares
systems as configured, not architecture alone. These are exposed diagnostic screens,
not a new independent benchmark. Runtime2.615seconds includes setup and46inferences;
it is not a controlled warm-latency benchmark. PID62411.

Fixed checkpoint SHA256:
`5428fdb426b2b06c59623326444bd264945fd18a102cc51ff7161354cc734c4f`.
Canonical [analysis](focus/final-analysis.json) retains inference pins and separately
identifies corrected analysis source. Original predictions and initial report remain
available; classification of known-negative versus unreviewed boxes was corrected
through replay, not another model pass. Visual inspection of Home frame003 confirms
the missed enlarged Photos tile and unrelated lower-row proposals.

## Complete iOS repair integration

New corpus: `NativeUITrainer/reconstructed_corpora/ios-41class-r8-page-dot`.
New export: `NativeUITrainer/yolo_dataset_41class_r8/dataset.yaml`.

- 19,740 members:14,540training /2,800validation /2,400test.
- Exactly666approved training replacements; all5,200evaluation members and their
  exported labels unchanged. Old corpus retained.
- All images decoded and annotation geometry/schema checked; zero decoded duplicate
  groups or cross-split pixel duplicates. All exported labels checked against annotations.
- Hardlinked originals: zero copied pixel bytes. Treat both corpus versions as immutable;
  in-place writes to linked files would affect both versions.
- Assembly44.138seconds; full audit188.100seconds.498replacement images retain old
  pixels;168differ on the current runtime, with regeneration provenance retained.

Evidence: [lineage](ios-lineage.json), [audit](ios-audit.json),
[complete export verification](ios-export-verified.json).
Two safe preflight failures were repaired before corpus creation: the source manifest
needed an explicit larger read limit, and the new corpus needed a scoped training-output
path check rather than the diagnostic-directory helper.

Remaining pageControl support:1,566train (666corrected dot groups plus900native
containers), zero validation,600test. The900native containers require an explicit
visible-body versus interaction-container target decision; this tranche does not
establish that all are erroneous. New representative validation is needed before
selecting page-control training settings.

## Verification and next substantial tranche

8focus tests +6corpus tests pass. Offline Swift build and134tests pass
(14XCTest +120Swift Testing). Logs are adjacent to this handoff.

Next, in order:

1. Qualify native rows/buttons/tabs and mixed artwork scene generation against current
   source/runtime; implement the grouped coverage recipe in the [plan](../../../Research/Plans/RealTransfer42.md).
   Proposed capacity:1,000training /250development pairs, covering all screen positions
   and held-out scene compositions.
2. Resolve native page-control target geometry and prepare new representative validation
   membership, preserving existing evaluation roles.
3. Execute scoped generation and matched training comparisons after new membership/data
   use is approved. Compare against the fixed baselines and require real diagnostic gains.

TTR publication remains deferred at the maintainer's direction. No process is left
running. The next boundaries are new corpus membership/use and native geometry policy,
not another approval for these completed local checks.
