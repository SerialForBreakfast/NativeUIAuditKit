# BACKLOG410 — repeatable experiment conversion and review

Owner: research-host-NUIAK. Date: 2026-10-15.

## Problem

The queue had 0 ready jobs, while the catalog had 105 open questions. Compute was idle because conversion was manual:

- Every batch was hand-written JSON. B405-002 needed 9 near-identical job descriptions.
- 100 catalog questions were boilerplate. The compiler ignored the catalog decision text.
- Every template job used the task `TEMPLATE395`. Results could not be grouped by question.
- No tool read results back. The decision index read 3 fixed output names, so it skipped `benchmark_summary.json`.
- The Tasks.md table was a hand-kept copy of the catalog.

## Process

The catalog `Research/Experiments/backlog405.json` is the single definition store. A record gets a `plan` block.
`scripts/backlog_pipeline.py` does each step:

| Command | Effect |
| --- | --- |
| `check` | Validates every plan against its template contract and adapter parameter checks |
| `expand IDs [--register --approve-listed]` | Writes `Research/Experiments/batches/<ID>.json`, then registers and approves exactly the listed new jobs |
| `review IDs` | Reads receipt-listed outputs, compares each arm with the control, and proposes an outcome |
| `confirm ID --outcome --by --note` | Records the confirmed outcome. Supported or contradicted closes the record. |
| `render-tasks` | Regenerates the Tasks.md table between the BACKLOG markers |
| `status` | Shows the ready jobs, the ready time from measured medians, and the refill warning |
| `blockers` | Ranks missing adapters, data, and decisions by the number of open records they block |

Supporting changes:

- `hcf_templates395.build` accepts optional `task`, `outcomes`, `hypothesis`, and `controlledComparison` fields. Absent fields keep the original spec bytes.
- `research_readiness.report` reads every small JSON output that an attempt lists.
- The dashboard has a Backlog panel with per-record progress and the refill warning.
- The [backlog-grooming skill](../../.agents/skills/backlog-grooming/SKILL.md) defines the 5-step cycle: review, confirm, render, plan and expand, report blockers.

Approval stays 1 record per job. Capture, training, export, and promotion keep their existing authority.

## Blocker ranking at handoff

| Missing input | Template | Open records | Records unblocked | Owner |
| --- | --- | ---: | ---: | --- |
| Fixture focus manifests with role ancestry (B405-041) | T03 | 11 | 40 | research-host-TTR |
| `detector-case-match` adapter (ENG405-02) | new | 23 | 35 | research-host-NUIAK |
| iOS native capture adapter (ENG405-03) | T03-ios | 10 | 20 | research-host-NUIAK |
| `temporal-evaluation` adapter (ENG405-05) | new | 12 | 14 | research-host-NUIAK |
| Difficult-case deployment membership | T11 | 8 | 10 | research-host-NUIAK |
| Screen-context and later-model data | future-model | 10 | 10 | research-host-NUIAK |

Rerun `backlog_pipeline.py blockers` for the current ranking.

## Results — box geometry tolerance of the HCF crop classifier

All jobs use T41 on the same 74 retained development frames: 37 HCF and 37 Standard, in 10 groups.
The crop model is `hcf375c-70-crop-train`, and the threshold is 0.85. The control is the unchanged known box: 35 of 36 focused HCF and 36 of 36 Standard frames are correct.
The 28 new jobs take about 18 s each. Results are in `Research/Experiments/results/`.

### B405-002 — tall-control regression (confirmed: supported)

A known-box translation of (+0.78, −1.11) px loses 2 tall-control successes. A margin change of the same size loses none.
Displacement, not lost context, explains the mapped tall-control loss.

### B405-073 — displacement tolerance (confirmed: supported)

| Shift | ±0.5 px | −1 / +1 px | −2 / +2 px | −4 / +4 px |
| --- | --- | --- | --- | --- |
| Horizontal: lost successes | 0 / 0 | 2 / 2 | 2 / 1 | 10 / 2 |
| Vertical: lost successes | 0 / 0 | 1 / 0 | 1 / 16 | 30 / 15 |

A −4 px vertical shift also loses 9 Standard successes. The tolerance is about 0.5 px.

### B405-074 — size tolerance (confirmed: supported)

| Centered size change (total px) | −16 | −8 | −4 | −2 | +2 | +4 | +8 | +16 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lost successes (HCF and Standard) | 21 | 12 | 1 | 3 | 0 | 29 | 66 | 69 |

| One axis, 8 px | Width −8 | Width +8 | Height −8 | Height +8 |
| --- | --- | --- | --- | --- |
| Lost successes | 2 | 3 | 0 | 41 |

Growth is much more harmful than shrinkage. Height dominates.

### Decision

- The classifier decision depends on the exact vertical framing of the crop. A 2 px error can remove most correct selections, including Standard.
- Proposals cannot reliably meet a 0.5 px tolerance. Stop tuning mapping offsets and insets for this model.
- Next: train the crop classifier with geometric jitter in crop preparation. Re-crop each source with shifted and resized boxes, and compare it with the unjittered control.
- Accept the jittered model only if B405-073 and B405-074 arms lose no successes within ±2 px, and the unchanged known-box result keeps 35 of 36 HCF and 36 of 36 Standard.
- Limitation: these are inspected development groups, not an independent audit. Model acceptance stays false.

## B405-041

Check by research-host-NUIAK on 2026-10-15. Result: no T03 plan. The blocker is NUIAK work, not missing TTR output.

### What B405-041 measures

B405-041 compares observed eligible related groups with family, theme, and hard-negative quotas.
It is a count of pinned manifests against frozen quotas. It is not a capture.
New captures only add to the counts. They cannot change the B405-041 decision by themselves.

### Readiness evidence (read-only)

- research-host-TTR checkout: clean `master` at `b9ddb177`. `origin/master` on the remote is `48f0e37f`.
- The checkout is not updated. TTR AGENTS.md forbids all Git writes, which includes a fetch. NUIAK AGENTS.md permits `git pull --ff-only`. This conflict needs a maintainer decision.
- Simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` is booted. The Fixture answers at `http://127.0.0.1:8080/device`.
- The Fixture PID (37401), instance ID, run ID, and both binary hashes match the binding of the HCF402 plans.
- No capture recovery marker exists at `.build/fixture-generation-recovery.json`. The USB volume has 1.6 TiB free.

### Role ancestry already exists locally

The completed capture `hcf402-focused-r3` has full role ancestry in `scene.semantic_inventory.elements`.
Each element has a `role` and a `parent_id` or `declared_parent_id`. All 29 chains in frame 0 resolve to a `layout_region`. 0 chains are unresolved.
Example: `item-0/artwork` (`image_view`) → `item-0` (`control_wrapper`) → `region-0` (`layout_region`).
The `scene.elements` list does not contain the parent regions. Use `semantic_inventory` for ancestry.
The Fixture source supports `poster`, `thumbnail`, `button`, `row`, `tab`, `text`, and `artwork` components (`FixtureComposition.Kind`).

### Why the T03 path does not supply the inputs

The local T03 capture path is qualified, but only for 1 family:

- `native_coverage402.validate` accepts only `poster` and `text` components with `native_image` focus.
- It accepts at most 3 cases and 18 frames, with the `standard` and `hcf` profiles.
- Every case has the role `development`. Every plan has `study-pending` and `trainingEligible: false`.

A T03 plan can therefore add only artwork development groups. These groups are not eligible training groups.
Such arms cannot change the quota decision, so this check adds no plan block and expands nothing.

### Current corpus deficits already measured

The last corpus inventory is `reports/work/FOCUS-CORPUS-03/readiness-recheck-20261001/inventory.json` (2026-10-01).
It predates the HCF371 and HCF402 native captures. It shows these deficits:

- The training role has no `tabs` and no `keyboard` samples.
- All 6 scene archetypes are below `focus_ring_readiness.MIN`. Example: `gridMatrix` has 218 of 2000 pairs. `focusMaze` has 0 of 500.
- Development samples have unknown sources (315 samples), so they have no related-group ancestry.
- Hard-negative strata are not recipe-linked. The report does not infer them from `label=0`.

### Exact blockers

| Blocker | Kind | Owner |
| --- | --- | --- |
| A reusable quota comparison adapter. It reads pinned current manifests and `semantic_inventory` ancestry. It counts eligible related groups by family, theme, and hard-negative stratum against frozen quotas. | adapter | research-host-NUIAK |
| Frozen family and theme quota values. Only the scene-archetype quotas and the hard-negative floors (DeliveryDecisions item 7, ADR-0010 D1) are numeric now. | decision | research-host-NUIAK, with maintainer review |

