# PER-DATA — bounded existing-evidence annotation

2026-09-22. Assigned44-member review completed; broader benchmark coverage is blocked.

| Outcome | Evidence |
| --- | --- |
| Software verified | Actual perception CLI accepts39 byte-verified cases;25 perception tests pass; real-manifest adversarial checks reject unsupported claims |
| Data eligible |39 local development-only reviews,0 training cases,0 independent evaluation groups |
| Integration qualified | Local validator/byte-verifier/report entrypoint passes; genuine TTR integration not assessed |
| Model gate passed | Not assessed; prediction status explicitly unavailable, no inference/training |

## Review and limits

[Dispositions](dispositions.json) accounts for all44 original images and binds their
existing hashes; originals, sidecars and predictions remain unchanged. [Manifest](manifest.json)
contains39 cases in **one conservative unknown-journey development group**:
31 Home grid/shelf,5 app-switcher,1 Home folder,2 Photos welcome.
All39 have reviewed absence of **row-disclosure chevrons and true dialogs**;
this is not an annotation of every arrow-shaped logo or decoration. Folder,
switcher cards and welcome screens are not dialogs. No synthetic predictions were
created; [validation](validation.json) correctly recommends no training.

Both Photos frames additionally have **four visible button boxes and two
appearance-only focused-element labels**. Boxes trace rounded fills, not shadows,
in original1920×1080 top-left pixels. Full-resolution source and rendered overlays
were inspected; overlays reside `.build/debug-output/per-data-overlays/`.
White/enlarged button fill supports the visual label; it does not establish native
callbacks, settling, capture sequence, a paired training example or physical identity.
The remaining37 focus states are unknown, not negative labels.

Review method: agent inspection of all44 existing contact-sheet members for scene
and disposition; full-resolution inspection for both Photos boxes and the Settings
lead. No independent human review. Contact-sheet negative labels remain development
triage evidence, not final gold evaluation. Filename intent was not used as truth:
`office_pluto_loaded.png` is a Photos welcome screen.

Five exclusions retained: account picker (privacy), Settings list (management-text
privacy), video content (unsupported UI truth), Fixture diagnostic screen (unsupported
relation/focus truth), spinner (transitional). No identity text transcribed in labels.
These are logical exclusions, not deletion/movement/redaction. Settings chevrons
are a known lead, **not admitted gold labels** without privacy clearance.

## Coverage and exact resume conditions

| Required cell | Support / gap |
| --- | --- |
| Chevron ordinary/focused/clipped/disabled/nested row relationships |0 admitted; Settings lead privacy review required, other variations need permitted evidence |
| Chevron negative screens |39 development reviews; no dedicated decorative-arrow near-miss corpus |
| True dialog/button relationships; informational/destructive semantics |0; neither reported incident is present; welcome screens cannot fill this cell |
| Dialog negative screens |39 development reviews |
| Visual focus appearance |2 Photos examples/four boxes; other states remain unknown |
| Native observed focus, hard negatives, light/high-contrast matrix |0 qualified; missing source callbacks/pairs cannot be recovered from appearance |
| Independent evaluation and exact historical provenance |0; unknown journey members kept together, cannot establish a held-out benchmark |

No new capture or destructive-navigation request is dispatched. Resume missing cells
with separately permitted retained/fixture evidence and privacy review. PER-LIVE's
held-out benchmark remains blocked, but these labels can support a separately
assigned development-only comparison now. No TTR fix is required to run that comparison.

## Integration and verification

`reviewedNativeCapture` is an explicit additive source kind, not `physicalFixture`
or `testOnly`. Validator requires development, trainingEligible=false, unverified
source, conservative unknown journey, local privacy clearance and reviewedVisual
labels. Focus must say visualAppearanceOnly; inventory reports it separately from
observed focus. Existing source behaviors preserved, no producer schema/API change.

Commands use approved isolated Python with PYTHONDONTWRITEBYTECODE=1:

- `reports/work/PER-DATA/review.py`: exit0,44 hash/decode checks,39 manifest cases.
- `scripts/perception_benchmark.py --manifest reports/work/PER-DATA/manifest.json
  --predictions reports/work/PER-DATA/predictions.json --verify-bytes
  --output reports/work/PER-DATA/validation.json`: exit0,39 verified, unavailable inference.
- `reports/work/PER-DATA/verify_admission.py`: changed hash, unknown row relation,
  test-partition upgrade, pending privacy and prediction truth rejected; see `adversarial.json`.
- `-m unittest discover -s scripts -p 'test_perception*.py'`:25 pass/0.022s, `tests.log`.
- Integrated78 Focus Python tests and required offline Swift checks pass; logs and
  commands in [compression handoff](../FOCUS-COMPRESS-01/handoff.md).

Frozen artifacts use exclusive output creation; no original bytes altered. Base and
preserved pre-existing changes are recorded in the integrated compression handoff.
New files: review/materialization, manifest, all-member dispositions, explicit
unavailable prediction declaration, validation/adversarial evidence and source-kind
regressions. Existing reviewedVisual origin reused; no model-derived labels.
Coordination not applicable: local labeling only, no peer action changed.

Bounded review and software acceptance are complete for review. Full PER-DATA
remains coverage-blocked by the enumerated inputs; do not mark parent complete.
No remaining authorized capture/training or background work is implied.
