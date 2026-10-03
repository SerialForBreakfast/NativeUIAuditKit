# NativeUIAuditKit — Current State

**As of:** October 3, 2026, DTM002 comparison completed (underlying results retain observation dates)
**Audience:** maintainers and agents  
**Open work:** [`Tasks.md`](../Tasks.md)  
**Finished work:** [`CompletedTasks.md`](../CompletedTasks.md)

**Live SSD storage:** seven report artifact trees now read through explicit mappings
to `/Volumes/training-drive/data/NUIAK/live/`;14.77GiB local copies removed after
verification.29pair transition corpus hash unchanged after removal;115Python and
134Swift checks pass. Keep SSD mounted for these inputs; unmigrated datasets and
YOLO exports remain local. [Operations](../reports/storage/README.md).
The inactive r5 prefix was subsequently preserved on SSD and its5.76GiB local content
reclaimed;16,334files verified after removal, active29pair hash unchanged. Internal
free space remains about21GiB at this observation. Active iOS corpora remain local
until absolute-link/export compatibility is qualified. No new model/data qualification.

**STORAGE-LIVE-03:** r7/r8/addon SSD inputs qualified; r8/addon local copies reclaimed
(10.74GiB logical content). Internal free space ~34GiB. New r7 export
`NativeUITrainer/yolo_dataset_r7_ssd03_frozen` preserves19,740members and exact labels;
default directory scanning incorrectly included5,171extra pairs. Use manifest-only
mode for frozen exports. r7 local source remains until maintainer untracks its old
generated export.48loader samples match, full r7 audit has zero integrity errors;
59Python/134Swift tests pass. Storage no longer blocks model implementation; model
quality and execution approvals are unchanged. [Handoff](../reports/work/STORAGE-LIVE-03/handoff.md).

**Localization55 / DTM002:** same24/5split,30epochs, only box objective changed to
GIoU+L1. Training paired localization fell2/24→0/24; Settings remains0/5. Raw change
improved2/5→5/5but all5abstain at fixed threshold. No adoption; warm CPU4.27ms.
68Python/134Swift checks and both legacy/new prediction parity pass. TASK-DOC-01
metadata label reconciliation complete; weights untouched. Next: controlled spatial
fit diagnostic, not threshold tuning or promotion. [Handoff](../reports/work/DIRECT-TRANSITION-55/handoff.md).

**Direct54 / DTM001:** approved24train/5development split;30epoch candidate completed.
Training change24/24, paired boxes2/24; Settings change2/5, paired boxes0/5.
Checkpoint reload parity passed; warm CPU median4.1ms excluding PNG load. Not usable
for navigation; no export/promotion/retrain.65Python/134Swift checks pass. Next controlled
experiment should address localization fit before treating this solely as domain
transfer. [Handoff](../reports/work/DIRECT-TRANSITION-54/handoff.md).

**Direct Transition53:** full-frame before/after CNN and trainer/prediction CLIs are
implemented. Strict source reconstruction yields29known-focus pairs,14changed,
without requiring tracker success. Proposal:24Fixture pairs train,5Settings development;
zero cross-group decoded-pixel overlap. Historical53preflight exited2before admission;
54above records approval and real fit.117Python/134Swift checks passed for53, including
generated-fixture optimization only. [Handoff](../reports/work/DIRECT-TRANSITION-53/handoff.md).

**Correspondence52:** pixel-feature consensus eliminates5native wrong matches and
raises correct identities43→86; positive correspondence remains0/12. It loses both
Settings departure matches, so default remains unchanged. Six native positive boxes
contain distinct stationary and scrolling feature evidence; direct paired-image
learning should be considered instead of making data admission depend on successful
single-motion tracking.108Python/134Swift tests pass; no capture/train/promotion.
[Handoff](../reports/work/CORRESPONDENCE-52/handoff.md).

**Correspondence51:** retained24reference actions and5Settings same-screen actions
replayed with opt-in90%/512px templates. Native correct identity43→89, but wrong
identity5→10 and arrival/departure still0/12. Guarded reference decisions15→30;
Settings33→36, both zero wrong guarded decisions. Candidate rejected for default
adoption and blocked from temporal learner admission.101Python/134Swift tests pass.
No live operation, training or promotion. [Handoff](../reports/work/CORRESPONDENCE-51/handoff.md).

**Reference Transition50:**24genuine reference actions replayed (12native-confirmed
moves), correcting49's limited inventory. Guarded control scores15correct/0wrong/
105abstained of120; all12scorable arrival/departure controls fail pixel correspondence.
41combined action pairs are now in the learner inventory; no complete-scene benchmark.
All9Settings raw endpoints pinned. User authorized generation/training; fresh8case TTR
campaign failed on its first case81.069s/cleanupTimedOut,0accepted,7unattempted.
Supported reconcile retained cleanup; Fixture postflight/device timed out. No restart,
retry or real candidate.106Python/134Swift checks pass. [Handoff](../reports/work/REFERENCE-TRANSITION-50/handoff.md).

**Focus Transition49 (historical two-source scope, expanded above):** paired-measurement learner and
prediction adapter integrated;78Python/134Swift tests pass. Retained17action pairs
provide76scorable controls:55correct,0wrong,21abstained with the guarded baseline.
Full-scene scoring has zero eligible actions. Two actual switches come from one
exposed Settings journey; accepted TTR pairs contain no moves. Strict preflight blocks
candidate training pending exact admission and separated move-bearing groups.
No real transition candidate was trained or promoted. [Handoff](../reports/work/FOCUS-TRANSITION-49/handoff.md).

**Family48:** current TTR planner accepts18native-button cases/66target intentions,
including three widths, two resting fills, two backgrounds and all control targets;
eight prior grid-density cases also validate.12-image grouped Markdown failure review
and all46real-result rescoring complete. Both47models miss25/25non-collection targets.
Local87e59be5source/helper unchanged; campaign export repair remains pending. TTR's
active SYNTH-01/02 now targets actual native table/tab/dialog, noncentral/aspect and
export diagnostics. Shared consumer findings published/read back; no new acknowledgment
yet. Existing61reference frames stay calibration, new membership is a proposal.
Six focused tests/reference regressions/134Swift checks pass.
[Handoff](../reports/work/FAMILY-TRANSFER-48/handoff.md).

**Augmentation47:** two matched one-epoch runs demonstrate a useful training fix.
Translation-only and translation+scale both improve synthetic exact screens425/500→
500/500, with0FP. Tested native padding positions all localize18/18, fixing the
prior0/18unaligned-shift failures. Translation-only improves real focused-body
localization1/46→8/46 while known-unfocused detections fall46→19. Adding scale reaches
9/46but increases those wrong detections to68; prefer translation-only for the next
experiment. All7fully annotated real screens still abstain; reference12remain0/12.
Real gains are collectionItems; rows0/16,primaryButtons0/4,tabs0/3 remain uncovered.
Next priority: diverse native control families/aspects and paired-content negatives,
with the same fixed challenges. Higher-resolution robustness also remains weak.
Both fits complete,512follow-up inferences replay,77Python test executions/134Swift
tests pass. Synthetic and real panels are exposed development evidence, not final
independent accuracy. [Handoff](../reports/work/FOCUS-AUGMENTATION-47/handoff.md).

**Priority46:**300fixed-model diagnostic passes identify severe alignment/scale
sensitivity. On18native development images, one-epoch localization is15/18at640and
0/18at1280. Identical640px content placed with top padding0/140/280scores0/15/0of18;
stride-aligned padding12/268restores15/16of18. Thus the initial apparent position
failure is strongly phase/alignment-dependent, not simply a center-position rule.
Ten-epoch centered result8/18versus15/18one-epoch; more unchanged fitting is not the
next priority. Training receipts confirm translate=0,scale=0,multi_scale=0. Prioritize
a controlled translation/scale augmentation comparison on already admitted data,
then diverse native control families. Reference12remain0/12full-body matches at640
and1280. All300rows independently reconstructed;30ordinary baselines reproduce earlier
decisions/scores.33Python/134Swift checks pass. Annotation review stays low priority
absent specific evidence. [Handoff](../reports/work/FOCUS-PRIORITIES-46/handoff.md).

**Human review update:** maintainer confirmed all12reference samples were perfect,
with no corrections reported. Bounds and focus sample review is complete; calibration
roles remain unchanged. [Exact confirmation](../reports/work/REFERENCE-BENCHMARK-45/human-sample-approval.json).
Earlier pending/provisional descriptions below and in immutable benchmark receipts
describe their execution-time status; this approval does not constitute exhaustive
review of all61distinct frames.

**Reference45:** fixed FSF001 misses full focused bodies on all61distinct reference
calibration images; shipped proposals locate13/61 atIoU.50. These are provisional
native labels, not independent real-app accuracy. Catalog containment diagnosis finds
a low-score focused-card candidate in30/30images, but an unfocused card outranks it
in28/30. This is not just a whole-card versus artwork-box mismatch. Guide rows get
no contained focused candidates. The existing model has not generalized to these layouts.
The grouped12-image annotator is running after removing an accidental OpenCV dependency
from its validation path. Calibration roles stay unchanged. TTR accepted six native
UIButton recipe cases/30target intentions and the eight-case grid-density plan;
rows/tabs are styled buttons, not actual native list/tab widgets. Source absence in
older33/37notes is superseded.126Python checks and134Swift checks pass; benchmark replay
matches. [Results, caveats and next substantial tranche](../reports/work/REFERENCE-BENCHMARK-45/handoff.md).

**Reference44:** strict reference/native-navigation importer now validates all36delivered
cases; all468visible-control production crops pass. One12-image grouped review is ready.
Catalog bodies grow ~23%in area; guide rows highlight without growth.72frames contain
61unique decoded images; selected12are distinct. Focused positions are center-heavy
and native Settings/tabs/dialog coverage remains missing. Calibration roles preserved;
fixed-model data-comparison preflight pins existing500evaluation members unchanged.
161Python test executions/134Swift checks pass; native Qt startup passes.
[Handoff and next substantial work](../reports/work/REFERENCE-IMPORT-44/handoff.md).

**TTR43 (historical intake, superseded by44above):** current running workspace is Developer/TVTestRig (source87e59be5), not
the stale Documents checkout. v7/v11plans and3/3local appearance captures pass:
native buttons3.23s, guide3.39s, catalog5.02s. Postflight ready/ownership clear.
Campaign export to NUIAK returns persistenceFailed; retained captures preserved.
Rich-reference36 archive received/hash-verified;36accepted pairs/72image entries/
66unique hashes pass image and reported-focus checks. Existing importer rejects
new reference inventory/native-navigation ancestry semantics. Next priority is the
strict consumer adapter plus grouped crop review, alongside producer export repair.
Guide rows are custom-highlighted; Settings rows/tabs remain a distinct coverage need.
7Python/134Swift tests pass. Shared receipt and actionable request published.
[Handoff](../reports/work/TTR-UPDATE-43/handoff.md).

**Local42 complete:** fixed FSF001 finds only 1/46 reviewed real focused bodies at
IoU .50, versus 21/46 retained production proposals. On seven completely annotated
screens it abstains on all seven; production selects four correctly. There are 46
predictions overlapping known unfocused controls and 11 unreviewed predictions on
partial frames. Synthetic success has not transferred. Next coverage must include
native rows, buttons and tabs alongside varied artwork, positions and scene layouts.
The complete iOS r8 corpus/export is verified: 19,740 members, 666 repaired training
members, all 5,200 evaluation members unchanged, zero decoded duplicates, zero pixel
copy bytes. Page-control validation support remains absent; native container versus
visible-body geometry needs an explicit decision before the next comparison.
14 focused Python and 134 offline Swift tests pass.
[Handoff](../reports/work/REAL-TRANSFER-42/handoff.md).

**Local41 complete:** exact2,000train/500evaluation full scenes admitted. One epoch
achieves425/500exact synthetic screens (85%);10epochs regresses to194/500 (38.8%),
both0FP. Complete pairs175/250→28/250. Longer fit2,392.99seconds; no time cap.
Diagnostic atconfidence.001 locates500/500targets in the one-epoch model versus
342/500in the longer model; bottom target candidates166→24of166. Training layouts
are horizontal; evaluation layouts vertical. Evidence points toward layout overfit,
not a modest threshold-only fix; retain the one-epoch result as the better baseline.
Next: diverse native positions/layouts plus real-app transfer before model delivery.
iOS666replacement members regenerated on iOS26.5 in159.50seconds; all8,958exported
labels verified. Old corpus/evaluation preserved.39Python/134offlineSwift checks
and native regeneration pass. New iOS validation coverage/training remain separate.
[Handoff](../reports/work/FULLSCREEN-EXPERIMENT-41/handoff.md).

**Local40:** full-screen v2 reads USB originals directly, keeps evaluation out of
trainer loaders and evaluates fixed-last weights only after completion. All2500
frames input-qualified;0image-copy bytes. Parent decode/check211.15s; child byte-hash
recheck22.17s. Resident preprocessing passed on actual USB train/evaluation examples.
Exact full-scene admission remains a draft; model execution still pending.
iOS repair now rendered:16/16cases across2templates×2widths×4dot counts passed;
boxes25/40/55/70×10pt, visually inspected overlays.35Python/134offlineSwift plus
the native render test pass. Next: exact full-screen admission/run and new-version
regeneration of666affected training examples, with a separate validation coverage
decision. [Handoff](../reports/work/FULLSCREEN-READTHROUGH-40/handoff.md).

**Local39:** found source-backed pageControl supervision mismatch:666training
examples measure whole-width rows, while600test examples measure intrinsic dot groups.
MediaCardGrid/ProgressActivity capture order repaired; old data preserved, fresh
render qualification pending. Conservative proposal refinement restores4/7Settings
selection but only19/46target coverage; no gain over production. Full native26scenes
validated:2,500frames/7,500controls,2,000train+500evaluation,13.87GBoriginals onUSB.
Full-screen draft prepared; exact admission, USB read-through and terminal-only
evaluation integration remain.35Python/134Swift tests pass; TTR update deferred.
[Handoff](../reports/work/CONTROL-ELIGIBILITY-39/handoff.md).

**Local38:** scored2,289recovered proposals. Geometry-only selection6wrong/1tie on
7complete screens; preserving known YOLO role exclusions2correct/5wrong versus
production4correct.35/46frames saturate at1.0; extra rectangles need whole-control
eligibility, not blanket focus scoring. iOS40page-controls at640/960/1280 remain
0/40localized atconfidence.25; AP50improves only among lower-score candidates.
Keep current configuration.9Python/134Swift tests passed. TTR update deferred.
[Handoff](../reports/work/LOCAL-DIAGNOSTICS-38/handoff.md).

**Proposal37:** same 46 real frames, fixed YOLO+raster+Vision union finds 42/46
focused bodies versus 21/46 YOLO alone; all reviewed-body recall 432/583 versus
346/583. Candidates increase 1,084→2,289, so final focus selection/precision remain
unqualified. Tight .75 IoU focused coverage improves17→35. iOS selected24-button
diagnostic: coarse family24/24, original fine role12/24; exact Cancel OCR hints3/3,
21abstentions, no fine-role gain. Bounded full-screen runner implemented/tested with
read-only preflight, exact admission/group checks and owned-child budget stops;
first real training through it remains pending.44Python/134Swift checks pass.
TTR acknowledges scorecard36 priorities and reports a new18-image reference delivery;
local dirty46dce7b still lacks grid-density source. [Handoff](../reports/work/PROPOSAL-RECOVERY-37/handoff.md).

**Priority reset / scorecard36:** shipped tvOS detector locates 346/583 reviewed
controls at IoU .50 (316 at .75), including only 21/46 focused targets, across 46
retained real screenshots. Exact role agreement is 265/320 localized controls with
mapped detector roles; 26 localized focus-only roles have no class equivalent.
Bundled production focus succeeds on 4/7 explicitly complete screens, all Settings
variants; the other three miss the focused row before classification. This is reused
development evidence, not general accuracy. Initial 3/7 score was corrected for
overlapping duplicate predictions; retained inference was replayed, not rerun.
Prioritize proposal recovery and native control-family diversity before more isolated
focus-head tuning. Full-screen diagnostic inputs prepared; bounded trainer and admitted
grouped synthetic membership still required for training. iOS 2,000-frame replay:
secondary buttons localized 292/341 but correct type 0; page controls localized 0/600;
list rows 106/700. Separate semantic and spatial remedies. 32 Python / 134 Swift tests
pass. [Results and next tranche](../reports/work/REAL-MODEL-SCORECARD-36/handoff.md).

**Transitions34:** corrected16case archive received,188member hashes verified.
Scene-unique semantic IDs are repaired; opt-in consumer accounting preserves clipped
controls separately from visible scoring membership.12pairs pass settled-bracket
checks; all4scroll_moved after endpoints remain unsettled/unverified because requested
item-1 differs from observed item-2. Fixed signals20correct/0wrong/8abstentions;
guarded stability22/0/6 on28scorable controls, all unchanged;4additional controls
are excluded after scrolling. This is custom-effect composite-card calibration,
not native-growth model improvement or qualified movement detection.101Python and
134Swift tests pass. Exact receipt and actionable readiness request published and
read back; peer acknowledgment/cleanup pending. [Handoff](../reports/work/NATIVE-TRANSITIONS-34/handoff.md).

**Brightness33:** simple brightness direction fails real unchanged rows:4correct/
41wrong/3abstained on48scorable controls. Stability/coherent-highlight guarded mean
matches existing33correct/0wrong/15abstained, including both actual switches.
Generated stress:9/14exact sign versus12/14existing/guarded. Keep existing rule;
positive-pair8/8brightness ordering is not transition reliability.48case native
artwork/wide-button/list-row coverage intent prepared. TTR reports new density
support, but local46dce7bdirty checkout lacks advertised dedfd613 and new source;
build qualification waits for source publication/synchronization.35Python and134
Swift tests passed. [Handoff](../reports/work/SETTINGS-BRIGHTNESS-33/handoff.md).

**Transfer32:** maintainer confirmed all six identities/states. Frozen FDR036 gets
6/12binary decisions correct, detects0/6focused controls; advisory6correct/5wrong/
1uncertain. Four wide-row pairs have production-clamped context; tab/button pairs
are contained and also miss. Home neighbor masking leaves both false positives;
target masking drives all four near zero. Fixed paired brightness ordering succeeds
8/8including Home, but is not a single-image detector or navigation qualification.
Pinned metadata audit: all1,000training pairs use artwork-row layout, body aspects
1.084–1.761; five new controls have aspects7.140–11.049. Home lies inside the aspect
range, so geometry alone does not explain its failure. Prioritize control-family
coverage plus matched native Home appearance diagnostics over scaling the same
generator. [Results](../reports/work/REAL-TRANSFER-DIAGNOSIS-32/handoff.md).

**Real challenge31:** approved frozen FDR036 scoring completed on two historical
Home pairs/four crops with exact production pixel parity. All four score focused:
2/4correct at0.5and0.85, both unfocused icons are false positives; zero uncertain
at0.15/0.85. This is difficult-case development evidence, not clean transfer or a
representative benchmark.46reviewed stills/31screen labels yield30spatial proposals;
eight inspected, one wrong-identity rejected and one duplicate omitted, leaving
six grouped identity checks. [Handoff](../reports/work/REAL-REFERENCE-CHALLENGE-31/handoff.md).

