# IOS169 — page coverage audit

Exact repaired017overlay hash verified; all14540training label files hash-verified
and parsed with finite/category/bounds checks.80empty members retained, no filtering.
1566page-control instances, one per1566images. No repeated pixel decoding or inference.

|Family|Instances|Horizontal center range|Normalized height range|
|---|---:|---|---|
|KitchenSink|200|.500000–.500848|.006970–.007727|
|UIKitControls|700|.499333–.502000|.008998–.013493|
|MediaCardGrid|266|.500000|.011737–.014993|
|ProgressActivity|400|.500000|.011737–.014993|

All1566are in the middle third; none in left/right thirds. The96development probes
contain48centered/48left, with centers down to.122137. Their width range
.101781–.365564 and height .008998–.030125 partly exceed training ranges.

Native159's pinned source hashes for KitchenSinkTemplate,NativeUIPageControlView
and UIKitControlsViewController still match current source. Those900repaired
members use native UIPageControl (direct or wrapped). Other two templates use
NativeUIPageDotsView. Thus the native-probe failure is not simply a total absence
of native training; styling, scale, composition and generalization remain relevant.
UIKitControls explicitly uses systemBlue/systemFill tints; probes use label/
tertiaryLabel and seed19prominent background. Do not treat template-family metadata
alone as authenticated renderer identity or infer a causal effect from marginals.

Combined with168, evidence favors a positional/style coverage experiment over a
blind resolution or epoch increase. These probes remain exposed development data.

Evidence: [sealed audit](artifacts/audit.json), including exact label references,
all page membership, source hash, family ranges and full class counts. Runner
`scripts/page_coverage169.py`; three tests exercise empty/invalid/nonfinite/outside
boxes and bin boundaries. Offline Swift build/tests terminal0; logs in
`.build/page169-{build,tests}.log`. No training, capture or role change.

Software verified; admitted data unchanged; audit integration verified; model gates
not assessed here. TTR native24 remains blocked on local source46dce7b3 lacking the
exact new table-v3 contract; no duplicate request or recapture necessary.

## Next substantial experiment

Build a spatial-diversity treatment from eligible training groups only, preserving
all annotations and source ancestry. Before training, test transformed box geometry,
clipping and content retention; do not silently lose controls at image edges or
change probe roles. Prefer native layout placement when augmentation cannot preserve
whole controls. Freeze a matched no-change control and one treatment with identical
initializer/membership/epochs, then evaluate same retained and development corpora.
Position and appearance changes must be separate comparisons to identify their
effects; qualify new final groups before any production decision. Explicit protocol
and acceptance evidence precede each execution, not an automatic sweep.
