# Local diagnostic tranche 38

Assigned continuation, TTR update deferred by maintainer. Two independent outcomes:

1. Score the fixed proposal37 union with the unchanged production cropper and bundled
   CoreML classifier through FocusRingTool. Replay the fixed .85 winner rule over
   geometry candidates (without inventing semantic roles). Compare to retained
   production selection, report complete-frame outcomes separately from partial
   target hits. Diagnose target missing, low score and distractor outranking. This
   is a geometry-only selector experiment, not production integration. CPU-only
   probe; maximum 2,289 crops, 600 seconds, 128 MiB outputs. Preserve duplicate
   suppression at .90, tie ambiguity, source and model hashes.
2. Execute the designed iOS resolution diagnostic: first20 GalleryPage and first20
   OnboardingPage members by imageID, Run013 at640/960/1280, confidence .001, NMS .7.
   Fresh640 baseline, MPS, at most120 image evaluations/300 inference seconds/64MiB.
   Report page-control AP and geometry recall, operating-point errors, latency.
   Existing labels and data roles remain fixed. Use resident weights/dependencies.

Retain replayable outputs and tests, update local status with concrete next actions.
Training, source synchronization and TTR coordination are separate pending work.

Execution repair: one detector box exceeds the frame by7.7pixels. Extend the
diagnostic tool with an explicit intersecting/out-of-frame opt-in; retain strict
default. Pass original bounds into production makeCrop, which expands then clamps.
Pre-clamping the body would change pixels. Retain aborted pass separately.
