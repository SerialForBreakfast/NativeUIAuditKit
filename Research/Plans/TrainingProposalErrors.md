# Training-only proposal errors

Owner: Maximum-mini-NUIAK. Parent: B405-196. Date: 2026-10-18.

## Question

Does training with measured detector-box errors outperform generic crop jitter without losing previous successes?
Do not use inspected development failures to define training offsets.
Standard remains unchanged. HCF results stay separate.

## Available inputs

The retained `nctrl417-admission` output contains 40 training frames across 5 groups and 21 unique image hashes.
The frame counts are 8 buttons, 8 rows, and 24 tabs.
Matched profiles and repeated images are not independent examples.
Keep the existing training membership and development exclusions.

The admission file has SHA-256 `774509ae745ac251466e392331651ec89dd34bc3a6ccc66f3fff7683b07ca65a`.
Its local path is `reports/work/research-queue/jobs/nctrl417-admission/attempts/1/out/admission.json`.
This inspection establishes available membership, not qualified detector predictions or reliable box correspondences.

## Exact implementation gap

Update, 2026-10-17: T87 and T88 now provide separate training-only preparation and measured proposal errors.
They retain unique image hashes, group identities, missing bodies, ambiguous correspondences, and unmatched proposals.
The sampler uses seed 371 and selects groups before controls. It does not create labels for missing boxes.
The fixed detector settings are confidence 0.5, image size 640, and NMS IoU 0.45.
Matching requires a unique correspondence at IoU 0.1 or above. Ambiguous matches remain excluded.
These are candidate correspondences for review, not independently verified body labels.

The batch contains 3 preparation jobs, 3 inference jobs, and 1 retained checkpoint review.
All 7 receive explicit approval. The background runner owns execution.
The batch is `Research/Experiments/batches/proposal419.json`.
Each job retains the 800 s and 100 MB diagnostic limits.

T89 wraps the resident detector trainer with fixed-last selection and 30 epochs.
It requires complete labels, pinned images, and separate train and calibration groups.
Software checks cover its caller contract. Real training qualification remains pending.
The native admission contains no calibration groups. Do not move inspected development groups into calibration.
T90 reviews retained checkpoint state without repeating training. State presence cannot qualify restoration.
The new T67–T86 prototypes do not remove these requirements.
See [the source review](Template418QualificationReview.md) for exact integration gaps.

T55 and T56 currently require development inputs. They do not support this training-only preparation.
T61 consumes development T57 reports. Those offsets cannot supply the training sampler.
Do not relabel training inputs as development or weaken the existing adapters.

## Reusable preparation steps

1. Add a separate training-only preparation adapter using the retained admission manifest.
2. Verify admission, image hashes, group separation, body bounds, and original taxonomy before inference.
3. Run the pinned general detector on training frames only, using resident inference code and frozen preprocessing.
4. Match proposals to bodies without using focus labels to select a proposal.
5. Record unique matches, ambiguous matches, missed bodies, and extra boxes separately.
6. Derive normalized center and size errors only from unique matches.
7. Save source-frame and group identities with every error. Do not treat duplicate pixels as independent support.
8. Sample those errors with a fixed seed. Compare equal exposure against generic jitter and unchanged crops.

Freeze confidence, matching thresholds, initialization, epochs, and the evaluation membership before registration.
Use training matches to choose the supported sampling range. Do not choose it from evaluation losses.
If correspondence support is insufficient, report the missing family or group and stop the dependent training branch.
Do not invent offsets for missing proposals.

## Qualification before training

- Positive: admitted training images produce pinned predictions and unambiguous correspondences.
- Negative: development or final-audit membership fails before inference.
- Negative: changed image bytes, invalid bounds, and conflicting duplicate labels fail explicitly.
- Negative: ambiguous matches cannot enter the sampler.
- Repetition: identical inputs and seed produce identical sampled offsets and membership.
- Preservation: original images, crops, models, and labels remain unchanged.
- Queue: positive and negative cases use the real queue in isolation before admission.

## Executable graph after qualification

The first background results establish useful correspondence limits:

| Family | Unique training images | Groups | Unique matches | Missed bodies | Ambiguous bodies | Unmatched proposals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Button | 4 | 1 | 9 | 6 | 1 | 4 |
| Row | 5 | 1 | 20 | 0 | 0 | 19 |
| Tab | 12 | 3 | 26 | 1 | 21 | 12 |

These counts measure geometric correspondence, not focus accuracy or generalization.
All 7 diagnostic jobs complete through the detached runner.
Tabs have 21 ambiguous bodies. Do not treat those proposals as clean training offsets.
The row sampler can describe observed errors, but 1 group does not establish broad transfer.
Do not manufacture offsets for the 6 missed button bodies.

The retained detector checkpoint lacks optimizer, scheduler, random state, and a usable epoch.
T90 requires a fresh fixed run. It does not authorize restoration from this inference checkpoint.

Validation: 18 focused Python tests pass, including positive and negative isolated queue checks.
The integrated offline Swift command succeeds. Swift Testing reports 177 tests across 25 suites.
The trainer caller test uses an explicit software fixture, not a trained detector.
Real T89 training qualification remains blocked on complete eligible membership and separate calibration groups.

Training-input preparation → detector inference → correspondence audit → fixed sampling → matched training → retained regression comparisons.

Reuse existing trainers and comparison templates. Add only the missing preparation adapter and sampler support.
Register branches together when their input contracts support deferred outputs.
Keep the 800 s and 100 MB defaults for diagnostic preparation.
Record explicit training budgets before admission. No training run is approved by this document alone.

Advance only if the correction improves deployable selection with zero lost retained successes.
Test known boxes separately from detector boxes. Preserve no-focus abstentions and the TTR artwork failure suite.
If gains fail to repeat or prior successes regress, reject the correction and retain the failed result.

## Independent work admitted now

B405-229 uses T42 for 6 native iOS overlap comparisons at confidence 0.25.
Each arm compares identical predictions with and without fixed cross-class suppression at IoU 0.5.
Reject any lost labeled match. Fewer unmatched boxes alone does not establish better precision.
The existing adapter passes 8 focused tests. All 6 descriptions pass compiler checks and receive explicit approval.
The background runner owns execution. No source adapter changes or native operations occur in this batch.

All 6 jobs now complete. Suppression removes 17 unmatched boxes but loses 41 labeled matches and gains none.
The preservation gate fails. B405-229 is confirmed contradicted; keep Standard unchanged.
Unmatched predictions decrease from 241 to 224. This does not establish improved precision.
