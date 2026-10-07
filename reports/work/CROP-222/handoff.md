# FocusRing crop sensitivity — CROP222

Completed a controlled inspection-only comparison on20retained schema4pairs.
No new capture, training, model export, data admission or production crop change.

| Measure (producer-reported roles, not accuracy) | Endpoint boxes | Shared pair-union box |
| --- | ---: | ---: |
| Positive focused-minus-unfocused margin |8/20|5/20|
| Reported focused probability ≥.85 |8/20|8/20|
| Reported unfocused probability ≥.85 |8/20|12/20|
| Unclipped positive margins |1/2|0/2|
| Clipped positive margins |7/18|5/18|

Mean margin delta:−.09131unclipped,−.13677clipped. The most improved case is
cutout-01-dark-detailed (+.89868margin); worst is streaming-library-dark-r2
(−.88156). This does not support replacing production cropping with the union.
Both frames determine the shared box, so it is not a single-frame online strategy.
Union also changes context/relative object size; the test does not isolate growth
as a causal feature. Sparse unqualified membership cannot establish recall/FPR.

## Implementation and actual execution

Extended `harvest_schema4_review.score_review` and existing
`ttr_focus_manifest.py` with opt-in `--review-geometry pair-union` and compatible
`--compare-review-scores`. Defaults unchanged; production makeCrop still applies
16%expansion and256×256output. Comparator rejects incompatible model/runtime/input
identities, duplicate/partial rows and invalid probabilities; flags remain unadmitted.
No parallel cropper, scorer or trainer introduced.

Current helper hash0dc900881da7729ac5b13e9c1ed71e8d43e33505785e96201598ffde37f5e331
differs from old cached87f7f831…; model/source/OS unchanged. Recorded amendment
then scored both policies on the same current helper,80endpoint responses total.
Original diagnostic preserved. All20pairs revalidated before/after each actual CLI
invocation. Model SHA9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7.

Inputs: ART-INTAKE-191/artifacts/regular-subset01/
tvtestrig-20261005-art191-regular-subset. Outputs under this packet's artifacts:
endpoint01/review-scores.json SHAda87b8a611bea7cd760b50d9f215ee141378937ef6501619dcf44bbd1a6374ab;
union01/review-scores.json SHA793534f1bde0a14045ac9ad87e5b83d04b3239ff8f73e9776864decc3bb69b79;
union01/geometry-comparison.json contains complete paired deltas.
Both actual entrypoint commands exited0; exact argument shape recorded in canonical
plan and CLI help. Runtime scores are real CoreML, unit-test scores are fakes.

28focused Python tests pass. Offline native Swift build passed; restricted test
execution failed with CoreML sandbox-extension denials. Scoped host-access replay
passed140Swift Testing+14XCTest; logs `.build/crop222-{build,test,test-authorized}.log`.
No signing/security changes. Git writes none; existing unrelated changes preserved.

TTR result published and parsed readback verified at
`nuiak/responses/nuiak-20261006-crop222-result.json`,1724bytes,
SHA2568b2abe75b94c1d89746c6eed9bddf862e0d52ee85b628b47a89b24b8ab6a313b.
Peer acknowledgment is not yet observed. Shared message contains metadata only.

Software verified; native-label data eligibility blocked as before; crop/inference
integration passed for this diagnostic; model gates not assessed. Next meaningful
tranche: integrate independently qualified focus labels and reserve matched native
growth/no-growth/content-only groups; run the planned exposure-matched FocusRing
comparison only when membership qualifies. Keep transition and single-frame claims
separate. This negative crop result prevents an unsupported production change.
