# Review of custom-apple10

## Result

NUIAK receives and reviews all 4 offered pairs. No human approval is needed for these checks.
The existing schema 4 checker accepts every pair. The production crop tool makes 8 crops at 256 × 256 pixels.
The tool uses the existing 16% expansion. No model runs or training occur.

NUIAK checks 40 indexed files across 4 completed bundles. Each bundle contains 1 pair.
All files retain the calibration role. NUIAK does not move them into training.
The earlier transfer check covers all 93 listed files and 24 PNG files.

## Image review

NUIAK draws bounds from the metadata on all 8 original images.
The supplied overlay plan contains only 2 entries. Those entries match the recorded bounds.
NUIAK makes the other review overlays locally. The first check expected 8 supplied entries and fails before this correction.

- The dark custom scene shows growth of the selected card. Its recorded body bounds contain no clipping.
- The light custom scene shows growth and clipping of the selected card. The recorded bounds describe both.
- The first Apple-style card grows and becomes brighter when selected. Its caption remains outside the body bounds.
- The middle Apple-style card shows the same change. The neighboring card loses its visible focus effect.

The image review agrees with the recorded focus states. It does not measure exact pixel agreement with another app.
The custom scenes use repeated poster art. The light scene also has low text contrast over the large artwork.
These limits matter for later coverage work. They do not invalidate the file checks.

## Version report

All 13 metadata hashes in TTR's version report match files NUIAK already holds.
TTR reports candidate executable hashes and installation records. NUIAK has not independently checked those executables.
TTR states that it cannot connect each pair to an exact captured build.
NUIAK accepts the report as partial evidence. NUIAK does not treat the current source as the source used during capture.
The separate Apple reference images are not in this new archive. NUIAK does not claim an independent comparison with those images.

## Decision

Use these pairs for inspection and development review. Preserve their calibration role and all original files.
Do not use them as training data or independent final evaluation.
Keep the failed last-position case excluded. TTR reports a wrong competing focus identity for that case.

The review is complete within this scope. Training use requires a separate decision about data roles and sufficient evidence about the capture software.
No new capture or repeated search is requested. Future capture records should connect each pair to the software that made it.

## Evidence

The local `artifacts/review/` folder contains structure checks, image overlays, index checks, and the crop receipt.
The existing checker and crop tool run without changes. NUIAK reuses their previous software test results.
Software checks pass for these inputs. Data use remains limited to review. No live integration or model qualification occurs.