The catalog record B405-041 now names these 2 requirements. `blockers` no longer groups it under research-host-TTR.

### Effect on dependents and on the TTR request

The 40-record count includes dependents with other needs. Two of them are separate capture work:

- Button, row, and tab manifests need a new NUIAK capture plan version with `native_button` focus (research-host-NUIAK). The Fixture already has these components.
- B405-046 needs a native keyboard component. The Fixture at `b9ddb177` has no keyboard component. The owner of Fixture source changes is not recorded here. capture-host-TTR or research-host-TTR must confirm it.

Item 1 of `reports/work/BACKLOG410/ttr-needs-request-DRAFT.json` asks TTR for role ancestry. The local Fixture already supplies it. This check does not edit the draft. Proposed replacement for item 1:
"(1) NUIAK confirms that current Fixture scenes supply full role ancestry in semantic_inventory. Please say whether a native keyboard component is planned for the Fixture (B405-046), and which machine owns that change."

### Decisions needed

- The maintainer decides whether an agent may fetch the research-host-TTR checkout, given the TTR rule against Git writes.
- The maintainer or an evidence-backed agent decision freezes family and theme quotas before the adapter registers jobs.
- No capture approval is needed for B405-041.

## Results — quota comparison (T44), 2026-10-15

Template T44 is `scripts/quota_comparison413.py`. Tests: `scripts/test_quota_comparison413.py`.
T44 reads pinned capture manifests and walks `semantic_inventory` parent links from each expected control to its `layout_region`.
It counts labeled control observations (the readiness pair unit) and related groups (plan group / case group).
It compares the counts with `Research/Experiments/focus-quotas413.json`. It reads no pixels and evaluates no model.

Quota file entries:

- Frozen (17 entries): scene minimums (`focus_ring_readiness.MIN`), the 0.2 scene theme share, hard-negative floors (item 7 and ADR-0010 D1), and 6,000 labeled pairs.
- Proposed (15 entries): 50 training groups for each family, and a 0.2 light or highContrast share for each family.
- A `frozen` run refuses a dimension that contains a proposed entry (`quota_unfrozen`). A `proposed` run is diagnostic only.

Inputs: 19 completed native captures (HCF371 and HCF402) in `Research/Experiments/quota-manifests413.json`. The runner executed 4 jobs, each in about 2 s.

| Arm | Eligible observations | Groups | Deficits |
| --- | --- | --- | --- |
| frozen-admitted (control) | 0 of 11,266 | 0 | 13: 6 scene, 6 hard-negative, total |
| frozen-any (diagnostic) | 11,266 | 342 | 13: 5 scene, 2 scene theme, 6 hard-negative |
| proposed-admitted (diagnostic) | 0 | 0 | 18: adds 5 family |
| proposed-any (diagnostic) | 11,266 | 342 | 19: adds 4 family, 2 family theme |

All 11,266 control chains resolve. 0 chains are unresolved.

### B405-041 — coverage against corpus requirements (confirmed: supported)

No current native capture is admitted. Every plan has `study-pending` and `trainingEligible: false`. All 13 frozen minimums are deficits.
If admission is ignored, the captures meet only gridMatrix (9,346 of 2,000) and the 6,000 total. They hold:

- 0 light or highContrast system-theme observations. HCF371 "light" cases are light backgrounds in the dark system theme.
- 10 no-focus hard negatives. All are dark, so 0 count toward the hard-negative floors.
- Only the artwork family: 250 training groups. Buttons, rows, tabs, and keyboard have 0.
- Only the gridMatrix scene. The other 5 scenes have 0.

The outcome does not depend on the proposed values. With 0 admitted groups, every positive family quota is a deficit.

### Decisions and next actions

- Image count is not coverage. Plan capture and admission by the largest named deficit.
- The largest deficits are admission of existing groups, light and highContrast system themes, hard negatives in those themes, and the button, row, tab, and keyboard families.
- Maintainer decision: freeze or change the proposed family and familyTheme entries. Then add a frozen arm with all 6 dimensions. Also confirm that quota themes mean the system theme.
- Rerun T44 with a new manifest list after each admission or capture. Do not edit the pinned list.

## Results — iOS and tvOS detector case matching (T42), 2026-10-15

All jobs use cached predictions. No inference runs and no model changes. iOS: Run 009 versus Run 013 on 2,000 withheld images and 17,862 labels, IoU 0.5. Label review status is unknown.
tvOS: nativeui-tvos-v3.0 on 46 reviewed real frames, 583 controls, confidence 0.50. Results are in `Research/Experiments/results/`.

| Record | Outcome | Finding |
| --- | --- | --- |
| B405-011 | supported | Run 013 loses 1,373 Run 009 successes and gains 1,436. The label class holds 1,305 losses. |
| B405-012 | contradicted | Class-agnostic matching recovers only 15 % of misses. Large recoveries only for toggle, secondaryButton, textField. |
| B405-014 | contradicted | 0 navigation bars missed. Run 013 adds 194 unmatched navigationBar boxes. |
| B405-015 | supported | All 341 secondaryButton labels are missed, 292 as another class. A coarse button group leaves 49 misses. |
| B405-016 | supported | Wide toggles (width 0.5–0.9) are predicted as listRow (232) or picker (151). |
| B405-017 | contradicted | No progress view is missed at 0.25. |
| B405-021 | supported | tvOS misses: collectionItem 131/301, listRow 124/224, tabItem 24/24; middle-left 124/172. |
| B405-026 | contradicted | Settings-row misses are localization or coverage failures, not taxonomy. |
| B405-107 | contradicted | Chrome-band extras fall 802 → 643, except top-center navigation bars (87 → 196). |
| B405-108 | supported | tvOS tab items get primaryButton (12) or no box (11). No reviewed tabBar labels exist. |
| B405-115 | contradicted | Label losses stay near 1,300 from confidence 0.05 to 0.40. They are missing detections. |
| B405-116 | supported | Run 013 keeps 13 of 800 middle-right labels and loses 97 of 100 top-left labels. Small labels hold 74 % of losses. |
| B405-117 | contradicted | Extra navigation-bar boxes keep high confidence: 194 at 0.25, 184 at 0.40. |
| B405-129 | contradicted | Duplicates are rare. All extra navigation-bar boxes and 297 textField boxes overlap no label. |

### Decisions

- The Run 013 regression is a label-class regression in specific places: middle-right and top-left labels, and small labels. Use these 3 slices as fixed regression guards for every iOS candidate.
- Thresholds do not fix it. Do not run a calibration study for the label class.
- pageControl is never detected. Its near boxes rise at lower confidence, so the failure is box fit. Review pageControl label geometry before training.
- Review the 194 navigationBar and 297 textField boxes that overlap no label. They may be unlabeled objects, not false positives. This review needs a person.
- Review button-role and wide-toggle label definitions before more button or toggle training (B405-015, B405-016).
- tvOS recall needs fresh inference below 0.50 (B405-023) and at 1280 px (B405-121). Both need a detector-inference template.
- The B405-011 comparison depends on the operating point: at 0.40, Run 013 nets +405 against Run 009. Report it at a fixed, stated confidence.

## Results — tvOS confidence and input size (T43), 2026-10-15

| Record | Outcome | Finding |
| --- | --- | --- |
| B405-023 | contradicted | Production at 0.10 finds 68 more controls (22 % of 310 misses, 0 lost) but adds 529 unmatched boxes. At 0.25: +46 and +290. Tab items stay undetected. |
| B405-121 | contradicted | The PyTorch weights detect 247 controls at 640 px, 287 at 960 px, and 215 at 1280 px. |
| B405-130 | contradicted | Against 640 px, 960 px gains 74 and loses 34; 1280 px gains 63 and loses 95. List rows gain; collection items become imageView or sheet. |

### Decisions

- Keep confidence 0.50 for tvOS. A lower threshold adds about 8 unmatched boxes for each recovered control. These boxes are unreviewed, so they are not proven false positives.
- Keep 640 px. Larger input helps list rows but breaks collection items. Class-specific tiling for rows is a possible later test, not a current priority.
- Tab items are never detected at any confidence or size. They need training coverage or a taxonomy decision, not inference changes.
- The PyTorch path differs from Core ML production. Production-faithful evaluation needs the production engine.


## T45 — Native button, row, and tab capture recipe, 2026-10-15

research-host-NUIAK adds the recipe version `native-controls-t45-v1`. The T03 template stays the same; no new template ID.
The old version `native-hcf402-v1` and its `validate` function are unchanged.

