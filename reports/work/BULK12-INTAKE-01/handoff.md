# BULK12 intake — complete for review

2026-09-29. Owner: current NUIAK consumer worker. Assigned receipt, crop QA,
efficient visual review, role decision and next-capture/readiness specification.

| Outcome | Result |
|---|---|
| Software verified | Existing importer validates all12 pairs; focused tests pass. No code changes. |
| Data eligible |12 native-labeled pairs valid for diagnostics;0 admitted to training because related development-source reservation remains unresolved. |
| Integration qualified | Received archive → native-bracket validation →24 production crops → visual review passes. Producer runtime recovery not assessed. |
| Model gate | Not run; no inference, training, export or promotion. |

## Receipt and accounting

Exact archive `ttr-focus-batch01-partial-12pairs-20260929.tar.gz`,37,640,464bytes,
SHA256 `00726d7346350338bebcd44d2249cfbd95418947c58fa7e285b2e6d1509cc8e5`.
New local destination: `dataset/tvos_captures/bulk12-intake-20260929/`.
41,311,088,640bytes available before copy; bounded extraction retains5GB reserve.
168 tar entries including directories/AppleDouble metadata;41,694,434expanded bytes.
All71 files.json entries verified; unlisted non-AppleDouble payloads rejected.
Sender originals untouched. Receipt.json records exact verification time/path.

Campaign receipt:25cases,3completed/1failed/1cancelled/20unattempted.12 exported
pairs accepted for diagnostic QA,0 rejected,0 blocked. Remaining88 planned targets
were not delivered; do not count them as completed or silently reduce campaign size.
Each completed recipe accounts for all4 observed targets and stable before/after
native capture brackets:48 endpoint snapshots across24frame files.

Existing `ttr_focus_manifest.derive(test_only=True)` preserved source labels and
raw training split, producing explicit development-only v1.5 QA manifests. That
normalization is not a source-role reassignment or training approval. Existing
FocusRingTool crop mode uses16% expansion,256×256, bounded pixel/item batches,
no model loading. All24 crop outputs pass manifest validation.

`qa/intake.json`:24frame files,21distinct full-frame pixels,24distinct crop pixels.
`qa/role-audit.json`:12distinct complete pairs; no contradictory crop labels.
Zero exact hash matches across10 checked training/retention/real/synthetic/protected
metadata references. This is not perceptual deduplication or proof of independence.
Protected challenge images were neither opened nor scored.

## Agent visual review — no human correction needed

Reviewed all3 numbered sheets and all24 crops. Flat, icon and linear-gradient
cards show enlarged/lit focused states versus smaller unlit counterparts. Target
geometry and context are coherent; neighboring focused controls intentionally
remain in some unfocused-target crops as hard-negative context. Text below a tile
appears within expanded context, not a manually expanded target label.
No blank/corrupt/cut-off target or visibly reversed focus pair observed.
This is agent visual QA, not a fabricated human signoff. Native observations remain
the label source. Three sheets are available for optional inspection; none require
the user to annotate every box. Inventory's pending-agent status is superseded by
this immutable review record; original generated inventory remains unchanged.

## Training eligibility and next decision

The new seed29001 samples reuse the flat/icon/linear-gradient motif and canvas
ancestry of SYNTH05's50 development pairs. Producer acknowledgment confirms this.
The existing source-role contract prohibits related variants crossing lanes; a
new family name or pixel hash cannot override it. Therefore no automatic admission.
Keep313 training candidates and9retention pairs unchanged. These12 are not new
independent evaluation evidence either.

**Recommended next decision:** approve a separately specified development experiment
that allows related procedural training variants while explicitly removing that
related SYNTH05 population from independent selection/qualification claims, and
uses the existing real development benchmarks for transfer checks. This requires
an explicit source-role/selection amendment, not just permission to launch training.
Alternatively retain the current strict source reservation and collect genuinely
separate training designs/assets. Neither option weakens untouched final-test gates.

Do not run another unchanged candidate. Real-world transfer, production coverage,
source independence and deployment gates remain open;24 valid crops do not satisfy
them. Human annotation is not the present blocker.

## Prepared next-capture specification (not dispatched)

`qa/next-capture-proposal.json` pins11 existing producer recipes/44target pairs:
buttons,Settings rows,tabs,nested tabs at variations0 and3 (32pairs), plus the
three received artwork motifs at brighter-background variation2 (12pairs).
Source recipe bytes and hashes are preserved. No repeat of received variation0
artwork; no invented runtime identity or executable campaign authorization.
This is a coverage probe before scale, not the production corpus or a replacement
for the96 matched-effect contrast proposal. Native-button artwork-equivalent
contrasts, sidebar/persistent-outline/profile examples remain unsupported gaps.

Before dispatch: TTR repairs timeout/strict stop behavior, source roles are agreed,
actual runtime/target/budget and explicit capture scope are approved. Prefer native
automation and deterministic grouped visual samples; no per-pair manual drawing.
After receipt, verify full accounting and crops, then decide production-scale waves.

## Verification and completion

Commands: existing synth05_receive.receive with the single named entry; exact files
manifest checks; existing validate_bundle/derive/prepare; metadata-only cross-role
hash audit; unittest scripts.test_synth05_intake scripts.test_harvest_bundle_validation.
All completed successfully. `focused-tests.log` records test counts. No implementation
change, so no full Swift rebuild required. Pre-existing dirty files preserved.
Source archive/member hashes retained; no source image or annotation modified.

Assigned intake/QA/review/decision/preparation complete. Training role amendment,
new capture and model execution are separate approval points, not unfinished local
QA. No worker processes left running. Shared receipt and concrete consumer result
are recorded in coordination.md; peer acknowledgment of this receipt is separate.
