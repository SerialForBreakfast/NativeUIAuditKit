# ADMISSION-136 — retained labels and negative-support audit

Completed October 4, 2026. Previous goal turn made progress through SPATIAL135;
this tranche changes the next fit's eligible membership and corrects its coverage
assumptions. No model run, capture, source edit, Git write or promotion occurred.

## Reviewed admission

[admission.json](admission.json) authorizes nine exact retained intervals for the
next pinned change-only development fit under the maintainer's autonomous admission
delegation: seven changes and two byte-identical controls. Two Balance intervals
remain excluded: their screen changes are visible, but native focus is unavailable.
This is agent visual review with corroborating producer observations, not human
annotation or authenticated framebuffer identity. It does not create precise boxes.

| Evidence family | Admitted intervals | DTM030 missed |
|---|---|---:|
| Within-screen focus | Survey26 1→2, 4→5, 7→8; Navbar29 15→16, 17→18 | 3/5 |
| Screen transition with known endpoint focus | Survey26 5→6, 8→9 | 2/2 |
| Identical-image controls | Survey26 6→7; Navbar29 16→17 | 0/2 |
| Unknown focus, excluded | Survey26 2→3, 3→4 | unavailable |

Both complete manifests were reverified against all member bytes. All 11 intervals
have exactly one recorded action with before-capture completion < invocation ≤
return < after-capture start, and producer-reported native bracketing agrees.
This supports interval association, not atomic frame/action causality.

Important exception: Survey26 frames 8 and 9 report `pixel_stable=false`.
The visible focus endpoints remain clear and agree with native evidence; the
moving/appearing preview is retained as a confound, not silently removed or called
settled. An exploratory assertion that *all* endpoints were pixel-stable failed;
the source flags were inspected and preserved. These pairs are admitted only for
the reviewed endpoint-change target, not a transition-completion detector.

Related Settings journeys/profile variants belong to one conservative exposed
ancestry group alongside previously admitted Settings examples. No random pair
split, independent held-out claim, or new final membership. Historical producer
`training_eligible=false` is preserved; the explicit consumer decision is an overlay.

## Existing negative coverage — corrected inventory

Verified `adapt_reflow117.inputs()` produced 433 examples with tensor SHA256
`bb670b721caeb98da3ba7beda1b7d3407a129047456fbb2d25df6eff639e7256`.
There are **160 positive and 273 negative labels**, not 207 positives.
“207 originals” is a mixed-label retention group.

| Negative subset | Count | Support |
|---|---:|---|
| Original, nonidentical | 31 | 12 synthetic scroll-unchanged, 16 Fixture content-only, 3 reviewed exposed Settings |
| Original, identical | 16 | Boundary controls |
| Derived identity | 226 | Repeated endpoints, not 226 distinct native motion scenarios |

The three Settings negatives are indices 25, 26 and 28. Their historical row
`split=development` is superseded by the explicit REFLOW117 admission overlay;
reading only that old field gives the wrong effective role. No new role change
to those examples occurred here. Nine newly reviewed intervals add no nonidentical
negative. The actual gap is broader native same-focus/content-motion support across
unseen journeys, not an absence of existing nonidentical negatives.

## Companion: TTR workflow review

Read and SHA256-verified in place (not copied; not cleanup receipts):

- `tvtestrig/ttr-grouped-campaign-workflow-20261003-r2.md`, 7,287 bytes,
  `29675c5b2181a7f31ed2aea2af274b5ac3d493d6d6934f0b58df2927897f82f7`.
- `tvtestrig/tvtestrig-20261004-workflow-navigation-feedback-final.yaml`, 1,417 bytes,
  `bfbb9fb1fc0bf9975a95a6a0c05895f044e00c180dda3803b38a2a799e312b3e`.

Consumer guidance: reuse compatible grouped campaigns with aggregate budgets and
preserved lineage, serial export by default. Report 24 attempts as four specifications
and one ancestry, not 24 independent samples. Producer timing means (90.63 seconds
grouped, 98.88 separate, 124.40 overlap) are small sequential evidence, not a general
speed guarantee. Report 47 passed/3 skipped, not the obsolete per-device aggregate77.
No consumer runtime/build qualification inferred from this metadata review.

Navigation feedback concerns a different retained run: DTM030 has three native-hint
agreements, four disagreements and one ambiguous case among eight selected intervals.
Do not mix it with Survey26's denominator or turn native agreement into accuracy.
The peer status remains timestamped 18:46:20Z, expired; no new runtime readiness
or acknowledgment of SPATIAL135 was established.

## Verification and outcomes

Read-only resident Python audit revalidated manifest membership, all source hashes,
pair chronology, exact source-image identities, encoded equality, and label counts.
First path-helper invocation used a relative root and was correctly rejected before
any write; reran with the resolved exact root. The pixel-stability assertion failure
above is retained as a finding, not a passing gate. Final admission validation checks
exact pair membership, source/request hashes, nine admitted/two excluded, labels and
original producer flags. JSON parsing and `git diff --check` are required at handoff.
Final admission audit passed: 11 exact source intervals, nine reviewed labels, two
unknown exclusions; original producer flags preserved. Admission SHA256:
`4c37065854bd7b0ba76cd83aa0203b3536f2b179cc82116852843e20bef29a37`.
JSON parsing and whitespace/diff checks passed. No implementation changed, so prior unchanged software evidence is reused; no new
Swift test claim. Worker and model-workflow skills kept data roles and model gates
separate; shared-status protocol distinguishes read-in-place from transfer receipts.

Software: not newly assessed. Data: nine scoped change-only roles eligible, two
excluded. Integration: retained data reviewed, no new live qualification. Models:
not assessed; DTM025/030 remain passive, neither replaced.

Published `packets.ADMISSION-136` in `/Volumes/SharedStatusFile/nuiak/status.yaml`
at20:52:04Z through the verified Sillycon SMB mount. Unique-key YAML readback passed;
unrelated semantic content remained SHA256
`3517cfa96b4e6b38de44ec9c98d466a84dae8f00b129c1ba8ec6d156cd6967fd`.
Peer acknowledgment is not observed. Metadata reviews were explicitly not copied
artifact receipts and do not authorize sender cleanup. Existing negative-coverage
request ID preserved; clarified the missing domain support rather than duplicate it.

## Next substantial experiment

Fit one retained-adaptation comparison against DTM036 using the nine admitted
intervals with equal family weighting, frozen encoder/proposals and old retention
constraints. Pin 600 epochs, Adam 0.01, seed 42, CPU two threads, fixed-last checkpoint
and ≤2 GiB outputs before execution. Prepare features once. Compare all 207 old
cases, 226 identities, the nine now-exposed fit cases, and existing quantized/localized
nuisance controls; report the two excluded Balance decisions without correctness.
No success on these exposed cases establishes deployment performance. Bind source
hashes and role overlay through the real training entrypoint first; do not bypass
the current fixed-membership protocol with an ad-hoc fit. Independently reconcile
FLOW124 conformance delivery once immutable SMB publication is supported; the
existing unsupported rename/link semantics remain a delivery blocker, not a
reason to recapture. TTR's retained native-motion inventory remains useful but
does not block the scoped admitted-data experiment.