**Accessibility30 / tracking diagnosis:** exact producer report received and hashed.
Later correspondence stop is now explained: Hover Text reached headings instead of
ordinary rows; a separate Home profile comparison changes body geometry306×183→253×151.
Cross-profile box transfer rejected. Real-artwork reference pairs still unavailable.
Two reviewed Home stills are now prepared as candidate Photos/Music reference pairs;
changing-neighbor crop overlap8.5–10.3%keeps them out of clean transfer qualification.
Diagnostic-use continuation approved and scored in31; clean qualification stays open.
Vision alignment rounding stays2/48correct; reviewed-center diagnostic reaches36/48
with zero wrong, versus existing OpenCV33/48. The oracle uses human geometry, so keep
OpenCV tracking and Swift arithmetic. [Results and next steps](../reports/work/ACCESSIBILITY-TRACKING-30/handoff.md).

**Review29 / Settings25 implemented:** optional High Contrast evidence now feeds a
new grouped annotator batch with profile/correspondence checks, separate random and
targeted samples, paired companions and a read-only evidence viewer. Ordinary boxes
stay intact. Actual CLI/editor/Finish review/crop QA paths are covered. Real audit
still finds zero qualified native-artwork reference pairs; TTR's exact later mismatch
is resolved by30above, while FDR036 real replay remains blocked. Swift pixel-rule port
matches33correct/0wrong on48scorable Settings controls; Vision tracking drops to2correct/
46undecided. Keep OpenCV tracking. [Handoff](../reports/work/ACCESSIBILITY-ASSISTED-29/handoff.md)
and [ADR-0018](ADR-0018-Settings-Swift-Pixel-Parity.md).

**Accessibility planning updated:** published TTR45c84b6 implements optional Hover
Text analysis; maintainer priority is now High Contrast focus verification first,
with per-setting profile receipts/restoration. Display and motion comparisons follow;
Switch Control is a discovery spike, and Hover Text remains optional. See the broader
feature matrix and producer request in the linked plan. Existing Hover
Text CLI/MCP proposals found5/6retained banners, with0/2off-control detections. High Contrast helps
locate Home focus, but one outline is about10px inside each ordinary-body horizontal
edge despite0.930IoU. Use assisted observations for identity/focus support; measure
ordinary training bounds separately. Later producer status reports a correspondence
mismatch stopped acquisition, now diagnosed in30. Profile-aware review import and
Settings Swift comparison are implemented; ordinary reference-pair qualification
remains next for Native28. Third-party interiors and real model benefit remain unqualified.
[Evidence and priorities](Plans/AccessibilityAssistedFocus29.md). Source review is not
verification of the installed runtime; the adjacent local TTR checkout is older/dirty.

**Native28 complete locally, real transfer blocked:** frozen FDR036 replay500/500;
equal-size crops398/500; interior-neutralized250/500at0.85. Removing growth costs102
focused detections; retaining size/context alone after hiding interior appearance
does not suffice. These diagnostic manipulations are not a pure causal separation.
All250unfocused examples withstand0.8/1.2global brightness gain;246constructed
content-only pairs and250identical no-ops remain unfocused. Actual offline advisory
CLI passes native-crop/model parity and guarded-unavailable cases. Existing real
recording has7reviewed Settings transitions, no qualified native-artwork reference
pairs. Next: retrieve/prepare real paired evidence, score reference reliability and
FDR036 transfer, then decide advisory integration. [Handoff](../reports/work/NATIVE-FOCUS-TRANSFER-28/handoff.md).

**Native26 complete, October2:**1,250native-effect pairs,2,500screenshots and5,000
validated crops received on USB (14.54GBexports). Matched1,000-update training:
standard input433/500 versus reference-window500/500held-out synthetic controls;
FDR021 baseline283/500at0.85. Growth-preserving input corrects all67standard errors.
This establishes synthetic learnability, not isolated shading recognition or real
generalization. Common windows require a known unfocused reference. Standard model
real-frame selection regresses12/14→0/14; reject replacement. Next substantial work:
real paired/reference validation, cue ablation and scoped advisory integration.
Generation median7.61s/pair; training33.12s/33.47s. USB is adequate. All model workers
completed; existing shipped weights unchanged. Earlier runtime blockers and exact
recovery evidence are retained in the [handoff/history](../reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26/handoff.md).

**CORPUS-LIFECYCLE-27:** implemented explicit OS filtering, immutable selection,
historical replay and read-only retirement advice. Existing OS policy/membership
unchanged.58focused Python tests and134offline Swift tests pass for the tranche;
final saved-prediction report replay passes for synthetic and333retained controls.

**SETTINGS-CONTEXT-24:** source-bound visual diagnosis confirms neighbor contamination
and residual text/edge differences after scrolling. Body-only stability improves
retained correct decisions33→37, but falsely calls a generated focus-outline change
unchanged. Reject blanket body-only substitution; retain23's full-context guarded
rule.111Python/134Swift checks pass. Next model-quality step remains eight-frame
sample review/source-role decision, then admitted matched training.
[Handoff](../reports/work/SETTINGS-CONTEXT-24/handoff.md).

**SETTINGS-STABILITY-23:** fixed near-identical pixel rule increases correct recorded
Settings control decisions from4to33, with zero wrong and15abstentions across48scorable
controls (50total). Broad-highlight guard rejects a content-only false arrival and
preserves both real moves;9/9generated stress cases pass. Full-screen outcomes remain
incomplete; this is development pixel-rule evidence, not a new model or live runtime
qualification.105Python/134Swift checks pass.
[Handoff](../reports/work/SETTINGS-STABILITY-23/handoff.md).

**FOCUS-RECORDED-STRUCTURAL-22:** actual DATA64 received and verified.48appearance
cases/96frames/264production crops pass;48unique target pairs yield96proposed controls,
with one eight-frame sampled review ready. Source-role/admission remain pending.
Native OCR resolves five same-screen Settings pairs and two page changes. Fixed
brightness identifies both real moves (four correct control changes, zero wrong,
44abstentions among48scorable controls); growth contributes no decisions because
row context is clipped.16native transition pairs remain blocked by duplicate child
IDs and planned-versus-visible membership.98Python/134Swift tests pass.
[Handoff](../reports/work/FOCUS-RECORDED-STRUCTURAL-22/handoff.md).

**October2 human review update:** all seven Settings frames reviewed. Maintainer
approved20row-type corrections in378/391; all72controls now`listRow`, preserving
every bound and focus label. Original revision retained; corrected revision and
completeness validate;72/72production crops pass.7/14timing-ready actions now have
both endpoints annotated. Next: screen/control correspondence and recorded-change
scoring. [Correction](../reports/work/FOCUS-REVIEWED-TRANSITIONS-21/listrow-correction.md).

**Earlier FOCUS-REVIEWED-TRANSITIONS-21 checkpoint (review counts superseded above):** saved human revisions feed recorded-endpoint
readiness and a retrospective native-crop comparison CLI. Tracking sees pixels and
before-bounds only; after-labels/geometry supply separate, ambiguity-aware scoring.
9/9 fixed generated pixel cases pass. One retained387→391transition has9/10controls
tracked but all10decisions uncertain; correctness awaits human labels. Recording
still has14timing-ready/0fully reviewed endpoint pairs. Seven prefilled frames open
together for review.111Python/134Swift tests pass. [Handoff](../reports/work/FOCUS-REVIEWED-TRANSITIONS-21/handoff.md).

**FOCUS-READINESS-20:** fixed measured-body assembly visibility-policy replay;
complete campaign now feeds a non-executable matched-data comparison, retaining
target-pair aliases, competitor label conflicts and evaluation membership. Retained
25pairs replay through1300candidates;333evaluation controls unchanged. Recording
audit accounts for166actions/14timing-ready/0fully annotated pairs; seven existing
reviews would complete endpoint annotation for seven actions, not prove navigation.
118Python/134Swift tests pass. Structural originals still await delivery; no new
training, capture, admission or model-quality claim.
[Handoff](../reports/work/FOCUS-READINESS-20/handoff.md).

**FOCUS-CAMPAIGN-INTAKE-19:** one campaign command now verifies exact planned
membership, measured-body bounds, visibility and production crops, then prepares
one family/focus-balanced annotation queue. Resume preserves human edits and rejects
changed inputs/outputs.103Python/134Swift tests pass; generated48case integration
checks192crops and eight-frame editor/Finish review. Legacy50frame batch unchanged.
Software verified, not new corpus/model improvement: actual producer48case pixels
remain undelivered as of04:17UTC; next human step follows that intake.
[Handoff](../reports/work/FOCUS-CAMPAIGN-INTAKE-19/handoff.md).

**FOCUS-LOCAL-PLAN-18:** updated local helper now passes actual48case planning,
consumer hash parity, deterministic reorder/repeat and five invalid-input checks.
Coordinator/Simulator readiness pass, Fixture not checked. Retained Vision retry
still fails, now precisely before_preflight/access_denied/NSCocoaErrorDomain513.
No new sidecar/capture/training. Producer reports48appearance+16transitions complete
locally; captured data delivery still pending. No producer build requested.
[Handoff](../reports/work/FOCUS-LOCAL-PLAN-18/handoff.md).

**FOCUS-INTERRUPTIONS-17 completed:** corrected interruptionr2 received,168manifest
files verified;20stable capture brackets and447production crops pass.98covered/
removed bodies excluded;8frames report not settled;20files contain6unique screenshots.
Failed recovery and unknown overlay-underlay focus remain explicit. Diagnostic only,
no training admission/model change.93Python/134Swift tests pass. TTR02:16:17UTC reports
four structural families passed and remaining44appearance cases collecting; their
proof originals and published source repair are still needed for consumer acceptance.
No producer build requested. [Handoff](../reports/work/FOCUS-INTERRUPTIONS-17/handoff.md).

**FOCUS-VISIBILITY-16 completed:** new sealed native review projections exclude
explicitly hidden/zero-alpha controls and block focused/invisible conflicts; partial
alpha and native scroll metadata retained. Legacy50frame batch validates unchanged.
84Python/134Swift tests pass. TTR acknowledges source-only/local-build policy;
01:12:19UTC status says recovery passed, first composite-card validation failed,
zero accepted pairs. Configured local TTR master46dce7b and fetched simulator-harvest
967d585 lack the self-service compiler, including working tree. Requested exact
branch/commit (commit/push only if needed), not a build. No local TTR build attempted
from the wrong source; no model or corpus change.
[Handoff](../reports/work/FOCUS-VISIBILITY-16/handoff.md).

**FOCUS-HANDOFF-15 verified:** TTR's self-service source checkpoint is received;
17files match hashes, example request matches producer signed-CLI receipt, all four
structural examples pass consumer parsing. Source adds deterministic planning,
unattempted-only resume and grouped local export; no new pixels. Running Maximum-mini
helper is not the reported candidate: help lacks plan/generate/resume and an actual
plan-only call exits64 invalidArgument. The build/candidate request was withdrawn by
maintainer direction: sync source through Git, build and produce planning evidence
locally; only request commit/push and revision identity if needed. First-four
capture/scroll proofs remain open. Producer
HTML selects first verified case per family, not a random sample; retain NUIAK's
seeded annotator review. Receipt/feedback published and read back; no app replacement,
capture, training or admission. [Handoff](../reports/work/FOCUS-HANDOFF-15/handoff.md).

**FOCUS-STRUCTURE-14 completed for review:** structural-v3 source archive received,
81members verified;48appearance and16transition recipes pass consumer checks.
Four structural kinds now flow through the existing diagnostic review caller;
hidden/alpha/scroll metadata is validated without inventing missing observations.
61Python/134Swift tests pass. Matrix distinguishes36custom-growth and12native-image
cases. No new captured data or training: first four measured family proofs, producer
digest parity and clipped-scroll membership remain open. TTR is independently
implementing self-service generation/export. Prior six sampled checks are approved.
[Handoff](../reports/work/FOCUS-STRUCTURE-14/handoff.md).

**FOCUS-INTAKE-13 completed for review:** received/hash-verified25new pairs/50frames,
all389manifest members and1,300production crops pass.130unique crop pixels,68new
versus prior six;50new target crops but only one layout/position. Six prefilled
checks ready together; no training admission. Full TTR48pair structural proposal
read and aligned. Opposing gain/loss scene rule yields7/12correct,5abstentions
versus arrival-only11/12; strict background resolution abstains on all12. A whole
screen with two content-color changes still falsely reports a switch through both
actual CLIs. Reject deployment; preserve FDR021.93Python/134Swift tests pass.
October1PDT: maintainer approved all six sampled alignment checks; saved revision
records6reviewed/44blocked. No source-role migration/training admission implied.
Next structural proofs (composite/row/icon/hero), not another same-slot training run.
[Handoff](../reports/work/FOCUS-INTAKE-13/handoff.md).

**FOCUS-ALIGNMENT-12 complete for review:** opt-in translation-aware offline CLI
recovers the161pxscroll (158.44pxestimated). Equal visible-support follow-up gives
18/18retention directions and11/12eligible frame directions, one abstention;
Home enlargement defeats rigid texture matching (0/6versus prior6/6). Two generated
content-only cases still cause false changes: no deployment or FDR021replacement.
Two2996case replays,34Python/134Swift tests,21generatedCLI cases,1045exact matched
pixel-decision replays. [Results](../reports/work/FOCUS-ALIGNMENT-12/results.md).
Producer23:35:36UTC reports25newpairs/50frames delivered,31/48total,17runtime-blocked;
coverage request acknowledged with proposed48pair structural successor. No receiver
receipt/admission for the25in this local alignment tranche. Next intake/coverage
assessment and full-scene focus-change corroboration.

**FOCUS-PAIRED-11 complete:**2996retained contrast/no-op cases,1702native fixed-window
crops. Growth finds6/6Home arrival contrasts versus0/6independent resizing (reused
screens, not independent tests). Frozen combined rule6/12eligible frame directions;
separate unchanged-threshold clipping follow-up12/12versusFDR021transition7/12.
Only sixpairs/nineframes. Scrolling retention row gives a wrong direction; movement,
content replacement and illumination prevent deployment. Next: translation-only
alignment/rejection, preserve scale, stress unchanged focus. No neural fit or model
replacement.23Python/134Swift tests pass;7CLI tamper rejections; primary replay exact.
[Results](../reports/work/FOCUS-PAIRED-11/results.md).

**FOCUS-TRANSFER-10 complete; both changes rejected:** FDR03310×relative emphasis
finds4/12artwork but29FP; FDR034native aspect-fit finds7/12but68FP and0/3focused
buttons. Both100updates; no eligible checkpoint. FDR032matched control3/12/25FP;
FDR021remains2/12/3FP and is not replaced. All1895production inputs replay pixel-exact,
333evaluation members unchanged,30saved evaluations replay exactly.46Python tests,
actual CLI2positive/6negative checks, offline build/134Swift tests pass.
Concrete next coverage: composite cards, wide rows, varied icon/hero arrangements,
actual focus positions and action-linked measured growth. Published TTR request
`nuiak-20261001-transfer10-coverage`; planning feedback, not new capture dispatch.
No further unchanged training or human redraw of accepted pairs recommended.
[Results](../reports/work/FOCUS-TRANSFER-10/results.md).

**FOCUS-CAMPAIGN-09 training comparison completed:** six sampled screens approved
without corrections; maintainer explicitly assigned six producer-calibration pairs
to consumer development-training.12targets admitted; original records preserved.
FDR031control vsFDR032added data each completed100updates: artwork3/12vs3/12,
FP24vs25, unique12/14both, retention18/18both. New model learns12/12added crops
but does not improve real-screen transfer. No eligible checkpoint; preserveFDR021
(artwork2/12,FP3).20evaluations replay exactly;333evaluation members unchanged.
42Python tests, actual CLI positive/six negative checks, offline build/134Swift tests
pass. [Results](../reports/work/FOCUS-CAMPAIGN-09/results.md).
TTR22:14:46UTC confirms backup receipt/capacity restoration; remaining42captures
blocked by screenshot timeout/runner cleanup, not consumer review or storage.
Consumer role-migration receipt published/read back; no new capture/export.
Earlier preparation snapshots below are historical, not current blockers.

**TTR status, October 1 at2:26PM PDT:** producer reports new six-pair/12frame
standard owned-artwork campaign completed, including host brackets, PNG binding
and measured growth. FOCUS-CAMPAIGN-09 now verifies archive/95members,12native
brackets and312production crops. Consumer composition pairing/selection-exclusion
compatibility repaired. Six prefilled sample checks and explicit source-role
decision remain before admission; all six producer manifests say calibration.
Conditional comparison is1550vs1562training controls, unchanged333evaluation.
Seven missing real Settings endpoints prepared with72unconfirmed proposals.
73Python tests, offline build/134Swift tests and native Cocoa doctor pass.
This is new evidence
to evaluate, not repaired timing for the previous48diagnostic pairs. Prior metadata
correction receipt acknowledged and sender cleanup reported. No new training.
[Handoff](../reports/work/FOCUS-CAMPAIGN-09/handoff.md).

**TEMP-FOCUS-02 retained spike completed:** fixed brightness rule matches all109
Settings development/retention controls, equal toFDR021; mixed315control application
produces58FP versus3. Settings-oracle hybrid does not improve frame selection;
agreement-only loses one correct frame.9static Settings pairs show clear brightening,
but only54/112Fixture pairs do; all48white-artwork pairs remain below the fixed delta.
No neural training or runtime deployment.14/166recorded actions pass timing checks,
none has both endpoints in accepted reviewed annotations; genuine transition test
requires paired endpoint review and runtime context/matching validation.
Artwork correction independently verifies48recipe bindings/96PNGhashes; host capture
correlation remains unavailable. [Results](../reports/work/TEMP-FOCUS-02/handoff.md).

**FOCUS-ARTWORK-08 complete for review:** composition-v2 and explicit diagnostic
pair intake integrated. All48 target pairs/96 frames/2,496 production crops pass
diagnostic QA; all48 owned targets meet the white descriptor in both states and
have focused competitors.96 unique target crops conditionally proposed; original
source roles and333 evaluation controls unchanged. Eight balanced prefilled review
samples ready, no human action assumed.129 Python tests and Swift build/134 tests
pass. Admission waits on specific index-hash/capture-binding evidence and sampled
acceptance, not renderer implementation or another unchanged run.
TTR isolated observer proof received:96/96 crop PNG/RGB-input hashes match local
crops; supplied scores recount TP32/TN40/FP8/FN16. All misses dark, all FP light;
descriptive, not causal or held-out evidence. No local model execution/promotion;
installed app path not qualified. [Handoff](../reports/work/FOCUS-ARTWORK-08/handoff.md).