### What the new version admits

`native_coverage402.validate_controls` admits these cases:

- 1 family for each case: `button`, `row`, or `tab`. Other components may only be `text` decorations.
- Every focusable control uses `native_button` focus.
- Composition version 3 and the `grid_matrix` archetype. The local Fixture rules (`fixture_composition.resolve`) check the composition offline.
- At most 3 cases, 4 targets for each case, and 24 frames. Profiles are Standard and HCF, with 1 repeat and 100 MB.
- Every case has the role `development`. The plan has `study-pending` and `trainingEligible: false`.
- 1 group holds 1 family and 1 role. A case cannot carry requested bounds or labels.

Requested design sizes are not annotations. The capture keeps the measured rendered body.
If a planned control has no measured body, for example `non_affine_transform`, settling fails and the capture fails.
`measured_bodies` summarizes the measured aspect by family. An unavailable body raises `unmeasured_body:<reason>`.

The capture dispatch in `hcf_study371`, `hcf_capture362`, and `generation352` now accepts the new version.
`backlog_pipeline` plans can carry a `capture` contract in `shared` or in an arm.
Tests: `scripts/test_native_controls_t45.py` (11 tests). The suites for the 3 dispatch files and the pipeline still pass.

### Local qualification

The target was clear: no recovery marker, no running queue job, and TTR readiness reported clear ownership.
The captures use the qualified native lifecycle with the shared host lock. Each capture restores the Standard setting.

| Attempt | Families | Frames | Time | Size | Result |
| --- | --- | --- | --- | --- | --- |
| qualify-r1 | button, row, tab | 4 of 24 | 42 s | 10.3 MB | Failed. The Fixture returned HTTP 400 for the row recipe. Cleanup passed. |
| qualify-r2 | row, tab | 16 of 16 | 107 s | 36.4 MB | Complete. Cleanup passed. |

The r1 cause: the Fixture accepts a composition only with the `grid_matrix` archetype. The row recipe used `settings_list`.
The validator now rejects other archetypes (`controls_archetype`). The cause is in `reports/work/T45/qualify-r1/cause.json`.

Measured bodies (`native_body_presentation_layer`, 3840 × 2160 px):

- Button: 547.6 × 156.4 px, aspect 3.50. Standard profile only (4 frames). The HCF button frames are not captured yet.
- Row: aspect 9.18 in 8 frames, both profiles.
- Tab: aspect 3.85 in 8 frames, both profiles.

The body size did not change between the Standard and HCF frames, or between focused targets.
These are development frames. They are not an audit and not training data.

### Plan for B405-042

B405-042 now has a T03 plan with 4 arms:

- `artwork`: the control. It reuses the completed job `hcf402-focused-r3`.
- `button`, `row`, and `tab`: new groups `t45-<family>-group-b042`, 8 frames each.

`expand B405-042` writes `Research/Experiments/batches/B405-042.json`. All 3 jobs are definition-valid. They are not registered.
After capture, T36 measures the Standard and HCF pixel differences for each family. The artwork T36 report is `hcf402-profile-pixels`.

### Approval needed

A person must approve 3 local tvOS Simulator captures: `b405-042-button`, `b405-042-row`, and `b405-042-tab`.
Each job captures 8 development frames within 800 s and 100 MB. The estimate is 330 s in total.
Then run `expand B405-042 --register --approve-listed`.
The recipe binding names Fixture PID 37401. If the Fixture restarts, freeze new recipe files first.

### Records that stay blocked

T45 unblocks only B405-042 directly. B405-104 (T37) waits for the B405-042 result.
B405-043 to 049, 109, and 110 need other inputs (owned artwork, action receipts, keyboard, route graphs) or wait for B405-041.

## T47 — Temporal pair evaluation (ENG405-05), 2026-10-15

### Template

T47 is `scripts/temporal_pairs414.py`. It scores ordered before/after focus pairs with 1 pinned transition model.

- Inputs: `pairs` (a `temporal-pairs-v1` manifest), `model` (pinned weights), and optional `prior` (pinned predictions).
- Parameters: `direction` (`forward` or `reverse`) and `thresholds`. The thresholds must be 0.15 stable and 0.85 changed.
- Each pair names its kind (`movement`, `content-only`, or `no-op`), both endpoint focus identities, and 1 action receipt.
- The adapter refuses a pair without both endpoint identities, a pair whose label conflicts with its endpoints, and a content-only pair with identical images.
- Scoring reuses the PROGRAM384-D1 path (`report_additive341.score_rows`) and the `reserve346.count` outcome rules.
- A `reverse` arm swaps images and endpoints. Its prior is the same model in forward order, inside the same job. An external prior is refused.
- Outputs: `benchmark_summary.json` (gains, lostPriorSuccesses, falseChanges, slices per kind, role, group, layout, action source, and domain, legacy FOCUS366 counts, decisions, `modelAccepted: false`), `cases.json` (1 row per pair), and `predictions.json`.
- Registration: 1 `CONTRACTS` line `T47` and a parameter check in `hcf_templates395.build` and `backlog_pipeline.validate_plan`.

The manifest builder (`temporal_pairs414.py manifest d1|graph364|graph364-authored`) writes pinned manifests under `reports/work/TEMPORAL414/`:

| Manifest | Pairs | Movement | Content-only | No-op | Roles |
| --- | ---: | ---: | ---: | ---: | --- |
| `pairs-d1.json` (PROGRAM384-D1 membership) | 1,408 | 472 | 656 | 280 | 1,392 train, 16 development |
| `pairs-graph364-authored.json` (FOCUS366/373) | 392 | 112 | 168 | 112 | development |
| `pairs-graph364.json` (FOCUS366/373 plus FOCUS-343 native) | 408 | 120 | 168 | 120 | development |

Authored endpoints come from the render annotations. The builder checks that each annotation names the same image hash.
Native endpoints come from the FOCUS-343 scene brackets. The before and after brackets must agree, and the capture receipt must name the same target.

### Qualification

An isolated queue under `.build/debug-output/t47-qualify` runs 5 jobs on the full manifests. All counts equal the recorded results.

| Job | Model | Prior | Correct | False changes | Abstentions | Gained | Lost | Recorded result |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| D1 baseline, train role | FOCUS-329 | none | 1,005 | 97 | 282 | — | — | 1,005 baseline successes |
| D1 control, train role | D1 seed 42 | D1 baseline | 1,136 | 82 | 172 | 131 | 0 | 1,136 correct, 0 lost |
| D1 control, development role | D1 seed 42 | D1 baseline | 8 of 16 | 0 | 0 | 0 | 0 | 8 correct, 0 lost |
| FOCUS366 baseline | FOCUS-329 | none | 308 | 33 | 47 | — | — | 308, 33, 47 |
| FOCUS366 control | focus366-control-train | FOCUS366 baseline | 301 | 42 | 45 | 2 | 9 | 301, 42, 45, +2, −9 |
| FOCUS366 notification | focus366-notification-train | FOCUS366 baseline | 342 | 18 | 28 | 34 | 0 | 342, 18, 28, +34, 0 |

The ExperimentProgram384 table lists 22 and 6 lost successes for FOCUS373. Those counts use a different reference. The FOCUS366 comparison files show 9 and 0.
Both D1 models miss all 8 native FOCUS-343 movements. Native movement recall is 0 of 8 on this scene.
Run times: 63–71 s for 1,408 pairs and 15–17 s for 392 pairs.

`scripts/test_temporal_pairs414.py` has 7 tests. The queue test checks each D1 subset probability against the recorded seed-42 and baseline values to 5 decimal places.
It also runs a reverse arm and 2 refusals through the queue (`pair_endpoint_identity_missing`, `reverse_prior_internal`).

### Per-case rows for B405-126

`cases.json` gives the outcome, prior outcome, gain, and loss of each pair. A T47 run on `pairs-d1.json` with the seed-43 or seed-44 model gives rows that compare directly with the D1 seed variation (45 of 1,392 training views).
B405-126 still needs the transition-training template. T47 does not train.

### Plans

| Record | Plan | Jobs | State |
| --- | --- | --- | --- |
| B405-061 | Forward (control) and reverse order. 408 development pairs, FOCUS-329 model. Rule any-loss. | `b405-061-forward`, `b405-061-reverse` | Complete. Confirmed contradicted. |
| B405-063 | Reuses `b405-061-forward`. No-op slices per action source. Rule manual. | none new | Complete. Confirmed inconclusive. |

`expand --approve-listed` fails with `resource_busy` while the runner holds the queue lock. The jobs registered first. Approval then waits for the same lock.

