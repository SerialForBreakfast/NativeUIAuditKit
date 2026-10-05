# IOS-ROI-193 — preparation complete

2026-10-05 / Codex. No training, capture, export or promotion occurred.

## Deliverable

802 unique training crops from216 already admitted source images;94 identical
pixel/label aliases retain their parent/group ancestry.184of1080 planned views
collapse at clamped edges. All-class labels preserve1381whole and1552clipped objects;
10698out-of-window annotations are accounted for, not silently dropped.

The first attempt stopped at83generated crops on a cross-group pixel duplicate.
Inspection established identical classes/geometry with different label line order.
The reviewed amendment deduplicates sorted-label-equivalent training crops and
rejects conflicting labels. Failed prefix remains under artifacts/dataset; accepted
output is artifacts/attempt02. No source image was changed or evaluation role moved.

Evaluation windows use only022predictions≥.25. All original records remain:

| Partition | Original images | Crop proposals | No proposal |
|---|---:|---:|---:|
| Training fit |216|223|17|
| Development |96|72|38|
| Retained |2400|273|2148|

No-proposal counts are not automatically misses: many originals lack the target.
Only complete end-to-end scoring can establish accuracy. Geometry refinement preserves
base confidence/counts and non-page detections; ambiguous or missing donors fall back.

## Evidence

- `scripts/roi193.py`: actual preparation, exit0,31.674s; frozen10epoch candidate
  uses022last, fresh AdamW, batch8,640,warmup.25; in-sample monitor only.
- `scripts/verify_roi193.py`: exit0,17.834s; verifies every generated training
  image/label/source signature and duplicate alias, all manifests and original-image
  accounting. Six rendered boundary examples inspected: visible page dots remain
  enclosed; clipped surrounding controls align to the crop edges. This is representative
  semantic review, not an exhaustive visual claim.
- Proposal seal `c3dbfed67df4cc2a8ac9a513b890bced258ff8fdf6b4b44d66afe1c5a6cfaaf2`.
- Verification seal `8b6a66c6f1d330035fd0800f9fa9e9650b29b171ba12b66df2e4ce428040fd36`.
- `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python -m unittest discover -s scripts -p 'test_roi19*.py'`:
  exit0,12tests. Bounds/inverse transforms, all-class clipping/slivers, proposal
  completeness, failed/ambiguous outputs, conservation, duplicate conflicts and collisions.
- Offline Swift build exit0; sandboxed test exit1 at known Vision access boundary.
  Scoped host rerun exit0,142tests. Logs `.build/roi193-{build,test,host-test}.log`.
- Accepted dataset/metadata about22MB, below2GiBbudget; initial free disk36GiB.
  Bulk artifacts remain ignored; concise code and handoff are reviewable.

## Outcomes and next tranche

Software verified; derived training inputs eligible within existing216train roles;
local preparation integration verified; model gates not assessed. Proposal's
pre-launch review requirement is satisfied by this handoff; experiment registration
still precedes launch. No claim of better model accuracy yet.

Next IOS-ROI-194: one registered candidate, actual second-pass artifact integration,
all14matched gates and measured latency. TTR's fresh status remains unchanged from
23:19:24Z: ART191still needs regular-file-only consumer packaging and exact source.
No duplicate SMB message or unrelated iOS progress was published. Existing191receipt
remains the actionable request. All pre-existing changes were preserved; no Git writes.
