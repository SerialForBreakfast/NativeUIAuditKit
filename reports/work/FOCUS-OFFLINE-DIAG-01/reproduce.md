# Reproduce the cached-only diagnosis

Run from the NativeUIAuditKit root using the resident interpreter:
`/Users/josephmccraw/Library/Application Support/NativeUIAuditKit/Environments/focus-export-01/bin/python`.
No install, model execution, network or device operation is involved. Python3.12.9,
Pillow11.3.0; all explicit outputs/caches stay project-local. Use `-B` to avoid
bytecode writes. Use a new output filename/directory: existing outputs are rejected.

```sh
python -B scripts/focus_offline_diagnosis.py freeze \
  --protocol reports/work/APPEAR-EVAL-RESERVE-20260927/protocol.json \
  --comparison reports/work/APPEAR-EVAL-RESERVE-20260927/comparison/comparison.json \
  --candidate reports/work/APPEAR-EVAL-RESERVE-20260927/candidate-dataset/focus_dataset_manifest.json \
  --output reports/work/FOCUS-OFFLINE-DIAG-01/input-index-NEW.json
python -B scripts/focus_offline_diagnosis.py report \
  --index reports/work/FOCUS-OFFLINE-DIAG-01/input-index-NEW.json \
  --output reports/work/FOCUS-OFFLINE-DIAG-01/analysis-NEW
```

`python` above denotes that exact resident executable, not an environment switch.
Freeze pins metadata/implementation/image references; report verifies byte/pixel
integrity and completeness before scoring cached probabilities. Models, runtime
helpers and challenge pixels are not opened. Old backend/runtime identities are
reported as the original prediction provenance, not as newly loaded identities.
Metadata-only protected lineage may remain in frozen source manifests; it is never
followed to challenge images or used for failure selection.

Outputs: accounting.json (every required image accepted/blocked), diagnosis.json
(reproduced original metrics plus distributions/pairs/ranks/evidence selections),
candidate-coverage.json (all230 pairs and source-bound geometry), evidence.md and
95 numbered PNG sheets. Unsupported strata have zero support and null summaries;
no scores are imputed. Excluded count is zero on the retained valid inputs.
Incomplete/invalid prediction artifacts fail closed, retaining blocked.json and
any clearly labeled partial model diagnostics. Structural errors print a blocked
reason and exit2; no complete report is issued. No empty-subset qualification.

Quantiles use linear interpolation on sorted values. Frame rankBest counts strictly
higher competitors plus1; rankWorst also counts ties. Margin is true score minus
maximum competitor, unavailable without a competitor. Ranking never changes the
threshold selector. Worst misses sort ascending score/ID; false positives descending
score/ID; wrong/multiple frames ascending margin/ID; every unique-correct frame is
included. Candidate representatives are the first sorted pair per role/source/
scene/style/control, not score-selected. Full IDs remain in JSON and evidence index.

The pages paste retained256×256 crops without recropping/resizing them; full-frame
previews are display-scaled, with original-coordinate target boxes where known.
Pair pages include the same control's opposite state. Competition pages may include
the top competitor. These are diagnostics, not a new crop/evaluation protocol.

Source bytes are rechecked after output generation. Output images can be regenerated
deterministically under the pinned Pillow version; tests compare complete output
trees byte-for-byte. Existing crop/runtime parity, importer tests and assembly/trainer
preflight evidence are reused from their original handoffs, not relabeled as new runs.