### Results

| Slice (408 pairs, FOCUS-329) | Pairs | Forward correct | Reverse correct | Lost in reverse | Gained in reverse |
| --- | ---: | ---: | ---: | ---: | ---: |
| Movement | 120 | 106 | 106 | 0 | 0 |
| Content-only | 168 | 90 | 90 | 4 | 4 |
| No-op | 120 | 120 | 120 | 0 | 0 |
| Native FOCUS-343 (all kinds) | 16 | 8 | 8 | 0 | 0 |

**B405-061 (confirmed: contradicted).** Reverse order loses 0 of 106 forward movement successes.
All 4 losses and 4 gains are content-only pairs, so the net change is 0. The any-loss rule proposed "supported" only from these content-only flips.
The plan decision asks about losses on movement pairs. Therefore the confirmed outcome is contradicted.
The model misses all 8 native movements in both directions. This is a native recall failure, not a direction failure.
Next action: test new native families in B405-112 when B405-044 supplies them.

**B405-063 (confirmed: inconclusive).** All 120 no-op pairs are correct, with 0 abstentions and 0 false changes.
Content-only pairs show 45 abstentions and 33 false changes.
Every no-op pair has identical before and after pixels. The test therefore cannot measure abstention after a real no-op action.
B405-063 now requires native no-op receipts with capture noise or animation from B405-044 (research-host-TTR).

### Records without inputs

| Record | Missing input | Producer | Owner |
| --- | --- | --- | --- |
| B405-062 | Native content-only changes with unchanged focus, and matched native movements | B405-043 T03 artwork exchange | research-host-TTR |
| B405-064 | Native scroll pairs with matched offsets | B405-044 T03 capture with a scroll recipe | research-host-TTR |
| B405-065 | Timestamped native sequences with an animated background | TTR Fixture animated-background recipe | research-host-TTR |
| B405-066 | Native pairs between identical-artwork controls | B405-043 owned-artwork recipe | research-host-TTR |
| B405-067 | Guarded Settings rule scorer as a T47 arm, and reviewed Settings frames | T47 variant | research-host-NUIAK |
| B405-068 | Swift tracking runner and arithmetic-parity evidence | New adapter | research-host-NUIAK |
| B405-069 | Native timestamps and a sequential capture interface | TTR sequential capture (B405-044) | research-host-TTR |
| B405-070 | Confirmed B405-061, B405-062, and B405-063 results | Decision | research-host-NUIAK |
| B405-111 | Native modal sequences with visibility labels | B405-048 T03 overlay capture | research-host-TTR |
| B405-112 | Ordered native pairs from new families | B405-044 T03 capture | research-host-TTR |

FOCUS372 captures are single focus states without action pairs. They do not supply ordered pairs.

## T46 — iOS native capture (ENG405-03), 2026-10-15

Work by research-host-NUIAK. Template T46 renders a pinned recipe with the pinned GeneratorRunner build on the generator Simulator.
It writes grouped, labeled iOS frames and a per-class support table.

### Contract

- Adapter: `scripts/ios_native_capture_t46.py`. Tests: `scripts/test_ios_native_capture_t46.py`.
- Inputs:
  - `recipe` (`ios-native-capture-recipe-v1`): families, seeds, devices, Dynamic Type sizes, appearances, group rule, role per family, `trainingEligible`, `supportedClasses`, `maxFrames`.
  - `generator` (`ios-generator-build-v1`): the build receipt that `ios_native_capture_t46.py build` writes. It pins the `.xctestrun` file and every file of `GeneratorRunner.app`.
- Parameters: `target` (only `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`) and `timeoutSeconds` (60 to 700).
- Authority: diagnostic, 800 s and 100 MB. The run uses the project's own generator app. It does not change status bar, settings, or TTR state.
- Outputs: `frames/` (PNG and schema 1.0 sidecar), `manifest.json`, `benchmark_summary.json`, `xcodebuild.log`, `artifact-receipt.json`.

### Rules

- Roles are per family. All seeds and variants of 1 family stay in 1 role. Groups are `family-seed` or `family`.
- A frame is training-eligible only if the recipe sets `trainingEligible` and the family role is `training`. Final-audit roles are not accepted.
- A class outside the frozen taxonomy, or outside the recipe `supportedClasses`, fails the job. The message names the family and the class.
- `supportedClasses: "taxonomy"` means all 41 frozen classes. This includes `unknown`, which `ChromeCoverage` draws on purpose as `unknown_0`.
- Each sidecar must pass the frozen schema, the image hash, the recipe binding, BP-11 pixel scale, and BP-10 Vision coordinates.
- Excluded, zero-area, and known-issue elements are rejected labels. They do not count as support.
- A light/dark pair must render at least 0.05 lower mean luma for dark. Otherwise T46 rejects both frames. Identical pixels are rejected as duplicates.
- The support table covers all 41 frozen classes: objects, frames, groups, families, objects by role, rejected labels, and status.

### Swift changes

- `ScreenshotCapture.rendersPresentationTraits` is a task-local value with default `false`. Only T46 sets it.
  When it is `true`, the capture applies the configured appearance and content size category to the hosting controller. The default output does not change.
- `GenerateDatasetTests.testRecipeCapture46` is opt-in. It skips unless `NUIAK_T46_RECIPE` and `NUIAK_T46_OUTPUT` are set.
- Build: `xcodebuild build-for-testing` passed in 17.8 s. `swift build` passed. The changed Swift files are in the Xcode targets, not in SPM targets.
- `swift test` is not verified. 2 runs stalled in the parallel Swift Testing suite: about 20 Core ML and Vision tests started and did not finish (0 % CPU for 3 h 52 min in run 1, no log output for 8 min in run 2). 90 tests passed and 0 failed before the stall. T46 changes no SPM target, so the stall is independent of T46. The cause is not diagnosed.

### Qualification

The live queue test ran twice on the Simulator after the T45 tvOS capture went idle. Each run took 8 s to 16 s.
- Recipe 1 (`SettingsList`, `UIKitControls`; seed 3; large and accessibilityMedium; light and dark): 8 frames, 2.66 MB.
- Recipe 2 (`InteractiveControlPalette`; seed 5): 2 frames. It uses the same harness with no new code.
- `UIKitControls` dark renders: mean luma 0.95 for light and 0.02 for dark. Its 4 frames are eligible.
- `SettingsList` dark is pixel-identical to light. `InteractiveControlPalette` differs by 0.0002 mean luma. T46 rejects these frames.
- Dynamic Type changes the `SettingsList` label geometry between large and accessibilityMedium.
- Offline tests: 8 pass. They include 2 queue failures before any Simulator work (`build_app_changed`, `recipe_families`). Related pipeline suites: 31 pass.

### Finding — appearance labels

Most SwiftUI templates choose their color scheme from the seed and apply `.colorScheme(...)` inside the view.
The trait override cannot change these templates. Their sidecar `colorScheme` can disagree with the pixels.
This also applies to the historical iOS corpus, because `ScreenshotCapture` treated both values as metadata only. See BP-117.
T46 marks each frame `appearanceVerified` as `paired-rendered`, `not-rendered`, or `unverified`.

### Plans and jobs

| Record | Arms | Recipe | Frames per arm | Approval |
| --- | --- | --- | --- | --- |
| B405-031 class coverage | 3 family thirds (a2, b, c) | seed 7, large, light | 16 | agent:assistant-t46-ios-capture |
| B405-034 Dynamic Type | 3 family thirds (a2, b, c) | seed 11, large and accessibilityLarge, light | 32 | agent:assistant-t46-ios-capture |
| B405-035 light and dark | 3 family thirds (a2, b, c) | seed 9, large, light and dark | 32 | agent:assistant-t46-ios-capture |

All arms use the development role and are not training-eligible. The rule is `manual`.
Recipes are in `Research/Experiments/t46-recipes/`. The build receipt is `.build/ios-capture-t46/build-receipt-r1.json`.
B405-034 and B405-035 list B405-032 as a dependency. These arms measure rendering only. They do not admit data, so they do not wait for the bounds check.
The families include the frozen test and validation families. Seed 7, 9, and 11 renders stay development diagnostics. Do not admit them to training.

### Remaining T03-ios blockers (all research-host-NUIAK)

| Record | Missing input |
| --- | --- |
| B405-032 | Rendered-body measurement: compare each exported rectangle with the visible native body in pixels |
| B405-033 | Rights-cleared long and localized strings and a string-injection recipe field |
| B405-036 | Overlay occlusion measurement under sheets and dialogs |
| B405-037 | Scroll-offset recipe field and visible-body measurement |
| B405-038 | State recipe fields and native state values in sidecars |
| B405-039 | Decision: frozen withheld-family list and roles |
| B405-040 | Decision: independent real labeled development set (unchanged) |

