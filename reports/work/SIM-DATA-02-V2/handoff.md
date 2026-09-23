# SIM-DATA-02: source-pinned v2 intake and runtime crops

Owner: NUIAK architect. 2026-09-23 UTC. Completed offline tranche for review.

| Outcome | Result |
|---|---|
| Software verified | Passed:83 focused Python tests; Swift build;14 XCTest and93 Swift Testing tests. |
| Data eligible | No new genuine admission; derived v1.5 is development-only, full training closed. |
| Integration qualified | Offline real CLI/crop/baseline path passed; genuine repaired TTR bundle pending. |
| Model gate passed | Not assessed; no new training or production change. |

## Scope and source

Local TVTestRig checkout inspected read-only at46dce7b3a79e4f17af49bc0324d4aeba3cc0958d.
Inspected production `HarvestPairMetadataFile`, `HarvestCaptureEndpoint`, recipe hash
algorithm, native bracket admission and `HarvestBundleValidator.validateVersion2`.
Peer reports merged8fbec4a and candidate dylib
`b56d4509bf65970a099e185ed1cc00ea7ba1a28fbc925c969f0dc7238c6695b2`.
Advertised `.local-work/native-observation/FixtureDerivedData/Build/Products/Debug-appletvsimulator/TVTestRigFixture.app`
does not exist in the local producer checkout; peer's linked reconciliation report
also absent locally. Do not claim build equivalence or changed runtime qualification.

Preserved all pre-existing iOS/model/perception/direct-resume edits. The existing
numeric Swift Date correction in harvest validation remains intact. No TTR files,
simulator state, installed app,138 retained pairs, source receipts or weights changed.

## Integrated implementation

- `scripts/harvest_sidecar_v2.py`: version2 strict contract; complete recipe/hash;
  all four before/after scenes; observed reference/target; native source/generation,
  freshness/settling; independent frame geometry; host receipt order; PNG binding;
  flat/nested alias and exclusion consistency. Varying diagnostic counters are allowed.
- Existing `harvest_bundle_validation.py` dispatches declared versions, preserves
  unverified source context and binding, and rejects unknown versions. Enforces
  documented filename/row-hash links, bounded decoded dimensions/decompression.
- Existing simulator manifest CLI preserves sidecar hashes and raw bracket evidence.
- `ttr_focus_manifest.py` adapts validated artifacts into v1.5; no new cropper/trainer.
  `harvest_focus_pairs.py --fixture-bundle … --ttr-sidecar-v2` integrates it into the
  existing extraction entrypoint. Choose `--test-only` for software cases or an
  explicit `--visual-review` bound to index/receipt/sidecar identity and report bytes.
  `--dry-run` writes nothing. Existing `--pair-evidence` legacy flow remains distinct.
- Actual production `FocusRingClassifier.makeCrop` supplies16%/256×256 pixels.
  Separate observed bounds are retained for each role. No invented frameID or
  focusFrameID appears in the new contract. Raw producer bundle stays immutable.
- Existing dataset validator revalidates original artifacts and exact derived
  membership; baseline/runtime recrop accept v1.5. Training preflight still rejects
  it. No API/model/preprocessing default changed; no caller-provided training override.

## Acceptance evidence

`verify.py reviewed` with approved isolated focus-export-01 Python, project-local
TMPDIR/module/SPM caches, automatic dependency resolution disabled:

- `swift build`: exit0,0.598s, no warnings/errors.
- Seven targeted unittest modules: exit0,83 tests (wall19.187s).
- `swift test`: exit0,3.435s;14 XCTest +93 Swift Testing, no warnings/errors.
- Exact commands and timings: `reviewed/verification.json`; full logs adjacent.

New v2 tests exercise actual manifest/extraction CLI, dry-run/collision behavior,
production crop byte revalidation, baseline protocol preparation, and training
rejection. Nineteen bracket mutations cover missing endpoints/labels, altered hashes,
dimensions, host clocks, recipe contradictions, stale/unsettled/native-false claims,
coordinate conflicts, alias and exclusion drift. Version matrix rejects1/3/null/
string2/float2/bool. Review/report mutation, fake physical source, derived membership,
geometry, source-byte changes and forged training approval reject.
Existing legacy, physical consumer, direct42-recipe assembly and baseline regression
modules pass unchanged behavior. Scores used by existing offline fixtures remain
test-only; no new genuine model-quality measurements were made.

First integrated pass failed one old synthetic fixture that omitted documented
PNG filenames and row SHA. Corrected that fixture; did not weaken production checks.
Initial failure logs remain alongside both successful passes. Final self-review
added complete accepted-row/unknown-annotation accounting and immutable descriptive
source checks; those changes are included in the reviewed pass. Test outputs were
removed only by their existing project-local temporary-fixture cleanup.

## Runbook for the next genuine bundle

1. Obtain exact producer candidate and its source/build receipt via approved transfer,
   not SMB image transport or remote shell. Fresh operation/setup authority and target
   checks still apply. No repeat of unchanged kitchen-sink failure.
2. Preserve36 direct recipes/138 pairs. After reviewed repair, resume only six missing
   groups; resolve54 historical maze clipping occurrences before full-pilot review.
3. Separately validate a genuine completed TTR v2 bundle. Inspect both images and
   nominal/focus-effect geometry; create a review bound to `bundleIdentitySHA256`,
   `sourceKind: simulatorFixture`, accepted disposition, report path and SHA256.
4. Use existing extraction CLI with `--ttr-sidecar-v2 --visual-review REVIEW` in a
   new output directory. Run existing baseline prepare/infer commands only under
   assigned inference scope. v1.5 and simulator success do not approve training.

Shared coordination records exact producer request acknowledgment separately from
publication/readback. This tranche contains no external wait/capture time and no
background operation. Remaining live criteria require unavailable exact artifacts/
genuine bundle, not another offline helper. Next useful work is the repaired boundary
and complete pilot/baseline, not a second consumer implementation.

[Shared coordination](coordination.md): final NUA publication/readback passed; the
new artifact-handoff request remains unacknowledged. Existing kitchen repair request
was acknowledged by TTR at01:34:37Z. Snapshot expiry never grants runtime access.