**FOCUS-READY-07 complete for review (historical receipt stage):** FDR021 observer archive delivered and TTR
copied/verified receipt received; not loaded or promoted. Offline readiness CLI and
actual trainer preflight tested:106 Python tests, Swift build and134 Swift tests
pass. D1 has350 distinct crop candidates and3,706 duplicate observations; all30
artwork negative target frames lack a focused competitor, and no matched white
artwork additions qualify. Baseline1,550 training/333 evaluation controls and source
weights remain unchanged. TTR's24-asset/48-pair proposal received; rendering remains
unimplemented. No new model execution or admission.
[Handoff](../reports/work/FOCUS-READY-07/handoff.md).

**FOCUS-APPEARANCE-06 complete for review:** D1 received and native composition
compatibility implemented, including previously omitted tabs.78 target pairs,
156 frame records,4,056/4,056 production-body crops pass; six prefilled sample frames
ready.132 Python and134 Swift tests pass. D1's complex layouts do not close the
appearance gap:0/1,530 unfocused artwork observations meet the retained white-body
descriptor. Calibration/source ancestry preserved; no admission or model execution.
Next: targeted white/logo/blank artwork proposal, not another unchanged run or broad
human redraw. [Handoff](../reports/work/FOCUS-APPEARANCE-06/handoff.md).

**FOCUS-VISUAL-05 complete:** four frozen/partial-backbone × detail/context runs;
no eligible checkpoint. Terminal artwork0/0/3/2of12, FP3/33/24/23,
unique11/7/12/10of14; all retention18/18. All39 evaluations replay exactly;
initial predictions match, partial tails change, BN/prefix remain frozen.
78Python tests and offline Swift build/134tests pass. PreserveFDR021, no export.
Retained-pixel audit identifies0/554 mostly-white unfocused training collection
items versus57/181 development artwork negatives;21/24 FDR029 false positives
meet that diagnostic descriptor. Not causal proof. Next inventory existing TTR
composition delivery for matched appearance coverage before new collection/run.
[Handoff](../reports/work/FOCUS-VISUAL-05/handoff.md).

**FOCUS-CONTEXT-04 completed:** FDR024/025/026all fit1550/1550training controls,
but no eligible checkpoint. Terminal local/geometry/scene artwork0/1/1of12,
FP10/9/24,unique7/9/11of14; baselineFDR0212/12,3FP,12/14. All retain18/18.
All34saved evaluations replay exactly; identical initial predictions. Increased
head capacity and this frozen context recipe fail transfer; annotation improvement
alone is insufficient. Next: bounded learnable visual representation comparison,
not another unchanged head or bulk-data run. No export/promotion. Tranche approval
adopted and this three-run scope completed.
[Diagnosis](../reports/work/FOCUS-CONTEXT-04/handoff.md).

**FOCUS-WEIGHT-03:** approved FDR023weight-control run completed on MPS
(1000updates,31.301training seconds). Selected update275reducesFP3→2but regresses
TP16→13,unique-correct12/14→10/14and artwork2/12→1/12vsFDR021; retention18/18.
All40snapshots replay correctly; no snapshot improves artwork beyond2hits.
Comparison rejected; FDR021retained. Correcting source budgets alone is insufficient.
Representation follow-up now completed above; no export/promotion.
[Outcome](../reports/work/FOCUS-WEIGHT-03/handoff.md).

**FOCUS-GROWTH-02:** explicit baseline-budget repair and experimental context-input
CLI complete. Retained1883controls across693scenes prepared with existing detail
crops, shared scene transforms, masks and current geometry;32/32growing pairs retain
growth.152missing historical bounds recovered without relabeling.57Python tests and
offline Swift build/134tests pass. Reweighted1550/333cached protocol passes actual
trainer configuration; new run approval is the only execution blocker. No retained
model run, fusion model or CoreML export. [Handoff](../reports/work/FOCUS-GROWTH-02/handoff.md).

**FOCUS-GROWTH-01:** analytic replay of112same-element comparisons confirms scale
normalization.32interior growing controls: median raw16.7%width/18.1%height growth
becomes0.09%/0.05%after current resize. Viewport-scaled context preserves growth;
recommend experimental detail+shared-scene+candidate-geometry input after weighting
repair. Static source data already retained; no TTR build needed. No changed crops,
model execution or claim of learned growth. [Analysis](../reports/work/FOCUS-GROWTH-01/handoff.md).

**SYN-13 offline diagnosis:** FDR022contains a weighting-policy confound: OS-native
loss mass9.3%→40%, prior fixture70.7%→27%, added fixture13%, human20%unchanged.
Recomputing the old native corpus alone changes all790weights. Cache label/shape/
hash checks pass. Correct proportional crops normalize absolute growth; retained
feature neighborhoods suggest weak artwork focus separation but do not prove cause.
Prioritize weighting-continuity repair/control before a backbone/context change.
No new model execution or implementation change. [Diagnosis](../reports/work/SYN-13-DIAGNOSIS/handoff.md).

**SYN-12-EXECUTION (October 1, 2026 PDT):** all12new sampled frames/90controls
human-confirmed, unchanged annotations; prior SYN-06five-frame acceptance retained.
Exact admission/reassembly passes:564native additions,1550training controls;
333evaluation records exactly unchanged,196human controls retain20%loss mass.
764blocked candidates and52source-quarantined controls remain excluded. Related
procedural-renderer group is training-only, not independent evaluation. Encoding
approved and completed:564crops,3.224encoder seconds on MPS,1,520,229bytecache,
encoder unchanged. Separately approved FDR022completed1000updates in31.217model
seconds: no eligible checkpoint. Terminal TP15/27vsFDR02116/27, FP6vs3,
unique-correct10/14vs12/14, retention18/18unchanged. Artwork hits2/12unchanged;
rows regress7/7→6/7. Data-only comparison fails; FDR021preserved, no export,
promotion or automatic retry. Existing metrics replayed over all saved predictions.
[Handoff](../reports/work/SYN-12-EXECUTION/handoff.md).

This page is the living snapshot. If it disagrees with `AGENTS.md` or `README.md`, fix those to match this file.

**REVIEW-QT-01:** supported annotation launches automatically probe actual Qt
plugin loading/QApplication creation in a bounded child before opening a batch.
Shared verified plugin cache and `--doctor` are the canonical path; no reinstall
or per-batch Qt workaround.33Python tests, real Cocoa/failed-launch checks and
Swift build/120+14tests pass. Current annotation window left running; corpus and
model state unchanged. [Guide](AnnotationStartup.md).

**SYN-11-REVIEW:** safe five-image artwork review launched; pending native3/palette4
queues unchanged. Repaired the annotation plugin cache's missing relative Qt
framework lookup without modifying installed dependencies;26editor/cache tests and
Swift build/120+14tests pass. Unapproved exact564-addition proposal is weighting-
feasible:1550training controls,333evaluation unchanged, native80%/human20%mass.
Human sampled review/source-role acceptance and exact admission remain necessary;
no encoding or training. [Handoff](../reports/work/SYN-11-REVIEW/handoff.md).

**SYN-10-ENCODING:** native-body feature encoder and actual trainer integration
implemented;89generated tests and offline Swift build/120+14tests pass. Reuses all
986baseline features through the original928+reviewed58cache chain, then appends
exact admitted native members. Separate encoding/output-budget and one-run approvals;
no automatic encoding from training. Actual retained preflight passes configuration
and correctly blocks on missing admission, features and run approval (exit2).
No saved revisions in the SYN-07native3/palette4 or SYN-09safe5review queues;
564unique candidates remain unadmitted. No new model run or weights. TTR's existing
78genuine variant request remains separate; no new transport/geometry requirement.
[Handoff](../reports/work/SYN-10-ENCODING/handoff.md).

**SYN-09-ARTWORK:** received356verified members,14new recipe bundles/42captured pairs/
756production crops;77new unique images. Combined native audit now564unique candidates
(137focused/427unfocused),318more than SYN-08.52reserved-source controls excluded;
764duplicate/incomplete/clipped/protected candidates held. Baseline986training and
333evaluation members/weights unchanged. All30representative recipes now have producer
proof; current per-slot capacity162/240 requires78genuine extra layout/content targets,
not duplicate captures. Final five-frame human queue excludes reserved dark-parent
source. Native-body protocol reader supports this8.46MBassembly under a32MiBbound;
26assembly/44fixture tests and Swift build/120+14tests pass. Actual trainer preflight
blocks execution correctly; no admission/encoding/training. Next: sampled acceptance,
exact membership, native encoding/trainer integration and a budgeted comparison.
[Handoff](../reports/work/SYN-09-ARTWORK/handoff.md).

**SYN-08-ASSEMBLY:** measured-body adapter integrates existing assembly and trainer
dry-run without recapture/recrop. Of624retained body crops,16reserved-source controls
are excluded before decode;608candidates yield246unique candidates (66focused,
180unfocused),362reasoned exclusions. Corrected generation-only false conflict
comparison while preserving original native records and old review seals. All986
baseline training and333evaluation members and existing weights remain unchanged.
Actual admission remains empty; encoding plan is prepared, not executed. Next:
sampled native/palette geometry acceptance and exact source-role membership, remaining
coverage-driven generation, then a separately budgeted changed-data experiment.
No model execution or quality claim. [Handoff](../reports/work/SYN-08-ASSEMBLY/handoff.md).

**SYN-07-READINESS (2026-10-01 UTC):** native configured button/row/tab/dialog repair
received and accepted through unchanged consumer intake:16captured pairs, six scenes,
32frames,154/154production crops;195manifest members verified. Representative overlays
visually checked. Three prefilled native-review images await human verification;
prior five-image artwork review remains accepted. New offline readiness CLI joins
saved review/crops, retained1,319crop inventory,72recipe lineage and30recipe catalog.
All60collection slots bind exact recipes;9producer layout signatures and recurrent
motifs are not independent train/validation sources. No roles reserved or training
admitted. Core geometry capability now exists across four families; remaining
artwork coverage, source-role binding and native assembly/encoding precede
changed-data training. Nine new and25corpus tests pass; Swift build/120+14tests pass.
[Handoff](../reports/work/SYN-07-READINESS/handoff.md).

Same-tranche palette follow-on: nine scenes/26captured pairs/320crops pass;174more
member hashes verified. Across corrected image/native/palette deliveries:63pairs,
77unique image files,624body crop observations. Four exact-image cross-recipe
overlaps match producer evidence and must stay grouped; no independent split implied.
High-contrast native controls and long/duplicate rows are now delivered. Remaining
artwork combinations are TTR's next action; consumer assembly remains local work.

**SYN-06-BODY (2026-10-01 UTC):** corrected native/custom image-body intake integrated
without altering legacy review batches.231producer member hashes verified;8scene
bundles/21captured pairs;150/150production crops from measured bodies,60unsupported
observations explicitly unavailable. Original growth box now520×496vs440×420wrapper;
representative overlays inspected and a small prefilled human queue prepared.
**Human acceptance:** all5sampled frames/20controls confirmed correct, including
negative cases. Saved human revision and snapshots verified; bounds/classes/focus
unchanged from crop-QAed proposals. [Receipt](../reports/work/SYN-06-BODY/human-acceptance.md).
Native buttons/rows/dialogs and tab-parent geometry were unsupported in this archive;
the subsequent SYN-07-READINESS delivery above supersedes that blocker.
44fixture,46TTR,136human tests; offline Swift build and120+14tests pass. Diagnostic-only;
human/corpus/source-role acceptance remains separate. No training or model change.
[Handoff](../reports/work/SYN-06-BODY/handoff.md).

**SYN-05 offline continuation (2026-09-30 PDT):** plan-driven local intake now
resumes completed bundles without recropping or overwriting human edits. Retained
image/rows/tabs replay:3bundles,5captured pairs,60crops; second invocation reused all3.
Thirty recipes yield14theme/seed-normalized layout/content signatures in one
conservative connected source group; no independent validation group established
or role reserved. Markdown side-by-side wrapper/annotation overlays explicitly
hold rendered-body acceptance.37fixture tests,136human tests, offline Swift build
and120+14Swift tests pass. No capture, training or model change.
[Usage and limitations](../reports/work/SYN-05/handoff.md).

**SYN-03 consumer proof:** five current TTR image/row/tab pairs accepted,60/60
production crops generated. **Human-review correction:** the native-image focused
tile grows beyond its exported wrapper box. Affected growth samples are held from
training; crop generation/schema checks do not establish rendered-body alignment.
[Producer repair request](Requests/TTR-Rendered-Control-Bounds.md).
Earlier software proof remains valid:60/60
production crops generated; five unique prefilled audit frames from ten originals
(two exact duplicate aliases excluded). All79emitted-pack members verified unchanged.
Rows retain budget halt and one unattempted case. Deliberate corrupt sidecar rejects
at alias consistency; direct semantic validation independently rejects out-of-frame
bounds. Legacy nested-tab primaryButton restriction repaired to preserve current
secondaryButton exports. No labels inferred from selected state, no training admission.
Thirty source recipes map60slots; they are not all rendered-qualified. Swift build,
120Swift Testing+14XCTest,46TTR,26fixture,12bundle,135human tests pass, plus installed
editor offscreen smoke. [Handoff](../reports/work/SYN-03/handoff.md).

**Earlier SYN-02 consumer integration:** three TTR contract/catalog archives received and
all36 listed member hashes verified. Optional native semantic inventory now validates
inside sidecar2/3 intake, preserving legacy absence and raw observations. Exact
fabricated examples,15new consumer tests,43TTR tests,12bundle tests and three
unchanged retained pairs pass; offline Swift build and120+14tests pass. New04:10:09Z
catalog supplies eight original recipes/ten sources, mapped to all60 planner slots.
Zero roles reserved or samples admitted: shared ancestry remains open; representative
emitted-image proof is now completed above. [Earlier handoff](../reports/work/SYN-02/handoff.md).

**TTR progress reconciliation,04:07UTC:** fresh producer status04:00:43Z reports
concrete `semantic_inventory` implementation, measured UILabel/image regions and
native accessibility properties;93tests passed/3disabled plus Fixture compile pass.
At that check, contract/source metadata were read directly from published archives;
SYN-02 above subsequently completed local receipt. Fabricated examples enabled offline consumer
mapping; matching captured examples remain pending. Four recipe families share
`shared_fixture_training_canvas`, so they do not establish independent train/validation
sources. Both INTAKE-AUDIT-01 and SYN-04 acknowledged by TTR. [Details](../reports/work/INTAKE-AUDIT-01/status-20261001-0407.md).

**Corpus planner, SYN-04 (2026-10-01 UTC):** offline planner revalidates the retained
1,319 crops/395 native pairs and generates prioritized artwork/tab/row/button
requests with separate intended training/validation sources. Default first-wave
targets total480 pairs over60 slots, not qualification thresholds or captured data.
All60 remain unbound pending exact reviewed recipe ancestry. Known transitive
source/content conflicts block proposals; no existing role, hold or gate changed.
[Handoff](../reports/work/SYN-04/handoff.md).

**Intake audit update, 2026-10-01 UTC:** existing annotation flow now supports a
reproducible random sample plus separate structural-exception queue, prefilled from
immutable reviewed annotations or producer proposals without inheriting approval.
Consumer software/retained replay verified; emitted TTR semantic contract pack still
pending. No corpus admission or model change. [Handoff](../reports/work/INTAKE-AUDIT-01/handoff.md).

**Workflow reconciliation, LOCAL-FIRST-01 (2026-09-30 PDT):** ADR-0012 adopted as
local-first/asynchronous workflow; ADR-0013 is a queued wrapper around the existing
production library, not a new inference stack. ADR-0014/0015 are comparative model
hypotheses, not approved replacements. One concise tranche report and automated
batch checks replace repetitive helper paperwork; data reservations, parity and
execution gates remain intact. [Delivery contract](Plans/LocalFirstDelivery.md).
CLI/MCP is now delivered below; focus corpus remains the model priority.
No software, data, model or TTR runtime changed by that documentation tranche.

**LOCAL-TOOLS-02 completed for review (2026-09-30 PDT):** nativeui-audit doctor,
scan, scan-batch and stdio MCP wrap the existing production session. Bounded roots,
input accounting, model identity, OCR/focus health and timing are exposed; heuristic
audit findings remain warnings. 120Swift Testing +14XCTest and4real-process tests
pass; offline build warning-free. Real iOS/tvOS fixture smokes pass, including warm
reuse and intentional corrupt input. M4 observation: iOS977ms cold/138ms warm,
tvOS1007ms cold; not a performance or accuracy gate. Shipped weights unchanged;
no TTR/agent configuration installed. Next: FOCUS-CORPUS-03 coverage-driven assembly.
[Usage](../Tools/NativeUIAuditCLI/README.md), [handoff](../reports/work/LOCAL-TOOLS-02/handoff.md).

**FOCUS-CORPUS-03 — local audit delivered; production generation incomplete:**
Follow-up recheck reproduces the inventory exactly; all eight indexed inputs remain
unchanged. [Readiness decision](../reports/work/FOCUS-CORPUS-03/readiness-decision.md)
provides the explicit family/split matrix and NO-GO for production assembly.
Forty native pairs have separate Settings scene names and are not silently credited
to settingsList. SYN-01 coverage specification is delivered; new producer recipe
membership remains missing. Keyboard is a separate capability gap, not a blocker
to a bounded supported-family pilot. No unchanged training approval is requested.
1319 baseline crops pass file/pixel/role checks (986training,315development,18retention);
395native training pairs plus196static human crops, not591pairs. All3retained native
diagnostic pairs pass native bracket/geometry and production crop replay. No new
admission or model execution. Reassembled current-runtime trainer preflight preserves
all data/selection/weights and is blocked only on new-run approval; this is baseline
reusability, not production readiness. Twelve tab/nested-tab pairs are present under
primaryButton labels; explicit keyboard support absent.64held pairs remain held.
TTR coverage archive received:32native-button pairs need no artwork-only recapture;
12native-image pairs retain body-specific geometry gaps. Source/layout-bound new
production campaign and keyboard/parent-state contracts remain open; no bulk capture
dispatched. [Audit and remaining scope](../reports/work/FOCUS-CORPUS-03/handoff.md),
[collection assignment](../reports/work/FOCUS-CORPUS-03/collection.md).

---

## Shipped

**Three-pair runtime proof complete,2026-09-30PDT:** local new TTRf2d9728c and
installed Fixture062ddfe7 captured3/3approved pairs; independent receiver hashes
44files/10,515,400bytes match. All3native-label brackets and6production crops pass.
Direct campaign export to project failed; supported app-owned export then verified
receipt succeeded without recapture. Target9026ECA9postflight ready/ownership clear,
Fixture settled/responsive. Initial no_sample resolved when Simulator display opened.
Diagnostic-only;15other targets excluded by approved cap; no training/promotion.
[Evidence](../reports/work/FOCUS-R2-LIVE-11/handoff.md).

**Historical TTR coordination check,00:26UTC (capture superseded by proof above):** peer snapshot00:19:36UTC reports
manifest repair plus corrected0.3.1/build7available. Capture track now awaits
consumer verification, not producer implementation. No new local runtime check,
download or capture was performed. FDR021RGB consumer request remains published
without peer acknowledgment; it postdates the current peer snapshot. Local333/333
production parity remains passed; TTR candidate loading/deployment remains unverified.

