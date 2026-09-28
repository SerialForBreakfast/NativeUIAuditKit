# Real-world focus regression v2 — collection and annotation proposal

2026-09-28. Maintainer prioritizes a materially more diverse development regression
set and its annotation. This supersedes training-data collection as the immediate
recommendation; it does not authorize device operation, training or inference.

## Outcome and roles

Keep the first8 Office frames as a legacy smoke set. Build a separately versioned,
real-screen development regression set; exclude both sets from training. Do not
present this failure-informed benchmark as untouched final qualification evidence.
Fixture-generated examples belong in a separately reported supplemental set, not
the real-world headline metric. Different sessions are not independent source groups.

## Coverage before volume

Initial collection target:24 distinct screen situations,2–3 settled focus states
each (approximately48–72 selected frames), across at least4 available apps/OS surfaces.
These are workload targets, not qualification thresholds. A new background or a new
selected tile alone does not count as a new layout situation. Select the coverage
list before model scoring, retaining ordinary cases as well as known weaknesses.

| Interaction family | Target situations | Variation to seek |
|---|---:|---|
| Artwork grids |4|Light/dark/colorful artwork, selected enlargement, visible neighbors; cap Home at2 situations|
| Horizontal shelves/cards |4|Different card shapes, dense/sparse neighbors, edge positions|
| Native lists |4|Different screens, row lengths, selected-white versus subtle focus treatments|
| Buttons/detail actions |4|Short/wide buttons, different backgrounds and button arrangements; Photos Welcome at most1 situation|
| Tabs/navigation/toolbars |4|Icon/text controls, horizontal/vertical arrangements, selected versus actually focused|
| Transient overlays/search/player controls |4|Only already-accessible, non-sensitive screens; no purchases, account prompts or settings changes|

Substitute unavailable families explicitly; never manufacture support by repeatedly
capturing the same dialog. Record app/screen/layout family, theme/artwork, control
shape/size, focus cue and source session. Unknown attributes remain unknown.

## Collection workflow

1. Confirm current target availability and operator-approved apps/screens. The human
   operates TTR controls; no autonomous navigation is part of this proposal.
2. Verify the action-linked recorder and exact consumer bundle. Start once, human
   navigates, stop once, review a batch. No chat per press. Local records still mark
   this integration unqualified; obtain current producer evidence before scheduling.
3. Retain raw before/input/settled-after sequences, timestamps and failures. Curate
   distinct settled frames for annotation; keep no-op/duplicate events in sequence
   evidence without counting them as diversity or requiring repeated annotation.
4. Compare decoded image pixels for exact duplicates. Reuse labels only with an
   explicit identity-bound mapping. Near matches are review suggestions, not proof
   that geometry or focus state stayed unchanged.
5. First review a6–8-frame mini-batch spanning several families. Measure annotation
   time and fix workflow problems before preparing the remainder in batches of8–12.

## Annotation contract

Use the existing local rectangle editor and cheat sheet. Label control bounds,
not a tight glow outline; use existing conventions for labels/artwork and production
16%-expanded crops. Annotate all visible focusable candidates in the selected region,
their taxonomy class, focused/unfocused/unknown state, and frame flags. Explicitly
identify the same control across paired states; copied IDs alone do not prove identity.

Prefill/copy rectangles for compatible layouts, clear inherited confirmations, and
check size/position after focus enlargement or scrolling. Human review owns labels;
OCR, remote intent and model predictions are assistance, not ground truth. Ambiguous
focus, transitions, occlusion and uncertain geometry remain blocked/pending.

The original review schema does not attest complete-frame candidate enumeration.
FOCUS-REVIEW-PREP-01 adds a separate optional, revision-bound completeness receipt
in Finish review; old v1 flags remain unchanged. Its crop-level metrics remain valid;
complete-frame unique-selection metrics still need a separately assigned adapter
that validates that receipt. Many annotated boxes alone never imply completeness.

Offline preparation is implemented: [operator checklist](../../reports/work/FOCUS-REVIEW-PREP-01/operator-checklist.md),
eight-frame balanced queues, exact-repeat dispositions, coverage and double-click
label editing. This does not unblock the recorder or require redoing the smoke set.

## Acceptance and subsequent comparison

Freeze reviewed membership, originals/crops/hashes, human receipts, source/layout
groups, explicit pairs, supported/unsupported coverage and duplicate dispositions.
Check training/retention/protected overlap; retain unknown independence. Existing
production crop QA and audit must pass. Report per-family positive/negative support;
do not let a large Home grid dominate an aggregate presented as broad performance.

Only after review is complete, propose one pinned shipped/candidate comparison under
separate execution approval. Report legacy smoke and v2 results separately, including
per-family recall/false positives and explicit paired outcomes. No threshold sweep,
training use, promotion or final-challenge claim.

Next operator input: identify4–6 available apps/surfaces that the maintainer is
comfortable navigating and capturing. Capture readiness must be checked separately;
planning and retained-image curation need not wait for model improvements.
