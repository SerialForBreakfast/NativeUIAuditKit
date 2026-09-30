# Bulk revision3 consumer source review — 2026-09-29

Scope: read-only inspection of published source/manifests plus execution of NUIAK's
existing pure recipe validator. No producer code executed, no inference, crop
generation, deployment or training. No archive copied or extracted; no receiver receipt.

## Findings, ordered by impact

1. **First shard is not representative across control categories.**
   FocusCorpusProduction.swift:62–74 emits all42 artwork cases for a variation
   before8 native-control cases, then slices25 cases/shard. Batch01 has25 card
   scenes:7 native-image,7 scale-only,7 border-only,4 glow-only. All use seed29001,
   dark theme, one background and four-column geometry. Buttons, Settings rows,
   tabs and nested tabs start in batch02. Keep existing captured evidence; do not
   claim four-category validation or silently replace/replay the running manifest.
   A later approved bounded selection should explicitly cover missing categories.

2. **Default review sampling does not reduce first-shard human work.**
   review-focus-corpus.rb:52,57,74–80 groups by motif/presentation, exact focus
   configuration, background, columns and mixed sizes, retaining six pairs/group.
   Planned batch01 has25 groups of4: all100 pairs selected. Across all500 recipes,
   projected184 groups select1,104 pairs, exceeding its1,000-record limit. The
   rescued budget exception would list otherwise verified pairs as rejected.
   These are static projections assuming all pairs succeed, not observed capture
   failures. Keep full automated verification; separate invalid inputs from valid
   unselected/review-budget-deferred inputs. Choose a deterministic small review
   budget spanning cues and controls; expose exceptions without requiring per-pair
   manual drawing. New coverage groups warrant review, not every seed repetition.

3. **Training-only labels are proposals, not established separation.**
   All500 cases declare train. Family identifiers change but retain common Fixture
   renderer and motif ancestry. TTR's19:49:30Z response explicitly confirms ancestry
   shared with prior50 diagnostic pairs and no independent-source claim. Do not
   infer independence from seed29001 or bulk-v2 names. Bind actual received members
   to source reservations before training admission; preserve benchmark/challenge
   roles and report overlap rather than silently relaxing gates.

## Checks passed and remaining boundaries

- Archive378961bytes SHA256
  cfe71e41d482828819c3f5312478d944e84aa242de45276528e73f2073d097a3.
- All60 handoff-manifest member sizes/hashes match. Archive member paths have no
  traversal/absolute names, duplicate destinations, links or special-file entries;
  expanded size1,924,414bytes. Inspection only, not extraction or receipt.
- Existing scripts/harvest_sidecar_v2.py recipe_hash validates500/500 published
  recipes against producer hashes, zero failures;500 unique recipe hashes.
- Planned support:420 card scenes,20 each buttons/settings_rows/tabs/nested_tabs_v1;
 70 native-image,350 custom,80 native-button scenes. Counts describe recipes,
  not independent sources, usable captured pairs or unique pixels.
- Coordinator source:443–484 binds exported split to campaign, requires v3
  sidecars/recipe identity and target accounting;615–628 emits case accounting
  and training_admission=consumer_pending.
- NUIAK already validates v3 competitor identity, ordered stable native brackets,
  both states' geometry, frame hashes and hierarchy. Production crop remains
  FocusRingClassifier.makeCrop:16% expansion each side, clamp,256-square resize.
  This delta does not require a crop-policy change. Actual new pixels/sidecars
  and production crop QA remain unverified; recipe compatibility is narrower.
- Producer grouped viewer checks hashes/dimensions/bounds, but does not replace
  NUIAK's full native-bracket/role validator.

## Fresh producer result and alignment

At19:49:30Z TTR reports partial_capture_exported_runtime_blocked:
12pairs/24images/48native brackets,3completed cases,1failed,1cancelled,
20unattempted. CoreSimulator inventory timeout; remaining88pairs not running.
Artifact: ttr-focus-batch01-partial-12pairs-20260929.tar.gz,37,640,464bytes,
SHA25600726d7346350338bebcd44d2249cfbd95418947c58fa7e285b2e6d1509cc8e5.
This artifact is announced, not copied or consumer-verified in this source review.

TTR accepted the division of work in its response to
nuiak-20260929-focus-campaign-alignment and acknowledged the8frame/155control
human-review/crop receipt. It confirms accepted12 cover icon/flat/linear_gradient
native-image cards only. Sidebar, persistent-unfocused outlines, circular/profile
and selected-unfocused tabs are absent; some are unsupported by the overall matrix.

## Decision and next owner

Source recipe compatibility passes; comprehensive coverage and training admission
do not. Preserve the partial12 and receive them for existing native/crop intake;
this work does not wait for TTR runtime repair. TTR owns timeout diagnosis and
strict stop-on-infrastructure-failure behavior before any separately authorized
retry. Address review sampling and coverage in the next proposal, not by discarding
the partial captures or repeating unchanged training.

Software:500 consumer recipe checks passed; no implementation changes/full Swift
build needed. Data:new capture eligibility unassessed. Integration:recipe identity
compatible, actual capture/crop path pending. Model:unassessed; previous no-promotion
decision unchanged. Skill enforced source grouping and production crop boundaries.