**FDR021 runtime repair,2026-10-01UTC:** production CPU parity now PASSES333/333;
exact model-input RGB hashes match the frozen training convention, maximum score
error0.0000341 with zero0.5/0.70/0.85decision changes. Candidate metadata
`inputPixelContract=png-straight-rgb-v1` opts into lossless in-memory PNG straight-RGB
handling; absent metadata keeps shipped code path, unknown contracts fail closed.
Fresh complete FP32 package3,788,293bytes.12Python/112Swift tests/build pass.
No bundled model replaced. TTR candidate loader/build is not yet verified; ask for
explicit contract enforcement and loaded artifact identity before observer testing.
[Runtime handoff](../reports/work/FDR021-PIXEL-PARITY/handoff.md).

**Historical FDR021 initial CoreML export,2026-10-01UTC (superseded above):** experimental complete FP32 model built and
compiled,3,788,242bytes. Direct RGB CoreML CPU matches all333frozen development/
retention crops(max error0.0000341; no0.5/0.70/0.85decision changes). Production
Swift path DOES NOT pass(max0.418649);63crops have partial alpha, exposing saved-RGB
versus opaque-buffer handling. FP16 also failed. No shipped asset replaced or TTR
deployment. Next: scoped alpha compatibility repair and production parity.
[Export handoff](../reports/work/FDR021-COREML/handoff.md).

**FDR021completed,2026-09-30:** approved58-control addition produced an eligible
experimental checkpoint at update775. Same315/18evaluation members: unique-correct
frames9/14→12/14, positive hits14/27→16/27,3FPunchanged, retention18/18. Artwork
hits1/12→2/12but artworkFP2→3; Photos FP removed at0.85, still uncertain negative.
No production qualification/promotion. The selected head requires the pinned encoder;
subsequent complete CoreML export is recorded above. Production parity precedes
observer integration; artwork coverage remains a major gap.
[Execution handoff](../reports/work/FOCUS-REVIEW-CONTINUE-16/execution-handoff.md).

**Next focus experiment prepared,2026-09-30:** source review verifies existing
whole-session training reservation; no independent-transfer claim. Exact addition
proposes58focus-control crops (4positive/54negative), excludes21text/decorative crops
without deleting annotations. Projected986training controls;315development/18retention
unchanged. Weights checked through existing implementation. This proposal was
subsequently approved and executed as FDR021; see current result above.
[Decision](../reports/work/FOCUS-REVIEW-CONTINUE-16/source-admission-review.md).

**Human review received,2026-09-30:** four confirmed frames,79controls,79distinct
production crops; crop QA completed79/79 with no audit issues. Exact protected and
baseline crop overlap checks found none (not proof of source independence).
User confirmed Ghost focused in frame598; new correction revision preserves the
original and changes only that label.79crops reverified unchanged;4focused/75unfocused,
one focused per frame. Subsequent58-control admission and FDR021execution complete.
Evidence: FOCUS-REVIEW-CONTINUE-16/ghost-confirmed-qa.

**Review continuation,2026-09-30 — FOCUS-REVIEW-CONTINUE-16:** the previously missing
review→crop QA→explicit admission→changed-data trainer adapter is implemented and
verified. Actual retained preflight preserves928train/315development/18retention,
the initial preflight had zero admitted new controls. Human review, crop QA and
subsequent approved execution now complete.73software tests plus15execution tests,
offline build and109Swift tests pass. Model result is recorded above.
[Handoff](../reports/work/FOCUS-REVIEW-CONTINUE-16/handoff.md).

**Retained focus work,2026-09-30 — FOCUS-RETAINED-NEXT-15:**702retained image
files/739frame observations screened against40reviewed frames.625unreviewed
candidate pixels are mostly nearby states, not625new screen designs. Four
Paramount contrast frames now reviewed with79verified crops; admission remains
pending. All1261FDR020 training/development/retention crops verified;
human training has6focused artwork and0focused buttons. Photos/Home/Settings
also occur in the supplement recording: source-session identity alone cannot
establish independence. Frozen315development/18retention remain unchanged.
Changed-data proposal, not a training launch; shipped models unchanged.
[Handoff](../reports/work/FOCUS-RETAINED-NEXT-15/handoff.md).

**MPS batch comparison completed,2026-09-30:** TRAIN-MPS-COMPARE-14 completed
four two-epoch trials in11m52s. Batch16delivered7.67%higher first-epoch throughput,
but MPS driver allocation rose5.62→10.60GiB and minimum available RAM fell to
3.374GiB. Retain batch8default on this24GiB M4. No quality equivalence, full-run
speedup or promotion claim. Next priority returns to focus coverage/validation.
[Results](../reports/work/TRAIN-MPS-COMPARE-14/handoff.md).

**MPS diagnostic completed,2026-09-30:** TRAIN-MPS-DIAG-13 attempt02 completed
two epochs on512train/64validation inputs in189.832s, exit0. Training batch
intervals80.3%of epoch time; OHEM/checkpoint costs minor. Minimum sampled available
RAM6.376GiB; all guards held after user freed memory. Diagnostic weights isolated,
shipped models unchanged; no quality/speedup claim. Next proposed experiment:
bounded matched batch8/16MPS comparison, now completed above. Prior30Python/
123Swift/build passes apply to packet13.
[Handoff](../reports/work/TRAIN-MPS-DIAG-13/handoff.md).

**Trainer software,2026-09-30:** TRAIN-OHEM-TIMING-12 repairs rectangular OHEM
replacement using equal-output-shape slots and adds optional host-wall timing.
43Python tests,123Swift tests and offline build pass. No model/run changes or
measured speedup. Next compute step remains a separately approved bounded MPS
experiment. [Handoff](../reports/work/TRAIN-OHEM-TIMING-12/handoff.md).

**Offline productivity tranche,2026-09-30:** optional annotation preview filter
reduces retained Vision244→193proposals without losing44reviewed matches; default
off, human time benefit unmeasured. Existing-score report reproduces FDR020strata
and9/14complete-frame unique decisions; first3scores remain unavailable. Run013
CSV/log confirm62.8hours and0workers; source audit flags rectangular-OHEM metadata
risk and unmeasured stage costs.512training-only members frozen for proposed local
MPS timing, not execution. CUDA removed per user; shipped models unchanged.
[Handoff](../reports/work/FOCUS-OFFLINE-PRODUCTIVITY-11/handoff.md).

**Revision2 live preflight,2026-09-30:** new local TTR/helper b79b34e4 and Fixture
062ddfe7 verified; booted local Simulator passes TTR readiness. Old-build blocker is
superseded. Campaign manifest validation still fails before dispatch; matching source
masks file-read errors as invalidArgument. Exact access cause remains unproven.
Native Fixture scene returns no_sample; capture/crop QA remain pending, no new pairs.
Follow-up workspace check passes in app-managed mode; current folder-repair UI
does not grant separate manifest input access. Producer import/grant path remains required.
User grants standing Simulator use; remaining21/training excluded from this proof.
22:46UTC recheck supersedes runtime liveness above: no TTR/helper/Fixture processes
observed. Latest producer22:03UTC status still lists manifest repair pending and is
expired; local manifest reader still masks file-read failure. No repeat capture
attempt or speculative release installation. Resume on an identified repaired
runtime/import contract, then refresh target and native-scene qualification.
[Live evidence](../reports/work/FOCUS-R2-LIVE-10/handoff.md).

**Historical revision2consumer readiness,2026-09-30 (runtime superseded above):**24actual producer
hashes match;50Python/123Swift tests and offline build pass. Strict optional geometry/
button identity and two motifs integrated through actual test-fixture intake/crop CLI.
Local running TTR remains old2ec0ea71; first3manifest validation returns invalidArgument;
9Simulators shutdown. User approved3pair proof, but no compatible local runtime yet
verified, no capture started. [Handoff](../reports/work/FOCUS-R2-COMPAT-09/handoff.md).

**Revision2static contract accepted,2026-09-30:**46members and all24axis declarations
verify,3+21manifests partition exactly. New dimensions/structural motifs/native light
buttons address proposal feedback. Existing consumer rejects24recipes at closed canvas
fields; next is strict local identity/parser compatibility, not another producer
rendering request. Fresh3pair proof remains unrun. No model changes.
[Review](../reports/work/FOCUS-R2-REVIEW-08/handoff.md).

**Matched24proposal reviewed,2026-09-30:**21members/16consumer recipe hashes verify,
but supplied geometry is near-square at two sizes and content is palette-only.
Requested revised aspect/content contrasts, explicit24target budget and missing
native gray buttons before capture. Integrity accepted, experimental fit not accepted.
[Review](../reports/work/FOCUS-PROPOSAL-REVIEW-07/handoff.md).

**Geometry QA/correction accepted diagnostically,2026-09-30:**2archives/55declared
members verified;64clamp flags corrected with unchanged crop hashes/other fields.
New4pairs have64measured geometry rows; older44lack352artwork records. All768QArows
explicitly lack enlarged presentation-effect bounds. No training or crop-policy change.
TTR's matched24proposal now published,8wide gray-button slots unsupported; consumer
proposal review next. [Intake](../reports/work/FOCUS-QA-INTAKE-06/handoff.md).

**Matched appearance preparation complete,2026-09-30:**24pair contract uses3families
×2contents×2backgrounds×2geometries; selected-state axis removed because existing
selectedIndex is tabs-only. Producer capability request published/read back; exact
recipe mappings and fresh runtime authority precede capture. No new model/data
admission. [Contract](Plans/FocusMatchedAppearancePilot.md).

**Retained transfer diagnosis complete,2026-09-30:** all395native pairs (150artwork)
correctly ordered in saved FDR020training scores, versus1/12development artwork hits.
Human training has6focused artwork controls and4negative/no positive primary buttons,
none Photos-style. Inspected Photos false-positive crop excludes the focused neighbor;
no relabel or crop correction warranted by this evidence.20numbered evidence sheets
and cached-feature contrasts support a targeted matched-appearance data pilot proposal,
with counterexamples preventing a causal claim. No new inference/training/admission.
[Diagnosis and next assignment](../reports/work/FOCUS-TRANSFER-DIAG-04/handoff.md).

**Full-corpus fit completed,2026-09-30:** approved FDR0201000updates on MPS finished
in21.34model-seconds (91.53s including preflight). All928training examples classify
correctly at0.5, but strict all-confident criterion remains901/928. Development
14/27focused hits,3/288false positives;14complete frames9unique correct,4no focus,
1multiple; retention18/18. No eligible snapshot/best.pt/export/promotion.
False positives improve38→3versus FDR019 while recall drops17→14hits; artwork remains
1/12hits, and Photos Welcome's unfocused button causes the multiple-focus failure.
47Python/123Swift tests and offline build pass; all saved predictions/source hashes
replayed. Next is targeted artwork/Photos transfer diagnosis, not more unchanged
training. Shipped models unchanged. [Handoff](../reports/work/FOCUS-FULL-FIT-03/handoff.md).

**Earlier full-corpus proposal/artwork comparison; execution superseded above:** existing928
training controls reverified; proposed80/20native/human weighted BCE with50/50labels,
fixed315development/18retention. No new training; implementation/run approval next.
Both TTR artwork archives received/hash-verified,96declared payload members intact.
4calibration pairs pass diagnostic intake;8artwork plus8wrapper crops render;
64/64producer reference PNGs match local production bytes/pixels. Producer's64clamp
flags are false positives from exact rectangle comparison; actual clamps0. Correction
request/exact receipts published and read back; peer acknowledgment/cleanup pending.
Neighbor slivers visibly present, prediction impact not measured;16%crop and training
membership unchanged. [Handoff](../reports/work/FOCUS-FIT-PREP-02/handoff.md).

**Training-fit diagnosis completed,2026-09-30:** FDR019 learned all48balanced
admitted examples at update162 (BCE0.038574), with18/18retention. Separate exposed
development:17/27focused hits,38/288false positives;14complete frames yield7unique
correct,5multiple,1wrong,1no focus. This is diagnostic, not release-qualified.
Retained FDR017/018 heads also failed to fit their own native training positives:
32/395 and27/395hits at0.85 (646/790 and626/790 correct at0.5). Training underfit
was not isolated before the prior data-mix experiments. Tiny-set success does not
prove full-corpus separability or fix transfer;31of38new false positives are artwork.
Next model decision: full-corpus fitting/optimization proposal with balanced loss
accounting before replacing the encoder. No additional run/export authorized here;
shipped model unchanged. [Handoff](../reports/work/FOCUS-FIT-01/handoff.md).

**Historical TTR coordination18:21UTC,2026-09-30; receipt superseded above:** producer18:15UTC update reports
qualified four-pair artwork delivery and a new retained crop audit. Both named shared
archives exist with advertised sizes; not yet copied/hash-receipted or accepted here.
Audit reports8source images/64role crops,32identical role comparisons, no image-edge
clamp, but neighboring nominal bounds intersect every crop and visible slivers occur.
This is a crop-context hypothesis, not a demonstrated cause of focus regressions.
Next: local production-crop parity and semantic review; keep16%expansion fixed.
Old producer disk/runtime hold is superseded. Remaining60pairs are planned, not
qualified; current device readiness was not checked. Producer has acknowledged the
earlier inventory only, not the completed FDR017/018 experiment update.

**Static-human experiment completed,2026-09-30:** approved FDR017/018 each completed
30epochs on MPS in~72s including preflight. Whole supplement session138controls now
has explicit static-human training reservation;315controls remain development and
64exclusions remain. Matched human auxiliary mixture worsened final27positive recall
(1hit→0) and288negative false positives(5→15);14complete frames1→0correct.
Retention9/18both; zero eligible epochs, no best.pt/export/promotion. Same frozen
encoder/head recipe is not ready for release. The subsequent FDR019 diagnosis above
changes the next model decision; qualified artwork delivery/crop acceptance remains
parallel data work. [Handoff](../reports/work/HUMAN-STATIC-ADMISSION/handoff.md).

**Human corpus inventory at original handoff,2026-09-30 (admission superseded above):** five latest human batches contain40 distinct
frames/517 reviewed controls (515 distinct crops),453 existing selection controls
and64 exclusions. Three sessions form two conservative related groups. Proposed
whole-session reassignment:138 supplement controls for a static-human training lane,
315 controls remain development; no independent real-world test claim. Existing
training already includes40 native Settings pairs. No admission/model execution.
15focused tests and123Swift tests/build pass. Next decision is explicit human-label
admission plus matched comparison preflight, independent of TTR artwork delivery.
[Handoff](../reports/work/HUMAN-CORPUS-INVENTORY-01/handoff.md).

**Annotator Undo fixed,2026-09-30:** first optional Vision/raster batch on a blank
image now has an empty baseline and can be removed in one Undo. Real TTR sample
verified19→0→19/save/reload; originals unchanged.50Python/Qt tests, offline build
and123Swift tests pass. Effective next editor launch; no human work interrupted.
Measured artwork delivery/crop qualification remains the next focus dependency.
[Handoff](../reports/work/ANNOTATOR-UNDO-01/handoff.md).

**Consumer repair intake,2026-09-30 10:08PDT:** both repair archives/13payload members
verified; actual Vision sidecar matches retained album_grid pair. Real editor preview,
cancel/add/save/reload passes; blank-image first-import Undo leaves boxes (no empty
snapshot).64focused tests pass; local Undo repair next. Artwork policy source-compatible,
not live-qualified; producer four-pair proof pending disk reserve. Exact receipts
published; no source merge/runtime/training. [Handoff](../reports/work/FOCUS-REPAIR-INTAKE-04/handoff.md).

**Focus resume check,2026-09-30 09:45PDT:** TTR GUI1268/status responds, idle queue;
helper and installed Fixture hashes unchanged from prior missing-artwork-geometry
trial. All9tvOS Simulators shut down.8scene/64pair proposal and18indexed first-case
artifacts hash-verified intact;45GiB project-local free. No new capture/model work.
Next gate is matched repaired runtime plus fresh bounded Simulator authority, not
external storage. SharedStatusFile reconnected09:54PDT; producer16:52:15Z reports
campaign artwork-policy propagation repaired (58offline passes), but four-pair proof
unrun due to producer9.58GiB free below10GiB reserve. Vision repair/sample sidecar
also published, consumer receipt/import pending. Cancellation and current focus
delta published/read back; new peer acknowledgment pending. No new runtime checks
or downloads in status reconciliation; previous local preflight remains09:45PDT.
[Resume handoff](../reports/work/FOCUS-GEOMETRY-RESUME-03/handoff.md).

**External storage cancelled,2026-09-30:** no further shared-drive/SSH/SFTP/rsync
work; use project-local evidence and verified SharedStatusFile receipts. Not a focus
blocker. User reports later authentication/enumeration success, repeated external
share mount failure even after APFS reformat/permission refresh; cause unproven.
No agent reformat/migration. Remote Login last user-reported enabled, shutdown
unverified; no automatic cleanup. [Closure](../reports/work/DATA-EXTERNAL-01/status.md).

Historical superseded storage observation: maintainer authorized
`/Volumes/Crucial X9/data_training` for shared datasets/captures/checkpoints. At09:05PDT
the same volume/partition UUID is mounted as `/Volumes/training`; folder and SMB
share now point to `/Volumes/training/data_training`. exFAT, approximately1.8TiB free.
Old mount path absent; no consumer relocation performed. Latest reported Sillycon attempt rejects SMB authentication;
remote mount/write access remains blocked, not a proven filesystem incompatibility.
Existing data not moved/deleted; path-bound manifests need migration checks.
Coordination share unmounted; current update unpublished. [Status](../reports/work/DATA-EXTERNAL-01/status.md).

**FOCUS-INTEGRATION-03,2026-09-30UTC:**1,947admitted images/crops reverified;
user confirmed exact Photos frame004 has two focusable buttons. Separate development
policy now supports14whole frames (buttons1,tabs3,artwork2,rows6,other2), preserving
original13frame baseline and453crop membership. Cached FDR016 ranks this button
correctly but0.826<0.85still abstains. No new model execution or admission.
Actual TTR retained Vision processing fails before sidecar despite working status;
producer-stage diagnosis requested. Geometry runtime unchanged, no capture repeated.
[Handoff](../reports/work/FOCUS-INTEGRATION-03/handoff.md).

**Updated local TTR acceptance,2026-09-30UTC:** authorized first4pairs captured,
exported with verified chunks and accepted for diagnostic intake. All8 wrapper
crops render; all8 artwork-layout crops blocked because geometry is `not_supplied`.
Remaining60pairs not attempted; postflight ready/ownership clear. Producer must
qualify the installed Fixture geometry before capture resumes. Optional TTR OCR/
rectangle sidecar import now available in annotator; supplied-file acceptance pending.
No new training admission or model operation;395pair candidate remains unchanged.
[Checkpoint](../reports/work/FOCUS-GEOMETRY-LIVE-02/handoff.md).

**FOCUS-CONTROL32-ADMIT-01 — approved data admission:** 32 retained native-control
pairs added to the candidate assembly: **395 training pairs**, comprising 133
buttons, 26 tabs, 150 artwork and 86 rows. All prior members, 9 retention pairs,
453 real selection crops and 64 selection exclusions preserved. The remaining
64 artwork additions stay held for geometry review. This is a data-only assembly,
not a runnable experiment or model improvement; shipped models are unchanged.
[Evidence](../reports/work/FOCUS-CONTROL32-ADMIT-01/handoff.md).

