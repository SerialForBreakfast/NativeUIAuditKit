# Proposal recovery and bounded training preparation — tranche 37

Assigned by the maintainer's continuation of scorecard36's recommended tranche.

1. Reuse the 46 frozen real tvOS frames and production predictions. Run the existing
   raster proposal detector and Apple Vision rectangle/OCR probe once. Compare YOLO,
   raster, Vision, and deterministic union (IoU .90 duplicate suppression). A separate
   OCR-supported raster arm retains only wide rectangles containing recognized text;
   text regions themselves are not expanded into invented control bodies. Fixed
   settings, no threshold search. Score body recall at .50/.75, focused-target recall,
   proposals per frame and duplicates; unreviewed boxes are not false positives.
2. Independent iOS spike: choose the first 12 distinct retained secondary-button
   frames and 12 cancel-action frames with an IoU .50 localized prediction, by sorted
   image ID. OCR the full frames, then use only text within the predicted box. Test
   exact case-insensitive `Cancel` as a cancellation hint; other text abstains on
   fine role. Compare existing type, coarse button-family type and selective semantic
   output. This deliberately selected development sample cannot establish general
   semantic accuracy. Source/label hashes remain checked; no label changes.
3. Implement a reusable bounded full-screen training entrypoint using the resident
   tvOS trainer/Ultralytics path. Separate validation-only from execute; require local
   checkpoint, exact complete grouped membership/admission and immutable input hashes.
   Watch only the launched child for wall-time and output-size limits, retain partial
   artifacts/receipt. Test with a stub child; real training waits for admitted inputs.
4. Recheck local TTR coverage source. Mapping/build needs the actual published source;
   independent tasks above continue if the adjacent dirty checkout still lacks it.

Execution: at most 70 existing screenshots, 600 seconds combined Vision/raster
processing, 2 GiB new output; ordinary Apple framework host caches allowed, explicit
outputs/temp/caches project-local. No threshold sweeps, downloads, new capture,
training/admission, model export or promotion. Record actual tool/source identities,
timings and failures. Focused tests and offline Swift build/test at integrated handoff.

## Bounded full-screen runner contract

`scripts/train_fullscreen_focus.py --contract <project-local JSON>` is read-only
validation. Add `--execute --output <fresh project-local directory>` only for an
assigned training run. The older tvOS trainer's `--dry-run` still means training;
the new entrypoint deliberately does not reuse that term.

Contract version `fullscreen-focus-run-v1` contains `checkpoint` and `admission`
path/SHA256 references, `runtime` from `runtime_identity()`, `seed`, `epochs`,
`batch`, `imgsz`, `budget: {seconds, bytes}`, and exact `frames`. Each frame has
`id`, `split` (`train` or `development`), `group` (shared source/content ancestry),
and image/annotation path+hash references. Group names are provenance claims whose
validity must be checked at admission; a new seed alone is not new ancestry.

Admission version `fullscreen-focus-admission-v1` requires `approved: true`, named
`approvedBy`, purpose `full-screen-focus-training`, and `membershipSHA256` equal to
the canonical digest of the exact frame list. This does not grant execution authority
or automatically convert existing diagnostic membership into training data.
Annotation version `fullscreen-focus-annotation-v1` binds the exact image reference,
`completeFocus: true`, `profile: ordinary`, and controls with unique IDs, top-left
pixel `bounds` and binary `state`. Only focused bodies become experimental class0;
complete no-focus frames are valid negatives, while both splits need positives.

The runner verifies bytes, decoded-image duplicates and source-group isolation,
stages its own images/labels, rechecks inputs inside its supervised child, and uses
the existing tvOS training-options function. It pins dependency versions, disables
automatic installs/network sockets, uses MPS/zero loader workers, preserves native
appearance by disabling geometric/color augmentation, and confines configurable
caches to the output directory. Preflight rejects insufficient staging space.

Budget stops terminate only the owned child process group and retain a terminal
receipt/log/partial artifacts. Output limits are sampled, so recorded overshoot is
possible; this is not a storage quota. Runtime validation is separate from model
qualification. Positive child wiring is tested with a model double; no real training
has been performed through this new runner yet.

## Designed iOS geometry follow-up (not executed here)

Retained page-control support is 200 GalleryPage and 400 OnboardingPage frames.
Freeze the first 20 image IDs from each family, independent of prediction outcome.
Compare the same Run013 checkpoint at 640, 960 and 1280 letterboxing, retaining
confidence .001 and NMS .7 from the original evaluator. Reuse the old 640 result only
if dependency/settings identity is compatible; otherwise include it in the fresh
comparison (maximum 120 image evaluations, 300 inference seconds, 64 MiB output).
Report page-body IoU .50/.75 recall, class AP, duplicate/false detections, latency and
model-input short-side size. Keep labels unchanged. This distinguishes resolution
sensitivity from the separate list-row/image-view layout-family gap; it does not
assert that resolution is the sole cause. Freeze a later challenge before tuning.
