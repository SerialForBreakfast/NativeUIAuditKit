# IOS-COV: the missing coverage is broader than webContent

2026-09-23. Decision preparation complete; no taxonomy, gate or split change made.
Current evidence: full fresh prefix-audit.json and its hash-bound coverage.json.

## What is established now

- All14,340 manifested pairs pass image decode, SHA256, strict schema, dimensions,
  source binding and visible-coordinate checks. Zero decoded duplicates and zero
  cross-split pixel groups. This is an incomplete replacement corpus, not recovered
  historical pixels or a qualified model benchmark.
- Frozen-count audit exits1 with exactly three findings: train10,140 !=12,340;
  test1,800 !=2,200; unindexed`.DS_Store`. Finder metadata is retained, not deleted
  or misreported as corrupt training pixels. No other member failure was found.
- Visible annotation support: train39/41 classes; validation12/41; test12/41.
  Train lacks dynamicIsland and webContent. The untouched test prefix supports
  imageView, label, listRow, navigationBar, pageControl, picker, primaryButton,
  secondaryButton, secureField, stepperControl, textField and toggle only.
- Full per-class counts including zeroes are in coverage.json. Counts exclude
  zero-visible-area/explicitly excluded boxes. Sidecar metadata is not proof of
  distinct runtime devices or rendered accessibility effects. Source OS unknown
  remains tied to pinned runtime evidence, not silently filled into sidecars.

## Count decision — must precede continuation

**Approved by the maintainer on2026-09-23:**12,540 train /2,400 validation /
2,000 test, total16,940. The user's “Yes. I approve.” answers the explicit
corrected-split request. Preserve all existing family assignments, pixels and
historical audits. This supersedes the unresolved decision below, not the coverage
or model gates. No new native-probe execution or training approval is implied.

The five remaining batches are UIKitControls700, UIKitForm700, UIKitList700,
UIKitToggleForm300 (train) and WizardStepFlow200 (test). They finish at
12,540/2,400/2,000, total16,940, rather than frozen12,340/2,400/2,200.

Recommended explicit amendment: preserve already assigned families and total16,940,
correct the erroneous split-count expectation to the actual recipe allocation,
and retain both original and amended records. Alternative: review a new remaining
recipe allocation that supplies200 additional unseen-family test members and200
fewer train members, without moving existing pixels or mixing a family across
splits. That requires new source/configuration and diversity checks, not changing
a manifest's split labels. Maintainer choice was requested; neither applied.

## Gate interpretation

1. Existing shipped five-class iOS model remains unchanged. Historical Run0090.586
   is non-comparable to reconstructed data.
2. P1-B baseline may eventually report AP on supported held-out classes once the
   complete declared test membership is eligible and inference is assigned.
   Unsupported AP entries must be unavailable with zero support, not AP0 or a
   fabricated41-class mean. Always name the metric's supported-class denominator.
3. DS-G8 and41-class shipping are not established by partial coverage or a high
   mean over12 supported classes. Expose all coverage gaps with any future result;
   do not silently drop absent classes from the declared model map.
4. Toggle and stepperControl have test-prefix support, but this is not the separate
   real-fixture gate, nor a license to replace iOS evidence with tvOS data.
5. `webContent` remains retired/absent. A native placeholder is not a valid webContent
   label. Do not revive the failed WKWebView route as an incidental reconstruction fix.

## Follow-on native coverage proposal, separately reviewed

Keep this fixed-count reconstruction intact. Define a supplemental new corpus
version with native-only, generator-direct boxes and source-disjoint held-out
families for missing native categories: chrome/navigation containers; contextual
menus/sheets/alerts; controls and visual indicators; collection/scroll content.
Require train/validation/test support for the declared evaluation scope and test
actual rendered geometry, clipping, crop/box transforms and deterministic diversity.
Capture family allocation and minimum support before rendering, not after inspecting
model failures on final test. Add visible dynamicIsland training examples using the
existing native chrome mechanism only if its rendered annotation is verified.

Resolve webContent through a separate honest milestone decision: keep the41-class
map and report its unsupported gate, or explicitly approve a scoped milestone with
clearly stated unsupported class while retaining IDs. No unilateral reduced mapping
or full41-class qualification claim. This proposal does not authorize supplementary
generation, training or model promotion; complete the existing corpus first once
the split-count decision is made.