**FOCUS-OFFLINE-PREP-03 complete for review:** duplicate sensitivity does not
resolve poor transfer (FDR0163/35TPunchanged,16/418FP→15/416unique-cropFP).
64pair diagnostic consumer workflow tested end-to-end on source-shaped fixtures;
v2cards/fillViewport and bright palette hashes now reproduce all8producer vectors.
Exact32native-control-pair admission proposal subsequently approved above;64artwork pairs held.
No new inference/training or shipped change. Real new-build bundle
and geometry review remain pending. [Handoff](../reports/work/FOCUS-OFFLINE-PREP-03/handoff.md).

**Matched artwork trial status,2026-09-30T01:50Z:** producer acknowledges the
consumer adapter; measured trial/parameter response still pending. Local Simulator
and Fixture observed, no local TTR host process. No new capture or data admission.
[Source-backed trial checklist and resume conditions](../reports/work/FOCUS-MATCHED-TRIAL-01/handoff.md).

**FOCUS-READINESS-02 completed retained audit:** FDR015/01629,202stored predictions
replayed; all16latest real false positives are artwork, with0/18artwork positives
detected.2,203image/crop files verified;24within-training duplicate crop groups,
zero exact cross-role crop overlap (not proof of source independence).363training
pairs/9retention pairs/453real selection crops at that audit;32of96diagnostic additions
subsequently admitted above. Actual trainer dry-run validates and blocks on missing new
approval. No model executed or promoted. Next is measured artwork geometry/contrast
evidence and member-bound admission, not another unchanged run.
[Handoff](../reports/work/FOCUS-READINESS-02/handoff.md).

**Vision annotation comparison (diagnostic only):** on8retained development frames
with78reviewed controls, Vision rectangles matched44atIoU0.5 versus32for current
raster helper;244valid proposals versus65. More coverage but substantial clutter;
not a semantic detector or automatic annotation replacement. OCR remains separate.
Recommendation: optional filtered proposal trial with measured operator effort
before TTR integration. [Results](../reports/work/VISION-ANNOTATION-COMPARE-01/handoff.md).

**Annotator improvement (local tooling):** optional Auto-detect boxes action now
proposes rectangles with a numbered selection preview and shared label choice.
Unconfirmed/unfocused defaults; existing annotations preserved; no model inference
or training changes.110Python/123Swift tests pass. Operator restart pending.
[Handoff](../reports/work/ANNOTATOR-AUTO-DETECT-01/handoff.md).

**FOCUS-GEOMETRY-ADAPTER-01 complete offline:** explicit diagnostic wrapper/layout
crop selector integrated with existing TTR intake, strict native bracket validation
and production16%/256square cropper. Eight retained crops byte-identical; eight
layout requests unavailable as expected on old telemetry;19source files unchanged.
No new measured producer sample or live geometry qualification; no inference,
training, admission or shipped-model change. Next is the bounded matched geometry/
contrast trial with fresh target/capture approval, not another unchanged run.
[Handoff](../reports/work/FOCUS-GEOMETRY-ADAPTER-01/handoff.md).

**FOCUS-GEOMETRY-CORPUS-01 preparation complete:**96member reuse proposal frozen
and384frame/crop files rehashed:32controls,60caption-inclusive artwork,4caption-free
artwork. TTR's additive nominal artwork-layout source contract inspected, not live
qualified; no enlarged-body measurement inferred. Diagnostic geometry-role adapter
is now completed above; proposed8scene/32pair matched contrast trial
requires separate capture scope. No new run/admission/model change. Plan/questions
published and read back in own shared packet; peer acknowledgment not observed.
[Plan](../reports/work/FOCUS-GEOMETRY-CORPUS-01/plan.md).

**FOCUS-PAIRED-INTAKE-01 complete:** FDR016 ran once,30epochs on cached FDR015
features, actual MPS. Same initial predictions/corpus/gates verified; no encoder
inference. Ranking11/13unchanged; two fixed0.85correct frame decisions, but
Home ranks2/8still wrong, retention12/18 and real3TP/16FP. Zero eligible epochs;
no best.pt/export. Recommendation: data/geometry alignment, not unchanged rerun.
Both native100-r2/native12 archives received and production-crop reviewed:
96usable development diagnostics,13duplicates,3old clipped Library holds.
All12repaired bodies enclosed; no training admission. TTR receipt and geometry
answer published/read back in own packet; peer acknowledgment not observed.
[Run](../reports/work/FDR-016/handoff.md),
[intake](../reports/work/NATIVE112-INTAKE-01/handoff.md).

**FOCUS-ARTWORK-AUDIT-01 complete for review:**150admitted artwork pairs/559files
verified; only24explicit native-image pairs, three procedural motifs/two backgrounds,
fixed four-control rows. All150reported pair box areas equal;27source representative
pairs inspected. Native-image examples have useful focus changes but narrow content
and different box/caption treatment from Home; not proof of a single causal bug.
The proposal was subsequently executed as FDR016 and the named archives received
and reviewed above. Producer confirms wrapper/caption bounds, not transformed
artwork-body geometry. [Audit handoff](../reports/work/FOCUS-ARTWORK-AUDIT-01/handoff.md).

**FOCUS-RESET-01 complete for review (2026-09-29):** cached-score scoreboard/crop inspection
complete. Ranking, strict ambiguity gate and runtime-style selection now distinct.
FDR014 initial/epoch1/final first-choice scores8/13,11/13,5/13; largest annotated-box
baseline8/13, random expectation1.398/13. Thresholded runtime-style decisions remain
unsafe; no gate waived.13complete frames are predominantly Settings, not broad
qualification.14,601scores replayed/488image files checked;44focused tests and offline
Swift checks pass. Eight visual pages show stretched shapes/neighbor highlights;
these are hypotheses, not relabeling. Official ImageNet weights approved, downloaded
and hash verified; frozen-feature path integrated with93focused tests passing.
FDR015 completed30epochs on verified MPS in94.55s overall/5.49s trainer. Final
ranking11/13 versus FDR014 final5/13, AUROC0.726 versus0.601; fixed0.85 yields
0/35TP,1FP,retention9/18 and0eligible checkpoints. No selected model. Both Home
artwork frames still rank incorrectly; eight Settings-related/three tabs rank
correctly. Next: matched artwork/context audit and separately approved grouped
ranking/calibration design, not unchanged corpus scale or another automatic run.
[FDR015 results](../reports/work/FDR-015/results.md).
[Findings](../reports/work/FOCUS-RESET-01/findings.md),
[handoff](../reports/work/FOCUS-RESET-01/handoff.md).

**FDR-014 complete (2026-09-29,22:26Z):** corrected appearance sampling verified,
same corpus/selector and one30epoch MPS run.0eligible checkpoints. Retention18/18
throughout; minimumFP10 (prior21) still detects only2/35focus targets. Final4TP/35FP;
real/artwork/frame guards fail every epoch. Sampling alone is insufficient.
82focused tests, offline Swift build and14XCTest+109Swift Testing pass;14,601stored
scores/selector metrics replayed. No best.pt, export, promotion or automatic rerun.
Next: targeted native100/canvas-v2 contrast/geometry audit, not more unchanged training.
[Results](../reports/work/FDR-014/results.md), [handoff](../reports/work/FDR-014/handoff.md).

**FDR-013 complete (2026-09-29,22:00Z):**30epochs on MPS,124.34s trainer,
217.41s overall.0eligible checkpoints.29epochs retain18/18, but every epoch
fails real/artwork/full-frame guards; minimumFP21 exceeds9allowed. Tabs0/3
throughout. All14,601stored predictions/metrics verified. No best.pt, conditional
comparison not run; last.pt not substituted, no export/promotion. Next: targeted
native100/canvas-v2 coverage audit, not unchanged retraining.
[Results](../reports/work/FDR-013/results.md), [handoff](../reports/work/FDR-013/handoff.md).

**FOCUS-SELECTION-01 complete (2026-09-29):** representative real-development
selection now integrated in the trainer; legacy selectors preserved. Immutable
363training+9retention pairs prepared, all668 prior rows unchanged.453 settled
real candidates select checkpoints but never enter training;64excluded labels
accounted. Only13/40frames support full-frame outcomes. All18retention decisions,
real per-stratum floors and actual improvement are required before weightedBCE
can choose a checkpoint. No eligible epoch means none selected.77focused tests
and offline Swift build/14XCTest/109Swift Testing pass. Actual preflight valid;
only blocker at preparation was missing_experiment_approval. The
[bounded run](../reports/work/FOCUS-SELECTION-01/run-proposal.md) was subsequently
approved/executed as FDR013 above; no eligible checkpoint or export.
[Handoff](../reports/work/FOCUS-SELECTION-01/handoff.md).

**QUALIFIED44 intake complete (2026-09-29):**135,449,487-byte archive received,
hash verified;44 native pairs reviewed with production16%/256crops.38 unique usable
development candidates,3 duplicates excluded,3 Library geometry cases quarantined.
No exact evaluation overlap.39 focused tests pass. Original325+9 unchanged;
potential363+9 was a proposal at intake, now prepared above. Representative real-screen
selection proposal ready; no new run/inference/export. TTR receipt and precise
geometry question published; acknowledgment pending. Selection implementation
and candidate preflight subsequently completed above, independent of the three repairs.
[Handoff](../reports/work/QUALIFIED44-INTAKE-01/handoff.md).

**FDR-012 complete (2026-09-29,21:09Z):**30epochs on MPS in90.70seconds,
396.55seconds including preflight. Epoch29 retains18/18;829/829comparisons complete.
453settled real candidates:1/35focused found,15/418false positives versus FDR010
3/35 and9/418. Related synthetic unique-correct18/50→20/50; artwork0/32→2/32.
Real complete-frame selection2/13→1/13, plus1wrong. Development criterion failed;
no export/promotion.33tests pass; shipped unchanged. Next: intake TTR's already-
published44pairs, audit representative gaps and propose selection that measures
transfer alongside retention before another run.44-pair intake subsequently completed above.
[Results](../reports/work/FDR-012/results.md), [handoff](../reports/work/FDR-012/handoff.md).

**FDR-011 execution interrupted (2026-09-29,20:45Z):** approved325+9 training
passed preflight but restricted launch selected CPU, unlike baseline FDR010 MPS.
Stopped owned process after3/30completed epochs;541seconds including preflight.
Scoped host probe confirms MPS available. Partial weights remain unselected;
no candidate inference/export/promotion.40real-frame/517score and50related-synthetic-
pair/312score comparison inputs and baseline scores verified;33focused tests pass.
Replacement approved as FDR-012 above; no new data/capture needed.
[Historical handoff](../reports/work/FDR-011/handoff.md).

**Related-synthetic policy approved (2026-09-29):** related renderer/motif ancestry
alone no longer excludes new reviewed variants from a development training lane.
Exact evaluation members/pixels stay excluded; related-synthetic results are reported
separately from real-app transfer and independent qualification. BULK12 admission
and325+9 assembly preflight are complete. Actual trainer configuration is valid;
approval was subsequently granted for FDR-011 (interrupted as above).16tests and
3actual negative admission checks pass; data-policy blocker resolved for this
bounded development experiment, not production qualification.
[Policy](Plans/FocusRelatedSyntheticAdmission.md).

**First bulk-shard intake complete (2026-09-29):**12native pairs/24production crops
verified and agent-reviewed.21distinct full-frame pixels;24distinct crop pixels;
no conflicting labels or exact overlaps in10 checked reference manifests. TTR stopped
after3cases due Simulator timeout; remaining88pairs not running. New examples share
reserved SYNTH05 development ancestry, so training admission remains0 pending an
explicit source-role/selection decision at intake time. That block is superseded
by the approved325+9 development assembly above; shipped models remain unchanged.
44pair non-executable coverage proposal ready; no human annotation requested.
[Evidence](../reports/work/BULK12-INTAKE-01/handoff.md).

**Human supplement benchmark comparison complete (2026-09-29):** reviewed8 frames
now admitted through a separate development-evaluation lane; original diagnostic
manifests unchanged.155/155 scores per model;138 focus candidates and17 auxiliary.
Shipped finds6/8 positives with99FP; FDR-0100/8 with2FP. Candidate92.75% accuracy
is negative-dominated, not successful focus detection. Full-frame selection remains
unavailable; no training admission or release.23 tests/actual negative checks and
metric replay pass; previous32-frame results reused without model execution.
Next: TTR bulk revision3 schema/role intake and first100-pair shard acceptance.
TTR19:38:41Z status reports that shard authorized/running; additional shards remain
unapproved. Its2,000-pair planning target is not qualification or a replacement for
existing coverage gates. Recipe-to-failure mapping, source-role separation and actual
runtime receipt remain explicit coordination questions; acknowledgment pending.
No unchanged training or broad manual relabeling.
[Evidence](../reports/work/HUMAN-BENCHMARK-02/handoff.md).

**Real-app supplemental review ready; diversity incomplete (2026-09-29):** Office
recording895563805bytes received and hash-verified; all702 image files verified.
Initial ten screens repeated prior coverage. Replacement eight-screen supplemental
batch compares against32 prior reviewed frames: seven Paramount+ contexts and one
OS Search. New visual/control examples do not establish broad app/source diversity.
Human revision192241Z confirms8 frames/155 controls;155/155 production crops and
structural audit pass.8 focused/147 unfocused, crop hashes unchanged. Maintainer
confirms first Top Stories item focused and Watch Now unfocused in frame3; no
annotation clarification remains. Complete-frame candidate coverage remains unknown.
Maintainer
removed repeat transfer-size approval; capacity and integrity checks remain. Two small
TTR source/audit archives also received,not installed. No new capture or model run.
[Checkpoint](../reports/work/HUMAN-REAL10-01/handoff.md).

**Representative focus validation complete:** shipped/FDR-010 each scored312 new
native-fixture crops;50pairs and50complete frames accounted,zero failed predictions.
FDR-010 finds18/18 synthetic button/tab/row positives but0/32 artwork positives;
unique-correct18/50 versus shipped7/50. Retained32 real frames reproduce poor
transfer: candidate0/3buttons,0/3tabs,1/12artwork,2/7rows. No export/retraining.
Production planner freezes313+9 membership and5727 additional canonical scene-pair
targets;696 source-defined recipe jobs are only a scheduling envelope. Priority is
matched native-effect/artwork/background/geometry contrasts and genuine OS transfer,
not repeating unchanged templates. Independent source gaps and capacity remain open;
33.4GiB free is below projected data plus10GiB work reserve. Legacy1500 crops exist
but their v1 manifest lacks original/native bindings; no new admission.
[Handoff](../reports/work/FOCUS-REPRESENTATIVE-01/handoff.md),
[collection assignment](../reports/work/FOCUS-REPRESENTATIVE-01/production-assignment.md).
Software:70Python/123Swift tests and offline build pass. Full production corpus
collection and revised selection-policy approval remain separate next assignments.

**SYNTH05 consumer intake complete:** approved22+28-pair capture archives verified;
50 diagnostic pairs,100 production crops,74 distinct full-frame pixels. Native
artwork and selected-parent/child hierarchy compatibility validated; all100 crops
reviewed,64 focused Python/123 Swift tests pass. All12 groups are dark/seed7 on one
reported Simulator target, not independent sources. No training admission;313+9
candidate/retention membership unchanged. No recapture,model execution or producer
deployment. Next: representative selection validation and production role/source
reservation before scaling. [Handoff](../reports/work/SYNTH05-HIERARCHY-INTAKE-01/handoff.md).

**FDR-010 complete; do not export:**313 training pairs/nine retention,30 epochs,
epoch29 selected,18/18 retention. Same24-frame real benchmark finds3/19 positives
with3 FP and2/13 unique-correct frames, versus shipped8/19,30 FP,3/13. Separate
eight-frame Home/Photos/Settings set finds0/8 positives; both Photos pairs fail.
362/362 candidate scores complete. The nine retention pairs all come from Settings/
Accessibility; passing them does not establish broad transfer. No second run or
model replacement. Next: representative selection validation and coverage-driven
production campaign, not more unchanged recipes/epochs. [Handoff](../reports/work/FDR-010/handoff.md)
and [production evidence map](../reports/work/FDR-010/production-acceptance.md).
This resolves the narrower-decision-pending status in the historical entry below.

**Gap-targeted synthetic corpus admitted (2026-09-29):** current running local
TTR/Fixture completed8 jobs,40 native competitor pairs,0 rejected targets.
24 button,8 Settings-row analog and8 selected-tab analog pairs;80 reviewed
production crops,42 distinct full frames. Explicit admission preserves273 prior
candidate pairs and9 retention pairs, adds40:313 training candidates plus9 retention.
No real-regression overlap, contradictory crop labels or new complete-pair duplicates.
Closed presentation/selection consumer support verified against actual producer
hash vectors;83 focused tests and offline Swift build/123 tests pass. TTR request
and qualification feedback published/read back. Original full protocol retains10
independent-coverage blockers. The narrower proposal was subsequently approved and
completed as FDR-010; failed transfer rejected export. No pending approval for that
run. [Historical corpus handoff](../reports/work/FOCUS-GAP-LIVE-20260929/handoff.md).
This supersedes the earlier gap pack's old-runtime, missing-row-competitor and
missing-flat-tab statements. SYNTH05 now adds diagnostic nested hierarchy evidence;
genuine native OS coverage remains separate.

**Synthetic repaired pilot received and crop-qualified (2026-09-29):** approved
34778079-byte archive verified;12/12pairs and24/24production crops pass, including
4competitor-v3 pairs. Actual receipt exposed omitted-nil baseline key handling;
consumer fixed with regression.49 Python/123 Swift tests and offline build pass.
Reviewed development manifests retain native geometry/focus and image lineage.
Only one seed/four collectionItems,16distinct full-frame pixels across24files;
broader training corpus/admission still required. No model change or recapture.
[Handoff](../reports/work/SYNTH-FOCUS-FACTORY-01/repaired-pilot-handoff.md).

**Focus test cycle (2026-09-29):** batch03 now reviewed and QA78/78 complete;
all three batches evaluated249/249 per model. Settled candidates202: shipped
recall8/19 with30 false positives; FDR-0094/19 with8. Complete-frame unique
selection3/13 versus2/13. No candidate release justified. Newly audited12 dock
pairs remain test-only; clean-canvas gap-addressing corpus is the next dependency.
1087/1105 label/focus conflicts quarantined; keyboard1043 frame coverage incomplete.
No new training/export or shipped changes. [Handoff](../reports/work/FOCUS-TTR-TEST-CYCLE-01/handoff.md).
This supersedes older statements below that batch03 remains open/untouched.