The largest single adapter is the rendered-body check for B405-032. B405-033 to B405-039 depend on B405-032.
The Tasks.md rows of these records still show `Needs data`, because `render-tasks` keeps the recorded state of unplanned records.

### Attempt 1 failure and repair

The 3 `families-a` jobs failed with `unsupported_class:ChromeCoverage:unknown`. The other 6 arms completed.
Cause: the first adapter removed `unknown` from `taxonomy`. `unknown` is frozen class 39, and `ChromeCoverage` labels it explicitly. The adapter did not infer it.
Repair: `taxonomy` now means all 41 classes. Offline tests and the live queue test pass again.
Successors `b405-03x-families-a2` use the same recipes. `Research/Experiments/reconciliation-t46.json` maps each failed job to its successor.
`backlog_pipeline.review` now skips a failed extra job only when a reviewed reconciliation maps it to a completed planned successor. It lists such jobs under `superseded`. A test covers both cases.
The failed attempts are preserved. No submitted specification was changed.

### Results (confirmed, 2026-10-15)

Each arm took 7 s to 12 s of wall time and 4 MB to 21 MB of output. All frames use the development role and are not training-eligible.
Support counts generator layout, not reviewed labels.

**B405-031 — class coverage: supported.** 48 families give 48 eligible groups.
- 40 of 41 classes have grouped support. `webContent` has 0 groups. No family draws it.
- 16 classes come from fewer than 3 families. `actionSheet`, `contextMenu`, `popover`, and `unknown` come from 1 family each.
  The others are `alert`, `collectionItem`, `destructiveButton`, `dynamicIsland`, `mapView`, `refreshControl`, `scrollIndicator`, `sheet`, `sidebar`, `statusBar`, `toolbar`, and `tooltip`.
- `pageControl` has 5 groups. The T42 result (Run 013 never matches `pageControl`) is not caused by a missing generator source. Check label geometry and training exposure next.
- Next action: plan producer cases for `webContent` and the 4 single-family classes before the next full iOS retraining.

**B405-034 — Dynamic Type: supported.** Large and accessibilityLarge text on identical structures.
- 37 SwiftUI families change label geometry with no new rejected labels. Keep Dynamic Type variants for them.
- 7 families add rejected labels at accessibilityLarge: InteractiveControlPalette, KitchenSink, LinkRichText, MediaCardGrid, RichContentFeed, SegmentedFilter, and SettingsToggleDense. Review their layout first.
- The 4 UIKit families do not change geometry. Their controllers use fixed fonts. Do not add Dynamic Type variants for them.

**B405-035 — light and dark: supported for UIKit only.**
- UIKitControls, UIKitForm, UIKitList, and UIKitToggleForm render dark pairs. Use only these 4 families for appearance support, with 1 group per pair.
- All 44 SwiftUI families render the same scheme in both frames, because each template applies its own seeded `.colorScheme(...)` (BP-117).
- Next action: make the SwiftUI templates take the scheme from the run configuration when T46 opts in. Then repeat B405-035 on the changed build. This is NUIAK engineering work.

## Results — native button, row, and tab HCF effect (T45 captures, T36), 2026-10-15

The user approves the 3 B405-042 captures. Each takes 101–112 s and records 8 frames with measured bodies.
The HCF setting is requested, applied, and verified in every capture, as in the artwork capture.

| Family | Pairs | Changed pixels per pair (median) | Byte-identical pairs |
| --- | ---: | ---: | ---: |
| Artwork (control, hcf402-focused-r3) | 8 | 98,916 | 0 |
| Button | 4 | 0 | 4 |
| Row | 4 | 0 | 3 |
| Tab | 4 | 0 | 4 |

B405-042 and B405-134 are confirmed contradicted. In this Fixture build on tvOS 26.5, HCF changes focused artwork only.
Native buttons, rows, and tabs render the same pixels with and without HCF.
TTR message 754 agrees: its ring finder finds no supported HCF ring in Settings.

Decisions:

- Keep HCF effect labels for artwork only. Do not label native buttons, rows, or tabs as HCF-positive.
- Do not plan B405-104 (mapping across control families) on these families. No HCF effect exists to map.
- Inspect the 1 row pair that changes 5.5 M pixels. It is probably a different screen state, not an HCF effect.
- Ask capture-host-TTR whether real tvOS HCF changes native button focus. The Fixture may not use the system focus effect for these components.


### Wave 2 — rendered-body measurement (2026-10-15)

T46 now writes `bodies.json` and a `bodyChecks` block in `benchmark_summary.json`. It compares each admitted exported rectangle with the visible body in pixels.
The gate was fixed in code before any result was read:
- Window: the box plus 3 pt. Ring: the window outside the box. Background: the median ring color.
- If fewer than 85 % of ring pixels match the background (channel difference 12 or less), the label is `ambiguous`.
- Body: the bounding box of window pixels that differ from the background by more than 24.
- Status: `tight` (every edge within 1 pt + 1 px), `inset`, `outside` (the body passes the box by more than the tolerance), or `empty`.
- A family passes with 0 `outside` labels and at most 10 % `empty` labels among measurable labels.

Tests: 2 new unit tests cover each status and the family gate. 10 offline tests pass. The live queue test passes.

**B405-032 — generated bounds: supported.** 48 families, seed 13, iPhone 17 Pro (3x) and iPhone SE (2x), 6 arms of 16 frames, 6 s to 7 s each.
- 34 families pass on both layouts.
- 14 families fail: AccountProfileForm, ChromeCoverage, ContextMenu, FormValidation, KitchenSink, MapOverlays, MultiSectionForm, Popover, RTLMirror, RichContentFeed, SettingsDisclosure, SettingsList, SettingsToggleDense, and iPadSidebar.
- MapOverlays has only ambiguous labels: a map background is not uniform, so this check cannot measure it.
- `toggle`: 46 of 74 measurable labels are `outside`. The exported box is 61 pt wide; the drawn switch is 63 pt and passes the box by 2 pt on the right (6 px at 3x). The offset is the same in every family. Repair the toggle frame before the next toggle training data.
- `listRow`: 15 outside, mostly on the right. `secondaryButton`: 5 outside. `label`: 10 outside, of which ContextMenu shows 3 pt on both sides.
  Limitation: the menu panel fill next to the text can look like body when the ring uniformity is near 0.85. Review these classes by eye before a repair.
- `pageControl`: 8 tight and 4 inset, 0 outside. Its boxes are not too small, so box size does not explain the Run 013 `pageControl` misses.
- Next action: admit only the 34 passing families to bounds-qualified generation. Repair the toggle frame, then repeat the arms for the 7 failing families that contain toggles.

**Other records:** the measurement does not supply their missing inputs. Each blocker in the catalog names the T46 extension or decision it needs:
- B405-033: rights-cleared strings and a string-injection recipe field.
- B405-036: a matched before/after overlay toggle.
- B405-037: a scroll-offset recipe field.
- B405-038: state recipe fields and sidecar state.
- B405-039: a frozen withheld-family list (decision).
- B405-040: depends on B405-039 and B405-011 (decision).

