# Trial02 development admission proposal — not execution approval

## Superseding two-batch proposal — 2026-09-28

The original single-batch proposal below is historical. The current scope includes
both completed revisions: `20260928T225131Z-056fc495` and
`20260928T232705Z-8a71fdbe`. Batch03 remains open and is not read or included.
Exact hashes, complete frame/sample membership, proposed partitions and pair
candidates are frozen in
[`batch12-coverage-proposal.json`](../../reports/work/FOCUS-REGRESSION-V2/office-trial-02/batch12-coverage-proposal.json).
This is a sealed **proposal**, not an approved admission manifest.

### Evidence and proposed scope

Both immutable revisions, their editor snapshots, completeness receipts and
production crop reports revalidate. Total:16 frames/171 controls,16 focused and
155 unfocused. Human completeness receipts cover all16. One recording session;
no independent-source or untouched-test claim. No formally declared pairs exist.

| Population | Controls | Focused | Proposed use |
|---|---:|---:|---|
| Settings listRow |49|5|Candidate focus classification |
| VoiceOver otherFocusable rows |20|2|Candidate focus classification, preserve role |
| Home collectionItem |49|3|Candidate focus classification |
| App Store tabItem |36|6|Candidate focus classification, not detector class metrics |
| Labels and decorative image |16|0|Separate auxiliary-background diagnostics |
| Home clock/avatar otherFocusable |1|0|Unresolved focusability; do not silently reclassify |

Proposed candidate population:154 controls (16 focused/138 unfocused).
Auxiliary population:16 controls. `recorded-605:new-7` is the unresolved clock/avatar
region. Its original human annotation is preserved. Source annotations must never
be rewritten by applying these analysis roles.

### Frame selection admission

Human completeness is necessary but not sufficient when visual evidence raises
a conflict. Frame605 shows partially visible lower-row tiles without boxes and the
clock/avatar role is unresolved. Preserve its seven crop classifications as
diagnostics; **do not claim complete-frame unique-selection accuracy** until an
explicit visible-candidate convention and this frame's completeness are reconciled.
This does not require interrupting the current annotation session.

The earlier settlement question for656/676/687 remains open. Retain all16 in
accounting; report those three as settlement-disputed and605 as candidate-set
unresolved, rather than silently dropping them. A provisional supported frame
subset would be12 frames/130 proposed candidates; report it as such, with all four
excluded frames and reasons. No such evaluation is executed by this plan.
Producer-unverified249 has a later explicit human settled confirmation; preserve
both facts. Human review is not native telemetry.

### Pair identity and confounds

The proposal lists14 potential cross-frame matches, **zero admitted pairs**:
9 visually supported same-control proposals (two Accessibility rows, Install Apps,
six tabs);1 Fixture tile with changed background/scroll context;2 value-confounded
settings;1 clipped Computers counterpart;1 uncertain blank-icon identity.
Even the nine are assistant visual observations, not new human pair attestations.
Install Apps retains its value, but surrounding Update Apps changes; disclose that
context. The six tabs await settlement reconciliation. Local `new-N` IDs are not
cross-frame identities: Install Apps is new-3 in456 but new-2 in488.
Use exact proposed mappings, never equal ordinal/nearest-box matching as truth.

### Next implementation assignment, after approval

1. Approve a separate, versioned development-only admission record binding these
   source/crop/completeness hashes and explicit candidate/auxiliary/unresolved IDs.
   Keep source `trainingEligible=false`; no taxonomy changes or forced role mapping.
2. Extend the existing evaluator's intentional revision-v2 rejection only for an
   approved role-aware manifest. Preserve legacy behavior. Test wrong hashes,
   changed membership, unmapped roles, disputed settlement, incomplete frames,
   missing/duplicate scores and auxiliary exclusion from frame metrics.
3. Pin exact shipped/FDR-009 model identities and current runtime paths before
   separately authorized execution, threshold0.85 and existing production crops.
   No training, margin/threshold sweep, export or promotion.
4. Report candidate recall/false positives and per-family support separately from
   auxiliary negatives. Report unique-correct/wrong/none/multiple only for admitted
   complete frames. Distinguish supplied human-box focus evaluation from full
   detector→focus performance; this does not measure detector recall.
5. Pair diagnostics remain unavailable until exact same-control proposals are
   approved; do not require pair approval to score independently admitted crops.
   Preserve per-frame states, clipping, context changes and failed predictions.

Decisions can be batched after annotation: partition/admission approval; settlement
for the three original tabs; completeness/role policy for605. Do not force repeat
annotation of all completed frames. Runtime execution remains separately assigned.

## Historical single-batch proposal

## Frozen source and proposed partition

Use only human revision20260928T225131Z-056fc495, its completeness receipt and the
qa-20260928 production-crop/audit reports under
reports/work/FOCUS-REGRESSION-V2/office-trial-02/. Never overwrite that revision.
The new review-batch-02 remains pending and is not part of this proposal.

Proposed candidate membership is exact:49 controls with class=listRow plus18 with
focusRole=tabItem,67 total,8 focused/59 unfocused. Retain all15 other annotations
as a separate auxiliary-background population (14 label,1 imageView), all unfocused.
Visual preparer observations on the rendered Settings contexts identify headings,
help text and the large decorative Apple TV image, not additional navigation
targets. This is a proposed role interpretation, not rewritten human ground truth.
Do not pool background-only accuracy into candidate focus accuracy.

Auxiliary IDs: recorded-303:new-12,new-13; recorded-319:new-10..new-14;
recorded-416:new-10..new-14; recorded-456:new-1;
recorded-488:new-4,new-12. All other reviewed controls belong to the proposed
candidate group. No control or pixel is deleted. Existing class IDs stay unchanged.

## Acceptance and unresolved evidence

- Preserve diagnostic source flags; an approval would create a separate versioned
  admission record binding exact revision, crop receipt and per-frame candidates.
- All8 frames have human completeness attestation and one marked focused control.
  Completeness is human evidence, not proof against unseen/offscreen controls.
- User previously called an App Store image unsettled, then explicitly confirmed
  all8 as settled in Finish review. Before settled-focus admission, clarify whether
  that later confirmation supersedes the earlier concern for recorded-656/676/687.
  Until then retain these3 as settlement-disputed diagnostics, not settled scores.
- Do not silently reduce an8-frame benchmark to5. Any supported Settings-only
  report must identify5 frames/49 candidates and explicitly exclude the3 tabs.
- All members come from one development-exposed session. Neither more screenshots
  nor the second annotation batch makes this independent-source qualification.
- Keep the whole session out of training and protected challenge populations in
  the proposed admission; future role registry changes need approval.

## Separately assigned evaluation implementation

Extend the human development evaluator to accept exactly role-schema-v1/revision-v2
under an approved admission manifest, replacing its intentional rejection only
after tests. Report67 candidate classifications separately from15 background
negatives; frame unique/wrong/none/multiple selection uses only approved candidate
membership. Preserve threshold0.85, exact models, production crops and complete
prediction accounting. Keep unmapped roles separate from detector class metrics.
No inference, threshold tuning, export or training is launched by this proposal.

Next approval: settle the App Store status and approve the candidate/background
partition, then assign role-aware development evaluation. Annotation of batch02
continues independently; no per-image interruption is needed now.