**Synthetic focus factory priority:** dock repair source received and all36 files
hash-verified and now integrated with explicit approval. Signed host/Fixture build
pass;82 focused tests pass,1 live-only skipped;6 model checks pass. Fixture installed.
Human project-folder grant resolved startup. Live four-control/nine-item sweeps
passed:12 native pairs, zero rejected rows,24 production crops,29 consumer tests.
All eight eligible dock targets captured; ninth item disabled. These samples remain
test-only. Direct export permission error513 worked around using the supported
caller exporter. Clean canvas/competitor-pair implementation remains next;
human annotation continues independently; no model change. Clean-canvas source
subsequently received:842765 bytes,50 source files verified/reconciled; not deployed.
Consumer canvas compatibility and target accounting now pass34 Python/123 Swift
tests including actual generated-bundle crop CLI; live rendering remains unrun. See
[consumer handoff](../reports/work/SYNTH-FOCUS-FACTORY-01/canvas-consumer.md) and
[canvas intake](../reports/work/SYNTH-FOCUS-FACTORY-01/canvas-intake.md).
[Plan](Plans/SyntheticFocusFactory.md).

**Review-parallel software complete for review:** role-aware development evaluator,
one-command QA and retained sequence audit verified.59 Python/123 Swift tests pass;
actual production crop replay89/89. Recorder input completion is not UI transition
truth:15/166 actions have bounded declared-settled posts,14 pass conservative checks.
No model execution or automatic admission; batch03 remains untouched.
[Handoff](../reports/work/REVIEW-PARALLEL-01/handoff.md).

**Trial02 coverage/admission preparation complete:**16 reviewed frames/171 crops,
154 proposed focus candidates plus16 auxiliary annotations and1 unresolved role.
Zero formally declared pairs;14 visual proposals retain identity/context caveats.
No model execution; batch03 untouched. Frame605 completeness and original tab
settlement remain admission decisions, not blockers to ongoing annotation.
[Audit and next assignment](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/batch12-coverage-handoff.md).

**Batch03 annotation open:** eight unused retained images validated and opened,
including populated App Store cards/search results plus Settings row/top-shelf.
No exact pixel overlap with prior sixteen. All producer-unverified; settlement
and annotations require human review. No model changes.
[Handoff](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/batch03-handoff.md).

**Batch02 complete QA (23:27Z revision):**8 reviewed frames/89 controls with
completeness receipt;89/89 production crops and full audit pass integrity checks,
89 distinct crops. No hard issues; one near-frame warning is Arcade→Search focus.
Two latest batches total16 frames/171 controls. Diagnostic-only, no inference or
training admission; earlier partial QA retained. [Evidence](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/batch02-crop-qa.md).

**Experimental click-box aid:** optional/default-off toolbar toggle implemented,
44 Python/14 Qt tests and offline Swift checks pass. Retained probe:3 Settings
panels suggested,1 tab abstained; not promoted. Numeric bounds dust repaired;
batch02 previews8/8 ready without writes, awaiting explicit Finish confirmation
and editor restart. [Handoff](../reports/work/HUMAN-CLICK-BOX/handoff.md).

**Batch02 partial crop QA:**70/70 production crops verified,70 distinct pixels,
no exact overlap with batch01 crops. Full audit remains blocked on immutable
pending frame249; failure receipt preserved. Latest two batches total15 reviewed
frames/152 controls, not matched training pairs. No inference/training/admission.

**Batch02 human review verified (23:14Z):** revision231403Z-405f04f0 contains7
reviewed frames/70 reviewed controls, with completeness attestation on those7.
recorded-249 remains blocked: Finish preview reported invalid_bounds; its untouched
snapshot retains19 boxes without assigned IDs, hence revision invalid_control_id.
No auto-repair/confirmation. Crop QA pending; diagnostic/training-ineligible.

**Editor navigation crash repaired:** stale rectangle selection on key release
caused PyQt abort. Reset/guard added,13 Qt tests and offline Swift checks pass;
batch02 reopened at image6, saved first5 annotations preserved. TTR notified that
this was a consumer editor issue, not capture failure; export qualification remains
separate. [Handoff](../reports/work/HUMAN-REVIEW-NAV-CRASH/handoff.md).

**Second annotation batch opened:**8 distinct retained frames, zero exact pixel
overlap with batch01;7 producer-settled/1 explicitly unverified diagnostic frame.
First-batch admission proposal prepared:67 candidates,15 auxiliary background
annotations, no source-label changes. Settlement reconciliation and separate
model-evaluation approval remain. [Handoff](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/batch02-handoff.md).

**Trial02 crop QA/audit complete:**82/82 production crops from8 reviewed frames,
82 distinct crop pixels,8 focused/74 unfocused. No hard audit issues. One near-frame
warning visually resolved as Games→Apps focus change; preserve both. Static labels
remain auxiliary annotations, not automatically focusable candidates. Next is
role-aware development-admission proposal (including settled-state reconciliation),
not training/inference. Circle-only focus row indicators implemented;11 Qt tests
and offline Swift checks pass. [Handoff](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/qa-handoff.md).

**2026-09-28 22:51Z trial02 human review saved and verified:** revision
20260928T225131Z-056fc495 contains8 reviewed frames/82 reviewed controls, including
tabItem focus roles. Snapshot-bound revision validation passes; separate human
completeness receipt covers all8 frames. Diagnostic-only, trainingEligible=false.
Production crop QA/audit remain next; no inference or training performed.

**Binary Finish review corrected:** unchecked Focused proposes unfocused during
explicit confirmation; legacy unknown flags no longer block the binary workflow.
Actual saved batch read-only preview8/8 ready, no automatic confirmation.59 Python,
11 Qt tests and offline Swift build/test pass; editor restart pending save/close.

**Annotation focus indicators:** focused controls now pin first with explicit
state markers and count/multiple-focus warning. Selection, geometry, canvas and
saved order remain unchanged.11 Qt tests and offline Swift checks pass; current
window must be saved/closed/reopened. This does not relax multi-focus admission.

**2026-09-28 focus-review taxonomy gap addressed:** individual tab items and other
unmapped focusable controls can now be annotated as local focus-only roles.
Editor, presets, Finish review, completeness, diagnostic coverage/audit and
production crops support them.77 Python/9 Qt tests and offline Swift build/test
pass. No detector IDs, native sidecar schema or weights changed; new-role model
admission remains separate. User saved/closed; editor reopened at App Store tabs.
[Handoff](../reports/work/HUMAN-FOCUS-ROLES/handoff.md).

**2026-09-28 rectangle presets:** local annotation editor now has Save/Load preset.
Follow-up: one Focused checkbox (unchecked saves unfocused), Enter accepts valid
labels throughout the dialog, optional description; eight Qt tests pass.
Layouts persist across batches with fresh IDs and no inherited focus/approval.
Six Qt tests and offline Swift build/test pass; user window restart pending
save/close. No model or data admission change.
[Handoff](../reports/work/HUMAN-REVIEW-PRESETS/handoff.md).

**22:05Z Office recording stopped:** trial02 completed166 actions/1082 observations.
Cleanup reports owned_provider_released; Office control connected. Source retained;
1009 images hash-verified,73 repeated pixel observations,24 producer-settled candidates.
Export failed serviceUnavailable; exact cause unknown, coordinator healthy afterward.
No recapture. Eight-image direct local diagnostic intake is now prepared and open
in the rectangle editor: five Settings and three App Store frames. Metadata and
original image hashes are preserved; the export defect does not block annotation.
Remaining recording is archived, not a human assignment. No inference/training or qualification claim.
[Session and non-blocking delivery-profile request](../reports/work/FOCUS-REGRESSION-V2/office-trial-02/session.md).

**2026-09-28 offline review preparation complete:** FOCUS-REVIEW-PREP-01 adds
rectangle double-click editing, balanced eight-frame queues with compatible exact
duplicate omission (raw history retained), and one optional completeness assertion
in Finish review. Hidden frames cannot be bulk-confirmed. Coverage is reported by
family/class/focus treatment; unknowns remain explicit. Retained smoke dry run:
7 selected/1 deferred by layout cap, no exact full-frame duplicates; all8 annotations
unchanged. No new human completeness claimed.168 Python +4 Qt tests and offline Swift
build/123 tests pass. [Handoff](../reports/work/FOCUS-REVIEW-PREP-01/handoff.md).
The recorder blocker below is separate; no new capture or model execution occurred.

**Immediate priority change (2026-09-28):** maintainer requests a substantially more
diverse real-world development regression set and annotation, before training-data
collection. Keep the8-frame set as a smoke test. Proposed v2 covers24 distinct
screen situations/~48–72 selected frames across multiple interaction families and
apps. Maintainer chose Apple apps, Settings and safe OS UI, and approved local
human-operated Office recording. The new running build advertises MCP recording
controls, but one record.start returned domainFailure/unsupportedCapability.
Postcheck: recording false,0 actions/frames; control connection preserved.
No retry or chat-paced fallback. Producer diagnosis/supported setup or matched repair
was the capture blocker; no model or remote-pairing prerequisite.
**20:41Z recheck:** newer running Max build97201 contains the producer's repaired
`startActionRecording(destination:title:)` overload. Matching MCP status works.
Office is currently disconnected, video idle, recorder off, no evidence session.
Repair is present, but start/action/stop/export/import has not been live-qualified.
Next is operator connection/availability confirmation and a bounded recording trial,
not another unqualified claim that the whole workflow is fixed.
[Repair/readiness evidence](../reports/work/FOCUS-REGRESSION-V2/recorder-recheck-2038/handoff.md).
**Subsequent authorized trial:** user confirmed safe connected Office; live coordinator
confirms connected despite stale device.list saying disconnected. One record.start
now returns persistenceFailed for the project-local destination, not unsupportedCapability.
Postflight recorder off, zero frames/actions; no retry or connection teardown.
Next blocker is producer diagnosis of the exact storage write/export boundary.
[Trial evidence](../reports/work/FOCUS-REGRESSION-V2/office-trial-01/handoff.md).
**21:03Z new-build review:** actual build checkout Developer/TVTestRig is at0d9389ab;
running PID99680 includes new destination resolver and recorder CLI help. Office
coordinator connected; recorder off. Resolver can silently re-anchor absolute paths
outside TTR's root; prior consumer request was absolute, not relative as producer
diagnosis states. No new start until exact output/export contract is verified.
[Review evidence](../reports/work/FOCUS-REGRESSION-V2/recorder-recheck-2102/handoff.md).
**21:49Z candidate recheck:** running build3876/source7ddd182b fixes the reviewed
path contract and adds prepare/export. Office connected. Actual no-write prepare
succeeds in TTR-managed storage and rejects direct NUIAK output. Need user approval
for that outside-project recording location followed by project-local export; no
further producer code blocker established. Live capture/export/schema2 intake remain
unqualified. [Preflight](../reports/work/FOCUS-REGRESSION-V2/recorder-recheck-2149/handoff.md).
[Start failure](../reports/work/FOCUS-REGRESSION-V2/recorder-readiness/handoff.md).
[Collection/annotation proposal](Plans/RealWorldFocusRegressionV2.md).

**2026-09-28 approved human development comparison complete for review:**
HUMAN-REVIEW-04 scored all113 controls with both exact models at0.85. Shipped
FocusRing detects4/8 focused controls with11 false positives; FDR-009 epoch3 detects
1/8 with15. Shipped passes both explicit Photos pairs; candidate passes neither.
Both miss the focused Photos Home tile and General Settings row. No promotion or
training; the whole8-frame session is reserved for development regression.154 Python
tests and offline Swift build/123 tests pass.37 numbered error sheets and a ranked
matched-data assignment are delivered. Source independence/complete-frame selection
remain unqualified; original diagnostic flags unchanged.
[Results](../reports/work/HUMAN-REVIEW-04/results.md) ·
[Handoff](../reports/work/HUMAN-REVIEW-04/handoff.md) ·
[Next assignment](../reports/work/HUMAN-REVIEW-04/next-assignment.md).

**2026-09-28 actual human review and crop/audit tranche complete for review:**
Joe explicitly completed8/8 Office frames and113/113 controls in Finish review;
the immutable revision and saved annotations match. Both explicit Photos pairs
are reviewed.113/113 production16%/256×256 crops pass, with111 distinct crop pixels.
HR2 finds no hard integrity/label-conflict errors, two duplicate crop groups and
four near-frame heuristic matches. All evidence retained.8 positives/105 negatives,
three screen contexts, one device/session; appearance/source independence and
complete-frame candidate coverage remain unknown. No model quality claim.

The lightweight local Labelme workflow includes rectangles, copy/paste, local IDs,
Finish review, current-frame flag toggle and Command-arrow navigation.145 Python
tests and offline Swift build/123 tests pass. Static audit queues and all eight
production crop sheets are available. No new capture, inference or training.
The subsequent development-evaluation lane/comparison was approved and completed
above. This whole correlated batch is reserved for regression, not training.
Existing diagnostic admission flags remain unchanged.
[HR2 handoff](../reports/work/HUMAN-REVIEW-02/handoff.md) ·
[Approval proposal](Plans/HumanFocusAdmissionDecision.md).
[Operator guide](../reports/work/HUMAN-REVIEW-01/OperatorGuide.md) ·
[Evidence-backed handoff](../reports/work/HUMAN-REVIEW-01/handoff.md).

**2026-09-28 supervised collection exposed a P0 workflow gap:**8 local Office
checkpoint frames and9 human TTR inputs retained, including both Photos Welcome
focus states. Button logging works; automatic per-input image retention is not
qualified (Right/Up/Select setup has no intermediate images). Maintainer rejected
chat-per-press collection. Session finalized, owned lease released, provider idle;
user control connection preserved. Next integration requirement is an
[action-linked demonstration recorder](Plans/TTRActionLinkedCapture.md), not another
chat-paced run. Raw data retained; human bounds/crop review is now complete above,
while training admission remains unapproved.

**2026-09-28 Max-local Office capture passed:** after the maintainer approved
permission prompts, a fresh connection succeeded in124ms and one1920×1080 PNG
was delivered locally, hash-verified and visually inspected (Home, Photos tile
visibly focused). First timeout/connectionLost attempt preserved. Owned lease
released, connection disconnected and provider idle verified. Max-local is now a
demonstrated alternative to Sillycon for basic capture; remote pairing is not a
dependency for this path. No input-sequence qualification, reviewed pair/training
admission or model test. [Bounded test](../reports/work/LOCAL-OFFICE-CAPTURE-01/handoff.md).

**2026-09-28 TTR consumer integration update:** existing local remote client passes
help/status/register and standalone MCP initialization/12-tool discovery; signature
verification passes in normal host execution. LAN service discovery returned no
candidates; no pairing or capture performed. Producer runbook/schema metadata
received and hash-verified; current registration output omits a custom state path.
Await exact running-build binding, Sillycon listener/pairing window and remote
simulator UUID/grant confirmation. No live integration or model gate pass.
[EXT-CAP-02 checks and feedback](../reports/work/EXT-CAP-02/handoff.md).

**2026-09-27 FDR-009 completed, not shipped:**30/30 epochs on273 training/9 retention
pairs,50/50 native–Fixture sampling,FDR-007 warm weights/fresh optimizer. Selected
epoch3 by minimum retention BCE0.000004791201; all30 epochs retain18/18 accuracy
at0.85. Process350.552s including preflight,79.808s post-preflight training/result
phase,torch2.7.0/MPS.106 Python tests and offline Swift build/123 tests pass; saved
checkpoint and all epoch selection scores verified. No independent transfer test,
export, promotion, final-challenge scoring or second run. Full qualification blockers
remain unchanged. [Handoff](../reports/work/FDR-009/handoff.md). Next: separately
assigned same-input48-frame development comparison, not additional training.

**2026-09-27 local Simulator training data admitted:** user-authorized exclusive
TTR/Fixture workflow completed40 new native-bracket pairs plus12 prior pairs.
All52 reviewed pairs admitted to a new training extension:273 total training pairs
and unchanged9 retention pairs.234 exported files verified;104 crops contain102
distinct pixels. Two positive crops repeat, but no whole pair duplicates. Six
appearance presets across grid/media and the prior dock add procedural diversity,
not independent sources or native Photos coverage. No source manifest rewritten.
Nine-control dock failed strict native-bracket identity; five matching recipes
were not attempted. Request published to TTR; four-control data work completed
independently.93 focused tests and offline Swift build/123 tests pass. No model
run/inference launched; original coverage/selection gates remain unchanged.
Actual trainer preflight completed: configuration valid, launch correctly blocked.
[Expansion handoff](../reports/work/SIM-FOCUS-DEV-01/expansion-handoff.md).
The concrete [retention-selected development experiment](../reports/work/SIM-FOCUS-DEV-01/selection-decision.md)
was subsequently approved and completed as FDR-009 above. Remote pairing/switching
remains unqualified. [Visual review](../reports/work/SIM-FOCUS-DEV-01/expansion-visual-review.md).

**2026-09-27 offline focus diagnosis complete for review:** all3,744 retained
probabilities reproduce published results;2,107 image files pass integrity,
all221 candidate +9 retention pairs audited. Both candidates rank true focus strictly
first on only1/48 frames. FDR-008 retains22 wrong and24 no-focus outcomes despite
fewer false positives. No threshold-only unique-selection repair for47 frames with
a strictly higher wrong competitor. Geometry/cue differences are hypotheses, not
causal findings. Recommend targeted additional source-separated data, not unchanged
retraining. [Handoff](../reports/work/FOCUS-OFFLINE-DIAG-01/handoff.md).
68 Python tests,offline Swift build/123 tests pass; no validation inference/challenge
analysis. Source/Photos gates remain open. TTR shared revision1's outdated two-frame
grant and exact receipt-schema requirements published/read back under existing request.
Live adapter/Photos acceptance unqualified; two Photos originals pending receipt.

**2026-09-27 P0 integration priority — human-approved external TTR control:**
The maintainer confirmed the two Office Photos captures are correct and show
different focus states, but judged the manual iteration flow unusable. Capture
proof achieved; one human-confirmed candidate pair, zero consumer-admitted pairs
pending original-byte receipt, bounds review and production-crop QA. No native-label,
training, independent-source or model gate passes; the full10-pair pilot is incomplete.
Local diagnostic adapter remains verified by96 Python tests and offline Swift
build/123 tests; no code or model changed in the request tranche.

[Formal TTR request](Plans/TTRSupervisedExternalControl.md) now has highest next
integration priority: human-approved external-client pairing and scoped qualified
lease, integrated readiness/capture/verified delivery/review/cleanup. The observed
38m42s to two successful captures includes manual/agent delay, not backend latency.
Producer implementation/deployment is not assigned by this request. Reuse existing
MCP work; no dependency on better models, native Photos telemetry, VoiceOver or DS-G8.
[Request handoff](../reports/work/TTR-EXTERNAL-CONTROL-01/handoff.md).
No Office session/lease cleanup receipt has been observed; current occupancy is unknown.

**2026-09-27 highest-priority tvOS focus intake/evaluation:**
[Metrics and next decision](../reports/work/APPEAR-EVAL-RESERVE-20260927/metrics.md).
All96 transferred pairs pass strict native-label/crop intake. On48 validation frames
with all24 candidates, shipped FocusRing yields0 uniquely correct; FDR-007 and008
each1. FDR-008 reduces false positives but misses46/48 focused targets. No replacement
is recommended. All3,744 predictions are accounted for;48 final-challenge pairs remain
unscored. Exact pixels are disjoint from3,789 prior images, but independent renderer/
journey qualification remains blocked on source review; genuine Photos buttons and
non-dark support are absent. The retained221+9 candidate assembly is rebuilt with
explicit runtime requalification after460/460 crops matched exactly. Actual trainer
preflight confirms valid configuration but blocks launch on10 independent-coverage
requirements and missing separate approval.105 Python and123 Swift tests pass.
[Review-ready handoff](../reports/work/APPEAR-EVAL-RESERVE-20260927/handoff.md). No training,
export, promotion or device work. [Next assignment](../reports/work/APPEAR-EVAL-RESERVE-20260927/next-assignment.md).