**Open engineering item ENG405-13 (Tasks.md):** `swift test` stalls in the parallel Swift Testing suite. 90 tests pass and 0 fail. These tests start and never finish:
- A forbidden anchor present -> unverified even if all required anchors matched
- A localized visual change is never reported as identical (changed-focus true-negative)
- A missing required anchor -> unverified, not a best guess
- A small localized change yields exactly one small ROI, classified local
- All required anchors present, no forbidden anchors -> verified
- Cache does not false-hit on a localized change under a tight threshold
- Cache reports unchanged on first sight only after seeding, then true for a repeat frame
- Cache states are independent
- Detection request confidence threshold filters output
- Detection request finds real elements on the kitchen sink fixture
- Detection request populates stage timings when recordTimings is enabled
- Detection request with OCR disabled leaves visible text nil
- Detection request with OCR fuses visible text on kitchen sink fixture
- Detector recognizer performs detection on valid PNG data
- Distance is symmetric
- Flags undersized interactive control
- Focus classifier flag controls which resolution path runs without crashing
- FocusRing crop is always 256 by 256
- FocusRingClassifier returns a unit-interval probability on a tvOS home crop
- Identical frames classify as no change with no regions
- Invalidate forces the next call to report changed
- Matching is case-insensitive substring containment
- ModalityHealth reports all requested modalities as available on success
- ModalityHealth reports ocr as empty on a legitimately text-free image
- ModalityHealth reports ocr as notRequested when text recognition is disabled
- NativeUIDetectionSession pre-warms models, eliminates load latency on subsequent calls, and manages cache
- NativeUIElementObservation is Sendable and Codable
- NativeUIRect round-trips through CGRect
- No OCR text found at all -> ambiguous, not unverified
- No required anchors supplied -> ambiguous, not a silent pass
- Optional anchors are reported but never affect status
- Package version is non-empty
- Permissive modality policy preserves detections and records honest OCR failure
- Pixel ROI to Vision-normalized conversion matches the package's existing y-flip convention
- ROI-scoped OCR still finds an anchor known to be inside the region
- Real OCR on the kitchen-sink fixture verifies against its own discovered text
- Result never exposes image data — geometry and classification only
- Same image compared to itself has near-zero distance
- Strict modality policy throws/fails request when OCR fails
- Two entirely different screens classify as fullFrame
- Two entirely different screens score further apart than the same screen
- tvOS auto-routing performs detection and resolves active focus
- tvOS expanded collection item takes focus precedence over bottom-edge list row
- tvOS peer-relative geometry heuristic rewards expanded collection items
Trivial tests in this list (for example `Package version is non-empty`) are probably waiting behind the blocked workers. A serial run must find the test that blocks.

## Results — remaining detector-case records (T42 extensions, T50), 2026-10-15

Owner: research-host-NUIAK. The contract details are in [DetectorCaseMatch411.md](DetectorCaseMatch411.md).
The 11 jobs were approved as `agent:assistant-casematch411`. All completed. Each control arm reproduces its stored result exactly.

New options:

- T42 slices `state` and `edge`.
- T42 matching `class-aware-suppressed`.
- A `fit` field for each missed label: `larger`, `smaller`, `offset`, or none.
- T50 adds VNDetectRectanglesRequest boxes from the compiled `scripts/vision_annotation_probe.swift`.
  T50 was the next free number, because Tasks.md reserves T48 and T49.

| Record | Outcome | Finding |
| --- | --- | --- |
| B405-013 | supported | 0 of 600 page controls at 0.25; 22 at any stored confidence. Of 578 misses, 328 sit under a larger box, 239 have no box. Repair group-bound geometry first. |
| B405-018 | contradicted | 7 spatial groups recover 550 of 6,377 Run 013 misses (8.6 %), only within button, selection, and text-input groups. Missed and mislocalized labels do not change. |
| B405-022 | inconclusive | Focused 21 of 46 versus unfocused 325 of 537 located (class-agnostic). Of 25 focused misses, 11 have a smaller box, which is not a majority. |
| B405-024 | supported | Cross-class suppression at IoU 0.5 removes 29 unmatched boxes and loses 12 located controls. Keep class-wise suppression. |
| B405-025 | contradicted | Rectangles locate 68 of 237 missed controls (29 %, 0 lost) but add 1,106 boxes, 808 unmatched. |
| B405-028 | contradicted | A larger box covers 45 of 210 collection-item and row misses. A smaller box lies inside 79. Container confusion does not dominate. |
| B405-029 | supported | 15 of 38 edge controls located versus 331 of 545 interior (39 % versus 61 %). The edge rule is a geometric proxy, not clipping review. |

### Exact requirements for the records without jobs

| Record | Kind | Owner | Missing input |
| --- | --- | --- | --- |
| B405-019 | adapter | research-host-NUIAK | OCR role association (template id `ocr-role-association`). Run the Vision probe OCR on the images with the 778 B405-012 wrong-class labels. Freeze 1 text rule for each confused class pair before scoring. |
| B405-020 | adapter, decision | research-host-NUIAK | ENG405-06 detector training and restore variant. Maintainer review of button-role labels (B405-015). Admitted T46 toggle groups 32 to 128 px high at 0.5 to 0.9 frame width (B405-016). |
| B405-022 | data | research-host-TTR | Paired focused and unfocused frames with measured presentation-layer bounds. |
| B405-027 | data | research-host-NUIAK | A T45 tab case with a selected tab that differs from the focused tab, plus capture approval. The detector locates 0 of 24 tab items as tabs (B405-108). |
| B405-030 | adapter, data | research-host-NUIAK | ENG405-06. Admitted tvOS groups for collection items, rows, and tabs. B405-041 admits 0, and its quotas wait for a maintainer freeze. |
| B405-106 | data | research-host-NUIAK | Steppers from at least 3 template families with value and disabled states. The 200 withheld steppers come from 1 family (MultiSectionForm). Run 013 detects all 200 (AP50 1.0). |

### Decisions

- **Page controls:** Group-bound boxes, not missing detail, limit page controls at the stored confidences. Review the page-control label extent against the predicted group boxes before region-detail work.
- **Coarse classes and suppression:** Do not pursue coarse-class training or cross-class suppression for recall. Neither addresses the missed and mislocalized labels.
- **Rectangles:** Vision rectangles find real missed tvOS controls. Their unmatched cost is too high for direct proposals. A filter for rectangles needs its own frozen rule.
- **Box size:** tvOS misses often sit around boxes smaller than the reviewed body (B405-028, B405-029). Compare reviewed visible bounds with detector body bounds before training.
- **Approval lock:** `expand --approve-listed` fails with `resource_busy` while the runner holds `.build/research-queue.lock`. Registration still happens, but a later `expand` skips existing jobs. This session approved the jobs through `research_approval.approve` after a blocking wait on the same lock.

## T48 — Representation comparison (B405-075–080, B405-114), 2026-10-15

Owner: research-host-NUIAK. Estimate: 90–120 min. Actual: about 100 min, plus a usage-limit pause.

### Template

`scripts/representation_t48.py` (T48) scores the fixed HCF crop classifier on the T40 retained bundle under 1 representation change.
Pixels, labels, source boxes, model `hcf375c-70-crop-train`, and threshold 0.85 stay fixed. Inputs: `bundle`, `model`, `tool`.
Parameters: `source` (T41 sources) and `representation`:

- `context` with `expansion`: the tool keeps its 0.16 expansion. The adapter scales the box about its center, so the tool crop rectangle equals the requested expansion.
- `aspect-fit`: the tool `experimentalAspectFit` crop. It letterboxes the expanded rectangle into 256x256. The padding fraction comes from geometry.
- `none`: the production crop.

Both changes use `FocusRingClassifier.makeCrop` through FocusRingTool (BP-46). Selection always matches the unchanged source box.
Each job also scores the unchanged crops. They must reproduce the cached T37 scores within 1e-4, or the job fails with `cached_score_mismatch`.
The output `benchmark_summary.json` has `gains`, `lostPriorSuccesses`, `slices` by profile and orientation, `decisions`, `geometry`, and `modelAccepted: false`.
T48 imports `producer` and the constants from T41. It does not change `box_intervention410.py`, because queued T41 jobs pin that source.

Tests: `scripts/test_representation_t48.py` has 6 tests: parameters, crop geometry, matching on the source box, compiler and plan rejection, and an isolated queue run on the tall-control pair with a negative role job. The T41 suite still passes (11 tests in total).

### Results (confirmed: supported for both)

All 5 jobs take about 63 s each. Every unchanged crop reproduces the cached score exactly (deviation 0.0).
The control is `b405-002-known-none`: 71 prior successes on known boxes.

| Arm | Lost prior successes | Gains | Mean target score change |
| --- | ---: | ---: | --- |
| Known box, expansion 0.20 | 57 (24 HCF, 33 Standard) | 0 | HCF −0.36, Standard −0.58 |
| Known box, expansion 0.24 | 71 (all) | 0 | HCF −0.84, Standard −1.00 |
| Mapped proposals, expansion 0.24 | 4 of 5 | 0 | HCF −0.43 |
| Known box, aspect-fit (mean padding 0.45) | 64 (32 HCF, 32 Standard) | 0 | HCF −0.50, Standard −0.87 |
| Mapped proposals, aspect-fit (mean padding 0.33) | 5 (4 wide, 1 tall) | 2 tall | HCF −0.36 |

The aspect-fit mapped gains are the unresolved tall controls `hcf402-tall-controls-hcf-item-0-0` and `item-2-0`.

### Decisions

