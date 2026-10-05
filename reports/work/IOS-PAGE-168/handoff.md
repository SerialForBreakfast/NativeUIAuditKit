# IOS-PAGE168 — higher-resolution inference rejected

Same Run017 checkpoint and96frozen compose155 development images,640versus1280
long edge. Existing exporter now accepts an explicit keyword-only resolution;
default640unchanged. All other prediction settings unchanged, including actual
export confidence.001 (not0),IoU.7,max300; original-image boxes preserved.
Settings hash differs deliberately. Strict old comparisons continue to reject it.

|Metric|640|1280|
|---|---:|---:|
|Page AP50|.291148|.039247|
|Page AP50:95|.177810|.007154|
|Operating TP/FP/FN|18/0/78|0/0/96|
|Native UIKit hits|0/48|0/48|
|Left-position hits|0/48|0/48|

Full confidence-ordered matching per stratum confirms prior oracle diagnostic
counts. All96members decoded/inferred/validated; no missing or failed inference.
Custom AP, development-only evidence, no independent release qualification.
Higher inference resolution alone is worse for this fixed model; it does not
prove higher-resolution training would be worse or identify the causal failure.

Evidence: [protocol](host-attempt/artifacts/protocol.json),
[sealed result](host-attempt/artifacts/result.json), and preserved predictions.
Elapsed12.317seconds includes model setup/export; allocator at reporting80070912
bytes is not peak memory. No matched640timing exists, so no speedup claim.
24focused tests passed, including actual mocked export, coordinate/settings
preservation, collision and invalid resolution rejection. Offline Swift build and
serialized tests terminal0 in `.build/page168-host-{build,tests}.log`.
First sandbox MPS failure and Swift cache rejection retained; scoped host retry
used project-local explicit caches. No service reset, dependency repair or capture.

Software verified; data roles unchanged; local inference integration verified;
model intervention rejected. Shipped models untouched. No TTR status publication
needed for local iOS findings; existing native24 source blocker remains unchanged.

Next substantial tranche: audit actual training page-control instances by
horizontal location, native renderer and normalized size; distinguish absent
coverage from label/scale issues. Then preregister one targeted coverage or
augmentation comparison, keeping these exposed probes development-only and
reserving fresh independent final groups. Native24 intake/model comparison proceeds
independently as soon as producer source is available. No blind epoch extension.