**2026-09-27 Run013 evaluated; DS-G8 remains open (no shipped model change):**
[Review-ready handoff](../reports/work/IOS-R013-EVAL/handoff.md). Training completed
106 epochs, best91. All19,740 r7 image/label pairs passed source-backed integrity
checks; zero decoded duplicates/cross-split pixel groups. All2,400 test predictions
succeeded. On the identical2,000 withheld-family cases, supported13-class custom
mAP50 improves **0.5549→0.6322** (+0.0773), mAP70 **0.4310→0.5834**,
mAP90 **0.2302→0.5299**, mAP50–95 **0.3982→0.5707**. Compatible retained Run009
predictions were reused; historical original-corpus0.586 is not a delta baseline.
Addon400-image mAP50 **0.9785** is within-family only; combined2,400-image/38-class
**0.8790** is supplementary, not a gate pass. homeIndicator, unknown and webContent
remain unavailable, and28 classes lack withheld-family support. Secondary buttons,
page controls, list rows and image views still fail the per-class floor; toggle
regresses. Next independent iOS assignment: source-label/geometry review and
independent coverage specification, then a separately approved measured experiment.
No training, export, promotion or capture was started; TTR/Photos is not a dependency.
Software verification:23 focused Python tests, offline Swift build and123 Swift tests pass.

**2026-09-23 iOS r6 Run 009 baseline completed (no shipped model change):**
[Handoff](../reports/work/IOS-R6-BASELINE-20260923/handoff.md) establishes the replacement-corpus
baseline across all 2,000 holdout test images in `r6` using Run 009 `best.pt`.
Supported 13 classes mAP@0.50 = **0.5549**, mAP@0.50:0.95 = **0.3982**.
Per BP-52 and P2-METRICS, the remaining 28 unsupported classes are reported as `unavailable`
without imputing AP 0.0. Complete `prediction-artifact-v1` document exported and verified with
`reference_comparison.compare` (2,000 samples accounted for). Frozen 250-member P3 regression
suite selected via `regression_selector` with zero leakage. Actionable error analysis published;
DS-G8 remains open.

**2026-09-23 r6 reconstruction completed (no shipped model change):**
[Handoff](../reports/work/IOS-R6-20260923/handoff.md) seals16,940 replacement pairs:
12,540 train /2,400 validation /2,000 test. Added2,600 native renders, preserved the
14,340 prefix and2,323 rejected trials, with zero decoded duplicates/leakage.
Only mutable Finder metadata is excluded from the content seal; strict audit and
metadata remain retained. Visible class support is39/12/13 of41, so this is not
complete-class training qualification or DS-G8. Six development probes passed
independent intake and visual review. No generation is running. Next: separately
authorized Run009 replacement-holdout baseline; independent backup remains open.

**2026-09-23 approved reconstruction count correction:** the maintainer approved
12,540 train /2,400 validation /2,000 test, preserving16,940 total and family
assignments. This supersedes the pending count-decision wording in older audit
notes below. Validator defaults now use the approved allocation; original expected
counts remain available for historical reproduction. No pixels were moved or
generated by that count-only amendment; subsequent r6 completion is documented above.

**2026-09-23 unshipped focus execution diagnostics:**
[FOCUS-RECEIPT-01](../reports/work/FOCUS-RECEIPT-01/handoff.md) adds optional detailed
request/session/recognizer receipts, loader-bound identity and recoverable operational
model-resource errors.123 offline tests pass. TTR's older package pin remains without
this API until adoption; no accuracy improvement, live qualification or model promotion
is implied. The shipped artifacts below are unchanged.

**2026-09-23 visual-state inventory (not a model change):**
[DATA-VIS](../reports/work/DATA-VIS-20260923/handoff.md) rehashed14,340 preserved
sidecars and revalidated12 retained status-axis probes. Theme/profile/type and
clock/charge schedules are coupled despite balanced marginals. Enabled/selected
fields are writer defaults throughout this prefix, not state-training truth.
[Targeted additions](Plans/VisualStateCoverage.md) prioritize truthful state
provenance and independent schedules; preserved corpus and training gates unchanged.

**2026-09-23 temporal focus diagnostic:**
[TEMP-FOCUS-DEV](../reports/work/TEMP-FOCUS-DEV-20260923/handoff.md) completed36
retained-image replays with production change primitives and cached model scores.
On9 reference→focus cases, diff localization9/9 and shipped+diff6/9 versus shipped
single-frame0/9; on18 constructed focus switches diff yields2 correct/2 wrong/14
abstentions. This supports exploring temporal proposals, not replacing focus
verification. Native oracle boxes, source-related development images and constructed
transitions are not live navigation or unseen-interface qualification. No new model.