- **B405-075:** Keep the 0.16 crop margin for this model. Larger context removes most correct selections, as box growth did in B405-074.
- **B405-114:** Keep the 256x256 stretch for this model. Inference-only letterbox crops are out of distribution for a model trained on stretched crops.
- The 2 tall-control gains suggest that aspect-fit can help tall controls. Test it only as a training comparison with aspect-fit crops in training and evaluation.
- Limitation: B405-075 asks about unresolved Standard cases. The bundle has none: known boxes give 36 of 36 Standard, and proposals exist for 0 Standard frames. The result answers prior-success preservation only.
- Limitation: inspected development groups, not an independent audit. Model acceptance stays false.

### Records without inputs (exact requirements are in the catalog)

| Record | Missing input | Owner |
| --- | --- | --- |
| B405-076 position transfer | Native frames of the same content at new screen positions. Needs a T45 or T03 capture after B405-041. | research-host-NUIAK |
| B405-077 scale-aware input | A trained size feature. The fixed model has no size input, and makeCrop has no scale-preserving crop. B405-070 is not confirmed. | research-host-NUIAK |
| B405-078 screen-level selection | Cached T37 scores already answer this bundle: 0 known-box frames have more than 1 candidate at 0.85 or higher, so a non-forced screen rule changes 0 decisions. Forced top-1 gives 1 gain (tall item-0 at 0.841) and 2 no-focus losses. Needs more no-focus scenes (B405-058) and multi-candidate errors (B405-056). | research-host-NUIAK |
| B405-079 alternative encoder | A licensed resident encoder and maintainer inclusion of encoder work in the tranche scope | Maintainer |
| B405-080 unified detector | Joint training. Needs B405-021 and B405-071 results and frozen role groups. | research-host-NUIAK |

## T47 Settings rule scorer and T49 transition training, 2026-10-15

### T47 `settings-guarded-rule` scorer

T47 has an optional parameter `scorer` (`model` by default). Registered T47 specifications keep their identity.

- `settings-guarded-rule` reads the sealed `SETTINGS-STABILITY-23/retained-final/result.json` (input `rule`). Its `model` pin must be `scripts/settings_focus_stability.py`.
- The rule decision for 1 action comes from `settings_focus_stability.action_outcome` on the guarded controls: switch = changed, unchanged = stable, other states = abstention.
- Pairs outside the same-screen Settings context are abstentions with reason `unsupported_context`.
- Re-execution of the rule is not possible. The sealed semantics need the `focus_recorded_semantics.py` of commit `f1736945`. The scorer therefore uses the sealed result. It does not replace scripts.
- `temporal_pairs414.py manifest settings` writes `pairs-settings.json`: 7 reviewed native Settings actions (2 row moves, 2 page changes, 3 same-row).
  The endpoint identity is the screen title and the text of the 1 reviewed focused row.

### B405-067 — guarded Settings rule versus learned transitions (confirmed: contradicted)

| Action | Kind | FOCUS-329 model | Guarded rule |
| --- | --- | --- | --- |
| 3FF537A2 | row move | correct | abstained |
| CCE16196 | row move | correct | abstained |
| 727E66A5 | page change | correct | outside scope |
| 32D860A2 | page change | correct | outside scope |
| F27D94F4 | same row | false change | incomplete |
| 6677A2C0 | same row | correct | incomplete |
| 6E7FDFAA | same row | correct | abstained |

The model decides 6 of 7 actions correctly. The rule decides 0 actions and loses all 6 model successes.
Per control, the rule stays 33 correct, 0 wrong, and 15 undecided of 48. Its per-control accuracy does not give action decisions on these partial endpoints.
Decision: keep the model. Keep the rule as a diagnostic. Only 2 genuine row moves exist, so this is development evidence.
The first registrations (`b405-067-model`, `b405-067-rule`) pinned the T47 module before a refactor. `reconciliation-t47.json` maps them to the r2 jobs.

### B405-068 — Swift versus Python (answered by reuse)

SETTINGS-SWIFT-SPIKE-25 ([ADR-0018](../ADR-0018-Settings-Swift-Pixel-Parity.md)) already measures this on the same 5 Settings pairs.
The Swift rule matches the Python rule on all 45 matched crops: 33 correct, 0 wrong, 15 undecided of 48, maximum difference 3.21e-13.
Vision tracking gives 2/0/46 and is rejected. No new job is necessary. The catalog records the reuse.

### T49 — FOCUS366 transition training with 1 fixed seed

T49 is `scripts/transition_training415.py`. It wraps `notification366.training` and changes only the seed (42, 43, 44), as `seed_review384` does for D1.

- Inputs: configuration (`Research/ResearchSpecs/T49/<arm>-<seed>-config.json`), initialization (FOCUS-329), membership, the `focus366-admission` dependency, `pairs`, and `prior`.
- Parameters: `arm` (control or notification) and `seed`. The recipe keeps 10 epochs. The compiler accepts 10 epochs for T49 only.
- The configuration copies the frozen FOCUS366 recipe. 2 pins get current hashes: `graph364.py` and `visibility364.py`. They differ from the FOCUS366 copies only in the owner text of `register()`.
- After training, the job scores `final.pt` with T47 on `pairs-graph364.json` against the FOCUS-329 predictions of `b405-061-forward`.
- Tests: `scripts/test_transition_training415.py` (3 checks, plus an 8-minute qualification with `T49_TRAIN=1`).

Qualification (isolated queue, seed-42 notification): `final.pt` is bit-identical to `focus366-notification-train/last.pt` (SHA-256 `a6f52027…`).
The 392 authored pairs give 342 correct, 18 false changes, 28 abstentions, 34 gained, and 0 lost. These equal FOCUS366.
The isolated job ends with `approval_or_code_changed_during_run`: other sessions edited `hcf_templates395.py` and `backlog_pipeline.py` during the 694 s run.
The approval covers every script, so any script edit during a training run fails that run. Edits to scripts must wait while training jobs run.

### B405-126 plan

6 T49 arms: control and notification at seeds 42, 43, and 44 (`b405-126-<arm>-<seed>`). Control: `control-42`. Rule: manual.
ExperimentLog entry `B405-126` precedes registration. Each run: 10 epochs, 1,800 s, 2 GiB. Expected about 430–700 s per run.
Supported only if the gain (notification minus control correct, 392 authored pairs) at every seed is larger than the control seed range, with 0 lost FOCUS-329 successes.

The first 6 jobs failed with `training_history_epoch_mismatch`: `fit.json` (the declared training report) had no `epochs` field.
Training itself was correct: control-42 reproduced FOCUS366 exactly. T49 `finish()` now writes `epochs`, and a regression test runs the trust check on the retained failed attempt.
The 3 unstarted notification approvals were revoked. `reconciliation-t47.json` maps all 6 old jobs to the `b405-126-r2` successors.

### B405-126 — notification correction across seeds (confirmed: inconclusive)

| Seed | Control correct | Notification correct | Gain | Notification false changes | Notification lost |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 301 | 342 | +41 | 18 | 0 |
| 43 | 308 | 347 | +39 | 12 | 1 |
| 44 | 305 | 344 | +39 | 16 | 0 |

- Seed-42 weights of both arms are bit-identical to FOCUS366.
- The control seed range is 7 cases (11 control cases vary across seeds; 7 notification cases vary). The gain is about 6 times larger at every seed.
- All gains come from content-only pairs (false changes fall from 33–42 to 12–18).
- Seed 43 loses 1 FOCUS-329 success: `artwork-s0-top_nav_shelf-005` (dim-movement, 0.847 against 0.85).
- All 3 notification seeds lower that case to 0.85–0.88. The controls keep it at 0.96–0.97. Movement correct drops 1–2 at every seed.
- Compared with PROGRAM384-D1 (45 of 1,392 training views vary by seed), this gain is not explained by seed variation. The dimmed-movement margin loss is systematic, not seed noise.

Decision: the frozen rule requires 0 lost successes at every seed, so the correction is not frozen.
Requirements: the maintainer decides whether 1 boundary loss at 1 of 3 seeds blocks the freeze (the same open rule decision as RECONCILE409).
research-host-NUIAK diagnoses the dimmed-movement margin before any further notification correction.

## Template extensions for B405-128, 125, 119 and 127, 2026-10-15

Owner: research-host-NUIAK. Estimate: 3–4 h. Actual: about 3 h, plus a usage-limit pause.
Each extension keeps old specifications unchanged: a new parameter is optional, and its absence gives the old behavior.
Plans are in the catalog. Batches are in `Research/Experiments/batches/`. Nothing is committed.

### B405-128 — 6-bit crop package (T10, then T11) — confirmed: supported