**2026-09-27 earlier TTR receipt (consumer diagnostics completed above):**
[Highest-priority next tranche: tvOS focus intake, validation baseline and candidate
proposal](Plans/FocusAppearanceAcquisition.md#next-tranche--received-data-intake-and-validation-baseline-2026-09-27)
was subsequently approved and executed for local diagnostics; independent qualification remains open.
[Completed receipt](../reports/work/TTR-STATUS-20260927/receipt.md). Four frozen seed7
surface-v1 archives (696,220,140bytes) and manifest are retained in the new gitignored
`dataset/tvos_captures/frozen-surface-receipt-20260927/`, with exact local hashes/sizes
verified.43.68GB remains free. Immutable shared receiver receipt and status readback
pass. Archive safety and embedded group/role/job/seed/freeze bindings pass;24 rows
per group. No extraction, inference or training. Next is crop/label/independence
intake, not recapture or another transfer approval. Preserve the frozen evaluation
roles despite three embedded `training` defaults. Photos and VoiceOver alignment
remain separate gaps; sender cleanup/acknowledgment is not yet observed.

**2026-09-26 independent-evaluation preparation (handoff advanced above):**
[APPEAR-EVAL-RESERVE handoff](../reports/work/APPEAR-EVAL-RESERVE-20260923/handoff.md).
Actual assembly now binds the native-retention reference:221 candidate pairs and9
retention pairs, unchanged sampling/membership, zero cross-partition conflicts.
TTR's source-backed response now supplies four independently authored surface-v1 groups.
Freeze: `cinema_rows`/`album_grid` for appearance validation and
`memory_mosaic`/`icon_shelf` for final challenge, all seed 7. The installed tvOS 26.5
Simulator has no Photos app. NUIAK nevertheless retains one historical physical-TTR
Photos screen at `dataset/tvos_captures/office_photos_focused_shared.png`; it is
development-only because its sidecar has `elements: []`, it has no paired native focus
labels, and it is absent from the FocusRing training manifests. Capture authority,
transfer, consumer intake and evaluation freeze remain separate gates. No new capture,
training or model improvement is claimed.

**2026-09-23 integrated appearance evaluation:** [handoff](../reports/work/APPEAR-FAMILY-EVAL-20260923/handoff.md).
Pinned cda0a32 source resolves consumer drift; all9 new pairs/18 crops qualify for
simulator development. Combined19-pair diagnostic: shipped TP6/FN13/FP6/TN13;
FDR-007/008 each TP0/FN19/FP0/TN19 at0.85. All models have0/9 uniquely correct
base-frame focus decisions; crop sensitivity remains substantial. Not an independent
holdout or production recommendation. Expanded proposal221 train-candidate pairs
+9 retention pairs preserves50/50 logical-source mass and known seed7 lineage.
Exact native retention reference is prepared (18 samples, floor1.0), subsequently bound
in APPEAR-EVAL-RESERVE's incomplete assembly. Untouched evaluation groups/approval remain
missing. No capture, training, export or promotion.

**2026-09-23 APPEAR-B1 software delivered:** [handoff](../reports/work/APPEAR-B1/handoff.md)
integrates a separate balanced-development contract into assembly/trainer preflight.
212 candidate training pairs +9 native retention-validation retain their source roles;
native and both Fixture adapters receive50/50 logical-source mass.91 Python tests,
offline Swift build and107 Swift tests pass. Actual preflight correctly rejects launch:
independent appearance validation/challenge, frozen selection reference and explicit
approval remain absent. No new model run, inference, export or promotion.
The [reservation follow-up](../reports/work/APPEAR-B1/reservation-binding/handoff.md)
closes an evaluation-admission gap: v2 reservations bind exact reviewed source and
membership, not family names alone.59 affected Python tests pass; no new real
evaluation inputs have been admitted.

**2026-09-23 delivered appearance intake:** [receipt](../reports/work/APPEAR-C/visual-intake/handoff.md)
qualifies10 delivered pairs/48 files/20 unique production crops for simulator development.
Archive hash, native labels, geometry and visual review pass; no exact overlap against458
scoped prior samples. All seed7 siblings remain development, not independent evaluation.
Delivery blocker resolved; no new weights or training. Producer reports newer family
source/offline work, with live evidence still pending. APPEAR-B1 integration is next locally.

**2026-09-23 appearance-v1 consumer support:** [continuation](../reports/work/APPEAR-C/appearance-v1/handoff.md)
passes3/3 producer vectors,43 focused/integration tests and the actual crop CLI;
all12 retained catalog pairs remain valid. Offline Swift build and14 XCTest/93 Swift
Testing pass in the approved host context, resolving the earlier test-context blocker.
New10-pair archive intake awaits local delivery. No new data eligibility, model weights
or training claim; distinct appearance/final-evaluation coverage remains open.

**2026-09-23 05:54Z replacement build check:** [evidence](../reports/work/APPEAR-C/recheck-0543/report.md)
confirms changed app/helper/Fixture and eight passing infrastructure checks. TTR reports
ten appearance-v1 pairs; NUIAK has not received the archive. Our recipe-hash consumer
matches0/3 new appearance vectors: next fix is local contract support and intake, not
another producer rebuild. High-contrast/Photos-like and independent evaluation coverage
remain open. No new capture, scores, weights or qualification claimed.

**2026-09-23 catalog qualification:** [APPEAR-C](../reports/work/APPEAR-C/handoff.md)
captured/validated12 catalog pairs across3 themes;8 distinct pairs because all
high_contrast crops equal dark.54 exported files verified,24 production crops
reviewed. Zero pixel overlap with434 audited prior samples, but only one renderer
family: independent validation/final challenge still absent. No scores/training.
Fixed existing destructiveButton extraction omission;23 focused tests/build pass;
full Swift tests remain blocked by restricted Vision/CoreML runtime/cache access.

**2026-09-23 TTR dialog path qualified:** [genuine smoke](../reports/work/TTR-CATALOG-01/smoke-0514/handoff.md)
completed2/2 pairs and NUIAK v2 intake/four production crops. Bundled caller-owned
chunk exporter succeeds; signed CLI export staging still denied. Postflight healthy,
ownershipclear. Data development-only; no training/model gate passed. Next catalog
and appearance qualification, not more build/readiness loops for this dialog path.

**2026-09-23 05:11Z TTR replacement-build recheck:** [TTR-CATALOG-01](../reports/work/TTR-CATALOG-01/handoff.md)
now verifies changed Fixture code and passing Top Shelf HTTP/CLI status; exact-target
readiness passes. Missing-new-build blocker resolved. Default scene still no_sample;
no recipe applied, so bounded two-control capture smoke is next, not another rebuild.
Corrected Sillycon4-pair catalog separately awaits transfer/intake. No training or
promotion. FDR-008 remains experimental with known Home/Photos failures.

**2026-09-23 appearance lineage/proposal:** [APPEAR-B](../reports/work/APPEAR-B/handoff.md)
audited202 proposed training pairs,9 native-validation and6 protected Remotes pairs.
All162 Fixture pairs share connected training lineage; no new independent appearance
holdout exists. Proposed source mass50/50 replaces prior11/89 only in a future reviewed
protocol. Next unblocked APPEAR-B1 adapter/preflight integration; no training launched.

**2026-09-23 authorized appearance pilot:** [APPEAR-A2](../reports/work/APPEAR-A2/handoff.md)
completed24 recipes/100 frames/76 development pairs independently of TTR desktop.
At0.85 FDR-008 detects73/76 focused examples with0 false positives; shipped11/76
with9 false positives. Six individual crops overlap training; this is not an
independent holdout and does not close Home/Photos failures. Fixed local4K crop
batching without recapture. Next APPEAR-B lineage/sampling/evaluation proposal;
no new weights or promotion.

**2026-09-23 appearance capability audit:** [APPEAR-A](../reports/work/APPEAR-A/handoff.md)
pins current Fixture source and finds fixed-gradient media cards, standard grid
buttons and unconsumed randomization attributes, not Home artwork/dock diversity.
A24-group/76-target development catalog now has [verified planning and intake
software](../reports/work/APPEAR-A1/handoff.md); the subsequently authorized pilot
is reported above. TTR rendering request published/read back, acknowledgment
pending. This is source evidence, not current installed-runtime qualification.

**2026-09-23 FDR-008 appearance check (not qualified):**
[FOCUS-VISUAL-03](../reports/work/FOCUS-VISUAL-03/handoff.md) finds0/8 correct unique
Home/Photos decisions despite perfect Fixture training fit. Home false positives
rise0→5 versus FDR-007 at0.85;532 correlated crops/model compared with unchanged
production preprocessing. No export/promotion. Next APPEAR-A/B: audit supported
appearance and label sources, acquire separately authorized ground-truth diversity,
then independent evaluation. Do not repeat same-data training or tune on known failures.

**2026-09-23 FDR-008 completed (experimental, not shipped):**
[Mixed-appearance run](../reports/work/FDR-008/handoff.md) finished30/30 epochs;
epoch3 selected by native-validation loss. At0.85, Fixture training fit improved
75%→100% on172 crops; native validation18/18 and Remotes challenge12/12 retained.
This demonstrates learning on reviewed examples, not unseen Fixture generalization.
The shipped model remains unchanged. Next evaluate retained Home/Photos and new
independent Fixture appearances before export/promotion or further training.

**2026-09-23 development-experiment integration (no new model):**
[FOCUS-DEV-01](../reports/work/FOCUS-DEV-01/handoff.md) freezes 126 training pairs
and nine native-validation pairs through real assembly and trainer dry-run. All
bytes/crop parity/splits passed; launch is blocked only by missing experiment
approval. Production mode correctly rejects the protocol. 63 focused Python tests
and offline Swift checks pass. Next review/authorize the single development run
or revise its sampling balance first (88.89% expected Fixture /11.11% native).
No independent Fixture validation, production admission or training is claimed.

**2026-09-23 retained-data review (no new model):**
[FOCUS-RETAINED-01](../reports/work/FOCUS-RETAINED-01/handoff.md) audited 36 recipes /
138 pairs and all 276 production crops. Visual review yields 86 distinct non-maze
development candidates; four exact pair duplicates and 48 maze pairs are excluded
from the proposed experiment. Seeds 7/19 share pixels and cannot be split between
training and validation. The six missing kitchen-sink recipes remain missing.
38 Python tests and offline Swift checks pass. Next implement the bounded
development-experiment contract, then seek one-run authorization; no new capture,
training, production data admission or model qualification has occurred.

**2026-09-23 mixed-source software (not a model release):**
[OS-FOCUS-04 assembly](../reports/work/OS-FOCUS-04-ASSEMBLY/handoff.md) integrates
49 retained native pairs and2 direct dialog pairs with immutable lineage/splits,
training-only sampling and actual trainer preflight. Old root crops were preserved
and refreshed offline through current production preprocessing, with24 new crops
reviewed.89 focused tests and offline Swift checks pass. Configuration is valid;
full training remains blocked by source/corpus approval, test membership and quotas.
Next qualify diverse retained Fixture development groups and freeze one separately
authorized mixed-appearance experiment. No new capture, training or weights.

**2026-09-23 consumer software:** strict TTR sidecar-v2 intake, development-only
v1.5 production crops and existing baseline/preflight integration are verified by
83 focused Python tests plus offline Swift checks. The peer acknowledged the
kitchen-sink request and reports a repair, but its exact advertised artifact path
is absent locally. No new capture, genuine v2 bundle qualification, or training.
Preserve36 recipes/138 pairs; next obtain the exact repaired artifact and qualify
only the missing boundary/groups. [Handoff](../reports/work/SIM-DATA-02-V2/handoff.md).

**2026-09-23 superseding direct-pilot progress:** authorized separate-copy Fixture
metadata cleanup, existing-signature verification, and exact-simulator installation
succeeded (dylib `46011bb0…`). Repaired media capture passed; retained pilot now
contains 36/42 recipes and 138 pairs. First kitchen-sink recipe stopped with
`no_sample`: source routes it to Components, not the native-probed procedural scene.
Six recipes/108 pairs remain. Focus Maze bottom-row clipping needs explicit review.
No full-pilot admission, baseline, training, or promotion claimed. Preserve partial
evidence and continue only after reviewed producer repair.
[Evidence](../reports/work/TVGEN-SETUP-20260923/handoff.md).

**2026-09-23 00:22Z repair available in source, not runtime:** producer6093663
implements measured-only geometry and sidecar v2. Running Fixture is still the old
binary. The existing repaired candidate fails local strict signature verification
(filesystem detritus), so it was not installed. Need a valid candidate and explicit
Fixture setup authority before the authorized resumed pilot. SMB mount absent;
feedback retained locally. [Evidence](../reports/work/TTR-CHECK-20260923-0022/handoff.md).

**2026-09-22 23:06Z continuation software:** missing-group execution and full-catalog
assembly now integrate with the existing production-crop/baseline entrypoints.
32 Python tests and offline package checks pass; real retained12 recipes/30 pairs
re-audited unchanged. No data admitted or training launched. The22:57Z Fixture check
still finds the unchanged media-header defect. Next is corrected-geometry boundary
qualification, then30 remaining recipes/216 pairs—not more resume scaffolding.
[Evidence](../reports/work/TVGEN-RESUME-02/handoff.md).

**2026-09-22 22:15Z repair check:** Fixture is now natively settled/ready, superseding
the initial zero-sample observation; unchanged dylib still reports inconsistent
media-header geometry. Producer commit3667185 addresses export, not that repair.
Direct pilot awaits geometry and reviewed multi-run completion; it does not depend
on the separate exported-sidecar repair needed by TTR intake. No capture retried.
[Evidence](../reports/work/TTR-CHECK-20260922-2215/handoff.md).

**2026-09-22 21:46Z superseding progress:** retained TTR bundle transferred through
documented read-job IPC (12 files verified); NUA numeric-date compatibility fixed,
but strict normalization rejects producer's omitted resolved theme. Independent
direct dialog capture/crops/inference now works: two development pairs, shipped
model TP2/FP2 on four crops. The42-recipe direct pilot completed12 recipes/30 pairs
before media_shelf header coordinate conflict (1920-based bounds in3840 scene).
Partial run preserved, zero pilot pairs admitted; native reference/postflight healthy.
No training/promotion. [Evidence and exact resume](../reports/work/TTR-SMOKE-20260922-2119/continuation.md).

**2026-09-22 21:25Z integration update:** the local two-element dialog smoke now
completes: two accepted calibration pairs/four PNGs, zero rejections, healthy
postflight and clear ownership. Export fails with `serviceUnavailable` despite
working manifest/receipt IPC; pixel intake and crop qualification remain unperformed.
Reuse completed job697018C6 for export diagnosis, not recapture. Prior dialog
geometry failure is superseded; other families and full training-corpus gates are
not qualified by this smoke. [Evidence](../reports/work/TTR-SMOKE-20260922-2119/handoff.md).

Latest Home evidence: [FOCUS-VISUAL-02](../reports/work/FOCUS-VISUAL-02/handoff.md)
compares six reviewed frames/72 tiles: at0.85 shipped makes2/6 correct unique
selections; FDR-007 FP16/int8 make0/6. Candidates'91.7% tile accuracy is the
all-negative baseline. Box variants expose wrong-focus decisions and int8 drift
up to0.09253 with threshold disagreements. No candidate promotion. Next implement
OS-FOCUS-04 mixed-source assembly/preflight offline, then separately authorized
eligible mixed-appearance acquisition/training. These legacy reviews remain
development-only and cannot train the model.

Earlier regression evidence: [FOCUS-VISUAL-01](../reports/work/FOCUS-VISUAL-01/handoff.md)
compares three models on two reviewed Photos frames without TTR. Shipped recognizes
1/2 visibly focused buttons; FDR-007 FP16/int8 recognize0/2. Four-pixel box variants
expose multiple-focus false positives and int8 probability drift0.04346 (>0.01),
despite unchanged threshold decisions. Preserve old Settings results as scoped;
neither candidate is ready for replacement. The Home follow-up above extends this
finding; do not repeat same-style Settings epochs.

Latest local tranche: [FOCUS-COMPRESS-01](../reports/work/FOCUS-COMPRESS-01/handoff.md)
produced one experimental int8-weight candidate:2,612,925 bytes (48.14% smaller),
zero decision differences from preserved FP16 on12 frozen crops; max drift
0.000000715255. Size gate now passes for this candidate, not the preserved FP16.
Warm CPU inference is essentially unchanged; no broad model gate/promotion claim.
[PER-DATA](../reports/work/PER-DATA/handoff.md) accounts for44 existing screenshots:
39 development-only negative-scene reviews, including2 Photos appearance-focus
labels/four boxes;5 exclusions. No admitted positive chevron/dialog examples or
independent benchmark. Next broaden visual challenge coverage, not same-style
retraining. All shipped artifacts remain unchanged.

Latest export: [FOCUS-EXPORT-01](../reports/work/FOCUS-EXPORT-01/qualification.md)
completed in an approved isolated non-cloud environment (Python3.12/Torch2.7/
coremltools9). Import8.90s, export3.47s, compile1.14s; genuine CPU parity passes
all12 frozen native challenge crops, maximum probability error0.00000357628.
This bypasses old iCloud dataless dependencies without repairing/changing them.
Experimental package5,038,123 bytes passes the legacy5MiB calculation but fails
literal5MB. Exporter now enforces5,000,000 bytes; fresh sizegate export correctly
exits1,70 Python/93 Swift tests pass. Existing challenge has zero near-threshold
cases and only one Settings screen. The assigned compression above supersedes
the proposed export follow-up; broader visual capture remains separate. No production replacement or
automatic retraining. [Follow-up](../reports/work/FOCUS-EXPORT-01/size-and-coverage.md).

Latest independent tranche: [OS-FOCUS-03/04](../reports/work/OS-FOCUS-03/handoff.md)
added3 Apps training pairs and6 Remotes challenge pairs. FDR-007 completed8 epochs
on40 train/9 validation pairs:18/18 validation,12/12 challenge decisions at0.85.
FDR-006 also scores12/12 challenge versus shipped CoreML5/12: no demonstrated
incremental gain. Native Settings acquisition/training works without TTR. Home
remains locally blocked on stable HeadBoard focus observations; zero Home samples
admitted. Next prioritize different focus appearances and export parity, not more
same-style training. No shipped replacement or release/physical-device claim.

Latest learning result: [FOCUS-EXP-01](../reports/work/FOCUS-EXP-01/handoff.md)
completed four native-focus training arms independently of TTR.46 reviewed pairs:
37 training/9 validation, grouped by Settings screen. Warm+production-stretch
achieved18/18 validation decisions at0.85 (shipped CoreML7/18); scratch+stretch
also18/18 but learned later. This is tiny same-app validation, not a final-test or
release gate. No crop-default/model replacement. Next: independent Home/style
challenge data and runtime parity investigation; no automatic training loop.
This supersedes the pre-training bottleneck in the older snapshot below.

Latest native focus development evidence (2026-09-22): independent Settings-root
sweep produced 12 reviewed focused/unfocused pairs with production crops; shipped
classifier at0.85 yielded TP1/FN11/FP3/TN9. [Evidence](../reports/work/OS-FOCUS-02/handoff.md).
Capture is unblocked independently of TTR. Broader independent data partitions,
not another identical sweep, are needed before candidate training. Shipped weights
are unchanged; this is development evidence, not a model gate.

| Artifact | ID | Notes |
|---|---|---|
| iOS 5-class detector | `nativeui-ios-v2.0` | YOLO11n, mAP@0.5 = 0.935 CoreML / 0.968 `.pt`. Latency ~7.5 ms/image. |
| tvOS OS UI detector | `nativeui-tvos-v3.0` | YOLO11n, 25 trained classes, mAP@0.5 = 0.9822. Bundled as `NativeUIModel_tvOS.mlmodelc`. |
| Stage 2 focus classifier | `focus-ring-detector-v1.0` | MobileNetV4-Conv-Small, FDR-001. FP16 4.80 MB. Bundled as `FocusRingDetector.mlmodelc`. Torch test 270/270. Hard-neg n=0. |
| Detection API | `NativeUIDetectionRequest` | YOLO letterbox inference, OCR fusion, audit rules, device inference, optional FocusRing Stage 2. |
| Perception primitives | Frame similarity, change-ROI, text-anchor verify | Track 4, for TVTestRig to consume. |

Phases **0–5b**, **6** (5-class), **6d**, **6-gate (skipped)**, **6b-S / WP1 / E**, **6b-R-2 / R-3**, **6b-FD-01–04**, **7**, **8**, **9-1**, Track 4, extraction checklist: **complete.** See [`CompletedTasks.md`](../CompletedTasks.md).

---

## Not shipped

**2026-09-22 18:30Z updated Fixture:** both binaries changed, source852f341d
matches producer focus-handoff receipt. Local job675C0665 fails earlier reference
geometry: only container measured, both dialog buttons missing, fresh native
reference focus. Neither target transition reached; no completed bundle/intake.
Producer's other-simulator transition proof does not qualify this full capture
path. Postflight healthy/ownershipclear; geometry diagnostic request published
and read back, acknowledgment pending.
[Evidence](../reports/work/TTR-CHECK-20260922-1827/handoff.md).

**2026-09-22 18:08Z TTR smoke:** changed TTR comparator passes reference stage.
Fresh Fixture process has the same dialog-capable code hash. JobE5BCE43B fails
first target handoff: requested dialog_btn_0, actual native reference still focused,
fresh observations and complete geometry, stableMilliseconds0. Neither target
capture nor completed export/intake qualified. Postflight HTTP healthy,8 readiness
checks ready, ownership clear. Producer request published/read back, acknowledgment
pending. [Evidence](../reports/work/TTR-CHECK-20260922-1805/handoff.md).

**2026-09-22 dialog smoke:** native reference focus now verified and settled,
but job661FFE7C fails `telemetry_bracket:identityMismatch` before target capture.
Producer full-scene equality includes changing diagnostic counters/timers; passive
snapshots preserve focus/recipe/geometry while these change. Exact failed bracket
samples were not returned. Zero completed bundle; export/intake blocked. Fresh
postflight HTTP healthy,8 infrastructure checks ready, ownership clear. No retry
or reset. [Evidence/request](../reports/work/TTR-SMOKE-20260922-DIALOG/handoff.md).

**2026-09-22 17:26Z TTR/Fixture:** changed local binaries and matching dialog-repair
source receipt now observed. Eight infrastructure checks ready, local ownership
clear, HTTP healthy. Passive shelf still non_view/unmapped_item (294 samples),
but shelf is explicitly outside the dialog-only candidate scope. Next qualify the
changed two-button dialog through a bounded authorized smoke/export/intake; no
new capture occurred in this read-only check. Do not carry the producer's other-host
cleanup guard onto the locally clear target. [Evidence/status](../reports/work/TTR-CHECK-20260922-NEW/handoff.md).

**2026-09-22 16:29Z TTR/Fixture update:** new local app/companion and persistent simulator
remote interface observed; all eight exact-target infrastructure checks ready,
ownership clear. Installed Fixture bytes remain identical to the prior failing
artifact. Following Fixture relaunch, HTTP health is restored; fresh passive
telemetry (412 samples) still reports native focus non_view/unmapped_item on the
current media_shelf scene. No new capture or two-element smoke. Producer crop repair source matches its receipt;
offline corrected-crop replay subsequently passed on 2026-09-23: 10/10 exact crops
and same-CPU scores ([report](../reports/work/FOCUS-PARITY-01/corrected-20260923/handoff.md)).
This scoped preprocessing result does not establish model accuracy or live navigation. This is
not a new storage regression or a block on independent native NUA work.
[Fixture follow-up](../reports/work/TTR-CHECK-20260922-1622/fixture-followup.md).

**2026-09-22 parallel acquisition:** direct HTTP/simctl runner, development-only
v1.4 consumer and existing runtime-crop/baseline integration delivered;38 Python
and92 Swift tests pass. Matching installed Fixture launched and reference PNG
captured/visually checked. First focused target fails `non_view/unmapped_item`;
independent TTR job fails the same native-identity prerequisite. Fixture responsive,
ownership clear. Zero eligible pairs;42-recipe pilot and genuine baseline not run.
This supersedes the endpoint-unavailable and screenshot-only bottlenecks below.
[Handoff and producer request](../reports/work/TVGEN/handoff.md).

**2026-09-22 05:49 UTC diagnostic:** updated local TTR responds; exact-target
infrastructure readiness passes and ownership is clear. Repaired companion source
matches the producer receipt, but prior Fixture endpoint8080 refuses connection.
Capture/export/intake were not run; screenshot repair is locally unqualified, not
newly failed. [Diagnostic feedback](../reports/work/SIM-DATA-01-02/readiness-20260922-0548/handoff.md).

**2026-09-22 01:39 UTC smoke:** native reference focus now resolves and settles,
but screenshot output fails Cocoa513/EPERM writing frame.png in TTR's app-managed
capture directory. Zero accepted rows; no export/intake or training. Postflight
Fixture responsive and ownership clear. This supersedes readiness-only status below.
[Failure and producer request](../reports/work/SIM-DATA-01-02/smoke-20260922-0140/handoff.md).

**2026-09-22 01:34 UTC runtime check:** updated TTR/Fixture and repair checkout
fd50a80 are present; all infrastructure readiness checks pass with ownership clear.
Idle Fixture has no native sample yet. A new bounded smoke is ready to be authorized,
but capture/intake and training readiness are not established.
[Evidence](../reports/work/SIM-DATA-01-02/readiness-20260922-0134/handoff.md).

**Offline perception acceptance (2026-09-22):** PER-01 evidence inventory and
PER-02/04/05/06 offline scopes are accepted after integrated review/corrections.
[Acceptance](../reports/work/PERCEPTION-ACCEPTANCE/handoff.md). All 44 supplied
screenshots were visually triaged; no real gold-label benchmark or training corpus
was qualified. Screenshot output access remains the last observed producer blocker,
not the previously resolved native-reference focus failure. No new training or promotion.

| Item | Why |
|---|---|
| 41-class iOS YOLO11m | Run013 r6 withheld-family diagnostic mAP50 **0.6322** vs same-input Run009 **0.5549**,13 supported classes; DS-G8 ≥0.850 remains unmet. Historical original-corpus Run009 **0.586** is non-comparable. No41-class promotion. |
| FocusRing v1.0 | Need ≥6,000 pairs and non-vacuous `light`/`highContrast` hard-neg (FOCUS-DET-05). |
| macOS detector | Phase 6c not started. |
| Unified iOS+tvOS model | Phase 6b-U not started. Keep separate models until every gate passes. |
| Badge/42-class expansion | Approved later milestone; 41-class release remains first. No enum/map/model change has shipped. |
| ScreenAuditKit contract/CLI | TASK-9-2 / 9-3 live in ScreenAuditKit, not this repo's remaining core path. |

---

## Current bottleneck

**2026-09-22 native OS lane:** approved independent XCTest Settings recording
passed: six directional inputs, seven hash-verified states/four distinct frames,
native focus visually aligned. No TTR/Fixture required. A development replay of
four native rows across four frames found 0/4 focused positives and 4/12 unfocused
false positives at 0.85 through shipped NUIAK preprocessing/model. This is a tiny
single-journey diagnostic, not general accuracy or training readiness. Native OS
admission/Home coverage can progress independently; Fixture repair remains open.
[Evidence](../reports/work/OS-FOCUS-01/live-20260922-0712/handoff.md).

**Parallel path approved, 2026-09-22:** [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md)
defines direct native tvOS Fixture/OS generation independent of TTR capture/export.
Direct software and runtime inventory are now delivered for review; no corpus is
qualified. Both acquisition adapters currently share the Fixture native-focus
identity defect. TTR desktop acquisition remains independent; iOS reconstruction
is unchanged. See [current evidence](../reports/work/TVGEN/handoff.md).

**Legacy FocusRing reuse warning (2026-09-21):** the 1,500-pair crop corpus is
byte-decodable but not requalified. An audit found 84 identical-pixel groups crossing
partitions despite zero shared seeds; all examples are dark and frame-bound label
evidence is absent. Historical 270/270 and empty-hard-negative passes are not clean
qualification evidence. Preserve shipped weights; no automatic replacement follows.
[Audit and corrections](../reports/work/EVIDENCE-AUDIT/handoff.md).

**2026-09-21 FocusRing update:** local simulator runtime/storage readiness passed,
but the clean two-element smoke failed `native_focus_or_geometry_unavailable:
sceneNotSettled`; no eligible pilot exists. Broad simulator collection remains
paused. [Smoke evidence](../reports/work/SIM-DATA-01-02/smoke-20260921/executed-smoke.md).
**2026-09-22 00:35 UTC follow-up:** the newly authorized updated-build smoke also
failed, now narrowed to `unresolved_focus`: both buttons measured, no missing IDs,
36 native samples but no resolved focus. Inline recipe import succeeded after
file import incorrectly surfaced `serviceUnavailable`. Postflight Fixture responds
and ownership is clear; no completed bundle or training data. TTR diagnosis/fix
requested; no automatic retry. [Latest evidence](../reports/work/SIM-DATA-01-02/smoke-20260922-0031/handoff.md).
Offline [launch preparation](Plans/FocusRingLaunchPreparation.md) is delivered for
review: runtime-exact crops, actual CoreML baseline adapter and frozen capture
planning. A tested crop-origin correction changes inference preprocessing, not
shipped weights; historical runtime metrics cannot establish its quality. No
training or promotion occurred. The older operational snapshot below is historical,
not a fresh Office/producer readiness check.

**TASK-6a-10** — full-frame fixture retraining for 41-class iOS. Ingest scripts are written and unit-tested. Coordinator IPC was resolved on 2026-09-18; the later live batch gate is `identity_preflight` / `identityUnavailable` until TVTestRig's adapters attest a shared HarvestIdentity. Office is occupied as of 2026-09-19; an authorized hardware run is a separate prerequisite. See [the recorded evidence](../reports/tvtestrig_feedback_2026-09-18.md). Do not retrain on empty sidecars or the model's own `*_result.json` predictions.

Office-independent work is defined in [ImplementationPlans.md](ImplementationPlans.md); dispatch state lives only in Tasks.md.

**Accepted offline foundation (2026-09-19):** H1 and the NUIAK software scopes of
P1-A, P2-A, P3-A, P4-A, P4-B, P5-A, and FR-A are accepted. This establishes fail-closed
consumer, evaluation, assembly, preflight, and FocusRing-alignment interfaces only.
It does not establish eligible pixels, a genuine producer bundle, live capture behavior,
or a candidate-model gate; those remain separately blocked in `Tasks.md`.

For the explicit iOS five-class → 41-class path, use the
[iOS platform tasks](../Tasks.md#ios-platform-tasks) and
[five-tranche delivery plan](Plans/iOSPlatform.md). Corpus recovery, offline toolchain
acceptance, and eligible synthetic baseline evaluation do not require Office. Live
fixture qualification is a separate input to the planned mixed-data candidate.

The [iteration roadmap](IterationRoadmap.md) separates software acceptance from data/model qualification. H1 producer-contract work, export/selector/preflight software, and recovery assessment are independently dispatchable. TVTestRig has a documented offline bundle-validator lane at inspected revision `586050e`; consumer compatibility remains to be implemented/verified, and passing offline integrity is not trusted capture evidence.

The accepted full backlog is defined as independent revision-4 [worker packets](ImplementationPlans.md),
including later models and separately owned consumer work. [DeliveryDecisions.md](DeliveryDecisions.md)
keeps 41-class first, moves badge to a versioned later model, prioritizes FocusRing then macOS
after DS-G8, and separates software/data/integration/model outcomes. Publishing these plans
does not mark any worker implementation, experiment or quality gate complete.

**Replacement corpus available — TASK-DATA-01 (2026-09-23):** [r6 handoff](../reports/work/IOS-R6-20260923/handoff.md) seals16,940 pairs at12,540/2,400/2,000, zero duplicates/leakage, preserved prefix and rejected trials. Content readback verifies38,529 files/9.51GB; only Finder metadata is excluded explicitly. Visible support is39/41 train,12/41 validation,13/41 test. Missing class support, comprehensive semantic qualification and independent backup remain open. Historical pixels remain unavailable and historical Run009 metrics remain non-comparable. No native job is running; next is a separately authorized replacement-test baseline, not training. [Historical evidence](../reports/dataset_availability_2026-09-19.md), [recovery plan](DatasetRecoveryPlan.md), [preserved failures](../reports/work/P0-C/resumption-20260922.md).

FocusRing v0.1 is independent of that bottleneck and is already bundled.

---

## Train / eval pointers

- Run log: [`ExperimentLog.md`](ExperimentLog.md)
- Doc index: [`README.md`](README.md)
- Fixture ingest format: [`FixtureBatchIngest.md`](FixtureBatchIngest.md)
- Phase streams: [`PhaseMap.md`](PhaseMap.md)
- FocusRing: [`FocusRingDetectorSpec.md`](FocusRingDetectorSpec.md)
- Provenance: [`../PROVENANCE.md`](../PROVENANCE.md)