- T10 has a new precision `palette6weights`. `compress_focus_ring_coreml.py --method palette6` uses a uniform 6-bit look-up table with grouped channels of 16 and weight threshold 2048.
- The k-means mode needs scikit-learn, which `.venv-coreml` does not contain. Uniform mode needs no new package. Grouped channels need specification version 9, which the source package has.
- `int8weights` gives the same command as before, without `--method`.
- Tests: `scripts/test_palette6_export128.py`, 4 tests, including a real 6-bit export and a Vision parity pass on the HCF396 membership.
- Jobs: `b405-128-export-palette6` (export authority, 1800 s and 2 GiB) and `b405-128-parity-palette6`. Control: `hcf396-11-parity`.

| Package | Bytes | Parity (8 controls) | Changed decisions | Maximum score error |
| --- | ---: | --- | ---: | ---: |
| INT8 (`hcf396-10-compress`) | 2,612,923 | pass | 0 | 0.00039 |
| 6-bit palette | 2,068,062 | pass | 0 | 0.00064 |

Decision: offer the 6-bit package as an option. It is 20.9% smaller. The check uses 8 controls from 2 frames only. It makes no accuracy, latency, or promotion claim.

### B405-125 — outline-rule wrong selections (T20) — confirmed: supported

- T20 has an optional parameter `taxonomy: outline-failure-v1`. It writes `failure-taxonomy.json` and `benchmark_summary.json`. Without the parameter, T20 writes the same files as before.
- The taxonomy was frozen before the job. It uses labeled boxes only. The first matching mode in this order applies:
  1. `no-focus`: the frame has no focused label.
  2. `neighbor`: IoU of at least 0.5 with a different labeled control.
  3. `clipping`: IoU from 0.1 to less than 0.5 with the focused body.
  4. `decoration`: IoU less than 0.1 with all labeled controls.
  5. `other`: all other cases.
- Tests: `scripts/test_taxonomy125.py`, 5 tests.
- Job: `b405-125-taxonomy-outline-v1`. Control: `hcf397-proposal-failure-audit`.

Result: all 25 wrong selections are `clipping`. All have focus IoU 0.47. All are in family `development-diamond`, across 10 groups.
Decision: the rule outline box has a fixed offset from the body. Repair the outline-to-body bound mapping before tuning the rule.

### B405-119 — proposal-kernel recall on missed native frames (T25, then T34) — confirmed: contradicted

- T25 has an optional parameter `kernelSettings`. `frozen-v2` (default) compiles the received TTR kernel unchanged.
- `relaxed-v1` rewrites a copy of the kernel in the job output with 5 exact replacements:
  - bright-pixel threshold 160 to 128
  - side support 0.65 to 0.50
  - edge contrast and delta 0.12 to 0.08
  - version `outer-ring-v2-relaxed-v1`
- A changed source fails with `kernel_settings_source_changed`. The geometry gates do not change.
- Tests: `scripts/test_kernel_settings119.py`, 5 tests, including a real compile and the HCF398 scoring run.
- Jobs: `b405-119-kernel-relaxed` (T25 producer) and 9 T34 arms `b405-119-relaxed-*` on the same 9 HCF402 captures as the frozen reports.

Results:

- 0 of 28 previously missed focused HCF frames get any proposal.
- The large-control and tall-control frames keep best IoU 0.53–0.68, so no match is lost.
- No-focus frames and Standard frames get 0 proposals.
- On the 264 HCF398 synthetic frames, proposals stay at 52.

Decision: the gate thresholds do not cause the native misses. Measure the native ring pixels before another kernel change. Do not share relaxed-v1 with capture-host-TTR.

### B405-127 — Swift fallback baseline (T51)

The requested entrypoint already exists: `Tools/FocusFallbackTool` calls the unchanged `resolveTVOSFocus` through `FocusFallbackReplay` (commit 0fd550b6).
`FocusFallbackReplayTests` covers it. STANDARD392 used it once, through `scripts/fallback392.py`, on 7 complete frames.
That run gives learned 4 correct and fallback 3 correct, with 1 lost success.

- New template T51 (`scripts/swift_fallback416.py`): inputs are a T40 bundle and the tool binary. Parameters are `arm` (T37 box source) and `elementType` (`primaryButton` or `collectionItem`).
- T51 reads the frames and rendered focused bodies from the capture that each T37 selection job pins. It sends the same boxes to the fallback, without labels or learned scores.
- Outcome names match T37. The match needs IoU of at least 0.5 with the rendered body.
- The tool binary is pinned at `.build/b405-127-tool/FocusFallbackTool`. It is a copy of `swift build --product FocusFallbackTool` from the current source.
- Tests: `scripts/test_swift_fallback416.py`, 6 tests, including a full known-box run on the 74-frame bundle.
- Jobs: `b405-127-fallback-{known-primary, known-collection, raw-primary, mapped-primary}`.

Results (confirmed: supported). Each job takes 1–5 s. Counts include 1 no-focus frame for each profile.

| Arm | HCF learned correct | HCF fallback | Standard learned correct | Standard fallback | Lost / gained |
| --- | ---: | --- | ---: | --- | --- |
| Known boxes, primaryButton | 35 | 0 correct, 36 abstain | 36 | 0 correct, 36 abstain | 71 / 0 |
| Known boxes, collectionItem | 35 | 1 correct, 32 wrong, 3 abstain | 36 | 36 correct | 34 / 0 |
| Raw ring proposals, primaryButton | 3 | 8 correct | 0 | 0 (no proposals) | 0 / 5 |
| Mapped ring proposals, primaryButton | 5 | 8 correct | 0 | 0 (no proposals) | 0 / 3 |

Decisions:

- On known boxes, the learned selection exceeds the fallback. With `primaryButton`, the fallback abstains on every focused frame. With `collectionItem`, the peer-expansion rule selects the wrong HCF control in 32 of 36 frames.
- On ring proposals, the fallback selects 8 of 36 HCF controls correctly. The learned selection gets 3 (raw) or 5 (mapped), with 0 losses. A learned proposal selector must beat 8 of 36 HCF.
- Limitation: these are development frames that were already inspected. The element type is fixed per arm, and runtime detector proposals are not used.

## Results — geometric jitter in crop preparation (JITTER413), 2026-10-15

Records: B405-131 (crops), B405-118 (training), B405-132 and B405-133 (T41 scoring). All 4 are confirmed. Results are in `Research/Experiments/results/`.

### Method

- T05 prepares crops from the HCF371 admission. The control crops are byte-identical to `hcf371r4-50-crops`.
- The jitter arm keeps all 8,960 original rows. It adds 4 variants of each of the 615 unique training crops (2,460 rows).
- Each variant moves each box edge by a seeded value in [−2, +2] px. `FocusRingClassifier.makeCrop` makes every crop.
- Development rows have no jitter.
- T06 trains each arm with the same initialization: 30 epochs, batch 16, seed 371, fixed-last selection.
- T41 scores each model with the B405-073 and B405-074 arms with the model cache off. The reference is the fresh score of the unchanged box by the same model.

### Losses of previous successes (HCF + Standard, 74 frames)

| Arm | Control model | Jitter model |
| --- | ---: | ---: |
| Unchanged known box: HCF correct / Standard correct | 35/36, 36/36 | 36/36, 36/36 |
| All 16 arms within ±2 px (sum) | 58 | 0 |
| dy +2 px | 16 | 0 |
| Size +4 px total | 29 | 0 |
| dy −4 px | 30 | 0 |
| Height +8 px | 41 | 0 |
| Size +8 px total | 66 | 0 |
| Size +16 px total | 69 | 21 |

The retrained control reproduces the `hcf375c-70-crop-train` fragility. The jitter model removes it up to 4 px shifts and 8 px size changes.

### Decision

- B405-118 is supported. Jitter meets the rule: 0 losses within ±2 px, and the unchanged box keeps at least 35/36 HCF and 36/36 Standard.
- Limitation: the jitter arm has 3,075 unique crops against 615, so it gets about 5 times more updates in 30 epochs.
- Before adoption, run a matched-update control. Also repeat both arms with seeds 372 and 373.
- The evidence is from inspected development groups, 1 seed. Model acceptance stays false. No export or promotion.
- Next: retest proposal and mapping candidates with the jitter model. Tuning stopped because of the 0.5 px tolerance, and this model removes that limit.

### Process notes

- `jitter413-train-jitter` failed with `approval_or_code_changed_during_run`. A parallel session edited `template_adapters395.py` during the run.
- `jitter413-train-jitter-r2` and `jitter413-jit2-t41-*` are identical successors. `reconciliation-jitter413.json` maps them.
- Approval needs the runner dispatch lock. If `expand --register --approve-listed` reports `resource_busy`, the jobs are registered but not approved. Approve them when the runner releases the lock.
