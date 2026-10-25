# Define a batch without a new script

## Bounded detector and restoration settings

T89 accepts optional Boolean `freezeBackbone`. The default remains false.
The true variant supports the resident YOLO11 detector backbone, layers 0 through 10.
It verifies unchanged parameters and BatchNorm buffers before training and after each epoch.
It preserves those tensors in EMA checkpoints. Detection heads remain trainable.
Use matched membership, initialization, settings, and retained comparisons. Frozen checkpoint restoration remains unqualified.

T89 accepts `learningRate` values 0.001 and 0.0001 in its pinned configuration. Omission preserves 0.001.
Set `checkpointRetention` to `last-best-final` to reuse the qualified retention callback. Omission preserves the old snapshot policy.
Keep membership, initialization, epochs, and evaluation groups matched when testing the learning-rate change.
Use the existing detector batch compiler for scoring, terminal decisions, and conditional class diagnostics.

T38 accepts a pinned configuration with `repeat` from 1 through 16. Omission preserves repeat 1.
Qualification compares uninterrupted training and separate-process restoration with exact state and loss-history checks.
A subset proof does not establish full-corpus accuracy or arbitrary checkpoint compatibility.
The restore adapter requires identical settings and verified qualification-row membership in the original checkpoint contract.
Keep complete original membership validation, cumulative continuation budgets, and negative tests. Do not reuse a repeat-1 proof for repeat 9.

## Retained optional observer exports

T10 can reuse a pinned FP16 package with `sourcePackage` and `sourceReport` inputs.
Set `precision` to `fp16` for retained packages. Fresh FP16 and FP32 exports also accept `maximumPackageBytes`.
The default remains 5,000,000 bytes. The optional observer permits the approved 50,000,000-byte limit per model.
The adapter verifies the package hash, checkpoint, precision, and exact byte count before copying and compiling.
The adapter preserves the source report. A new report records the selected limit and source pins.
T11 and consumer regression checks remain required. A passing size check does not activate a model.

## Reusable crop training campaigns

Use `training_campaign452.py` for preparation, T06 fitting, matched T37/T63 scoring, comparison, and bounded follow-ups.
This frontend reuses the existing queue and workers. It does not introduce another trainer.
Standard remains primary. HCF can appear in frozen membership but stays a separate result slice.

Create one `training-campaign-v1` request with these fields:

| Field | Required content |
|---|---|
| `id` | New immutable campaign ID |
| `question`, `controlledComparison` | Observed gap, changed factor, matched control, and practical decision |
| `suite` | Pin to a `training-suite-v1` document |
| `training` | New training definition below, or `{"reuse":"registered-training-id"}` |
| `budget` | Positive `maxJobs`, `maxSeconds`, and `maxOutputBytes` |
| `followups` | Existing supported/contradicted branch descriptions, or an empty list |
| `reuseScores` | Optional complete map from baseline job IDs to completed candidate score jobs |

The suite contains `baselines` and `excludedGroups`.
Each baseline entry contains `job` and `specSHA256`. Freeze the whole retained suite, including consumer regressions.
Excluded groups include development, calibration, and audit ancestry. Their names require reviewed source grouping, not invented independence.

For new training, supply `id`, `preparation`, `configuration`, `initialization`, `membership`, and `experimentLogRunId`.
Use pins for configuration, initialization, and membership.
Preparation is a registered crop producer ID or an existing T05 description with producer dependencies.
Pending preparation uses `crop-membership-plan-v1`; the worker checks produced membership before fitting.
Complete crop documents remain supported for qualified retained inputs.
The compiler preserves 30 epochs, fixed-last selection, 1 attempt, 1800 s, and 2 GiB per new fit.
Use the trainer's balanced mode; frozen rows select the profiles without an implicit HCF filter.
Record the training hypothesis in ExperimentLog before admission. A request does not grant data eligibility.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/training_campaign452.py REQUEST.json --output reports/work/CAMPAIGN
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_admission440.py reports/work/CAMPAIGN/compiled.json --text
```

Register with the existing admission interface. Approve exact IDs in groups of 5–10. The detached runner owns execution.
The compiler copies fixed scoring inputs from every baseline. It changes only the candidate model reference.
`reuseScores` avoids new scoring and must cover the entire suite. Reused training does not run again.
The cumulative reservation charges every new node and reused training, including unselected follow-up branches.
Completed baseline scoring is not charged as new work. Reservation ceilings are not duration estimates.
Retries require explicit successors and a reviewed remaining budget. This frontend does not resume checkpoints or create automatic training branches.

Follow-up branches support existing T37/T63 diagnostic descriptions and `decision-audit`.
The existing terminal report handles inconclusive results without another fit. No branch promotes models or changes Standard.
Missing inputs block only their dependent graph. Missing detector annotations need a producer task, not substituted labels.
This version supports crop training only. Detector trainers require their own qualified campaign contract.
See [RESEARCH451](../../Research/Plans/ResearchGraph451.md) for qualification and remaining work.

## Diagnosis and matched correction campaigns

Use `research_campaign451.py` for retained T57 evidence and compatible crop corrections.
One `research-campaign-v1` request defines the question, membership, pairs, retained failures, and total budget.
Each pair names `condition`, a registered `baseline` job, and a `correction` job or T57 description.
The membership uses `coverage-membership-v1` and maps case identities to original groups.
The compiler creates diagnosis, comparison, and terminal report jobs through the existing queue.
An embedded T57 scorer depends on diagnosis. Existing completed scores are reused without inference.
Inputs must be pinned or resolvable during compilation. Scoring receipts may arrive later.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/research_campaign451.py REQUEST.json --output reports/work/CAMPAIGN
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_admission440.py reports/work/CAMPAIGN/compiled.json --text
```

Use existing admission tools to register and approve exact jobs. Compilation does not start execution.
The `budget` contains positive `maxJobs`, `maxSeconds`, and `maxOutputBytes` limits for newly generated jobs.
The compiler rejects graphs whose summed limits exceed that budget. Each job permits one attempt.
Historical reused work is not charged as new execution. Limits do not represent measured runtime estimates.
Each retained failure contains `reason` and a pinned `evidence` file. Declared retained failures prevent acceptance.
The report never promotes a model. HCF results remain separate from Standard acceptance.
Invalid evidence blocks dependent comparisons; it does not become a successful terminal report.
This version does not select new training, capture, exports, or recursive follow-ups.
See [the contract and qualification](../../Research/Plans/ResearchGraph451.md).

## Final comparisons with future receipts

Use `cascade_validation.compile_request` with `cascade-validation-request-v1`.
Name `id`, a pinned `membership` file, the retained `prior` decision, and up to 8 `pairs`.
Each pair names `condition`, `primary`, and `supplemental` registered T57 jobs.
Producers may still run. The queue verifies their receipts and output hashes before dispatching comparisons.
The compiler creates one comparison per pair and a terminal report. It never starts execution.
Inspect and approve exact IDs through the existing admission tools.
The report preserves case identities and counts original capture groups.
See [VALIDATION448](../../Research/Plans/CascadeValidation448.md).

## Baseline-first model fallback

`cached_model_cascade.compile_request` reuses the agreement graph compiler.
Use `cached-cascade-request-v1` with `id`, `decision`, `review`, and verified `bundles` pins.
The `decision` names the supplemental summary. The `review` names the completed agreement summary.
The compiler creates a measured gate, cached comparisons, and a complete report.
The policy preserves baseline single selections and HCF behavior.
See [CASCADE446](../../Research/Plans/BaselineCascade446.md) for fixed settings and acceptance checks.

## Fixed agreement correction

`proposal_agreement445.compile_request` accepts a `proposal-agreement-request-v1` document.
Name `id`, the prior supplemental `decision` job, and up to 8 verified `bundles` pins.
It compiles a gate, cached comparisons, and a complete terminal decision.
Use the existing admission inspector and exact-job approval after compilation.
The gate requires retained-model gains and new wrong selections before releasing the correction.
The fixed rule uses unique primary score ranking and IoU 0.5. It exposes no threshold sweep.
Standard controls acceptance. HCF retains primary decisions.
See [AGREEMENT445](../../Research/Plans/ProposalAgreement445.md) for evidence and limits.

## Select bounded proposal follow-ups

Use `selection_campaign444.py` after matched proposal campaigns complete.
The request names existing baseline, candidate, and contrast report jobs.
It sets integer limits for the supported Standard metrics. It contains no executable commands.

```json
{
  "version": "bounded-selection-request-v1",
  "id": "new-selection",
  "sources": {
    "baseline": "completed-base-report",
    "candidate": "completed-new-report",
    "contrast": "completed-detector-contrast"
  },
  "rules": {
    "geometry": {"cropLosses": {"min": 1}, "scoreFailures": {"min": 1}},
    "supplemental": {"proposalGains": {"min": 1}, "proposalLosses": {"min": 1}}
  }
}
```

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/selection_campaign444.py REQUEST.json --output reports/work/NEW-SELECTION
```

Inspect the compiled manifest with `workflow_admission440.py` before exact-job approval.
The compiler reuses T61 and the fixed supplemental adapter. It does not run jobs or grant approval.
At most 8 matched conditions enter this graph. Each selected job runs once.
Missing focused observations, no-focus observations, or 3-group support release neither branch.
Standard controls selection. HCF remains a separate optional report slice.
Terminal summaries record the next requirement. They cannot create training, capture, or promotion jobs.
See [SELECTION444](../../Research/Plans/BoundedSelection444.md) for rules and limits.

## One request with bounded follow-ups

Use `workflow_campaign439.py` for an embedded model-decision plan or a reused compiled graph with typed follow-up branches.
Each branch names `supported` or `contradicted` and fixed job descriptions. Inconclusive evidence releases neither branch.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_campaign439.py REQUEST.json --output reports/work/NEW-CAMPAIGN
```

Add `--register` and one `--approve EXACT_ID` per authorized new job.
Before admission, inspect the compiled campaign:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_admission440.py COMPILED.json --text
```

The campaign command also runs this preflight before publishing specifications.
Preflight checks training records, storage, dependencies, failed producers, and completed evidence.
It does not approve jobs or reserve resources. See [WORKFLOW440](../../Research/Plans/WorkflowAdmission440.md).

Do not approve IDs outside the compiled campaign. Changed specifications require successor IDs.
Use `workflow_batch435.py inspect COMPILED.json --text` to review readiness and unselected branches.
See [the contract and limits](../../Research/Plans/WorkflowCampaign439.md).
For T05 preparation followed by T06 training, pin the membership plan before preparation starts.
Put both descriptions in the execution batch. Connect training to the exact preparation specification and `crops.json` output.
The membership plan freezes ordered `id`, `role`, `profile`, `group`, and `label` fields.
The existing bridge compares produced membership with this plan before training starts.
Unknown labels remain blocked. Other templates keep their existing input requirements.

## Admit frozen captures after recovery

Use `recovery_capture_gate437.specification` for new bounded 6-capture recovery branches.
Its `recovery-capture-admission-v2` plan pins the recovery specification, staging file, original marker, and 6 draft recipes.
Preserve an immutable original marker copy before recovery removes the active guard.
The original byte hash remains required. Saved marker values must match after JSON serialization.
Keep submitted GATE433 jobs unchanged. They require explicit successors, not edited specifications.
Each capture entry names its fixed job ID and draft hash. No arbitrary commands enter the plan.
Register and approve the gate through existing queue APIs. Do not run its adapter directly against the live queue.

After verified restoration, the gate derives qualified recipes and uses the existing T03 compiler.
It registers and approves only those named captures. Each capture also depends on successful gate completion.
Missing evidence, changed identities, uncertain restoration, conflicting jobs, and revoked approvals block admission.
Partial admission does not start captures. Identical publication is idempotent; changed specifications require new IDs.
The gate does not capture, remove guards, start a runner, or retry failed work.
Use the isolated tests in `test_recovery_capture_gate437.py` before extending this contract.

This adapter does not provide general deferred binding for every template.
See [the qualification](../../Research/Plans/Review432.md#gate433-implementation-and-qualification).

## Cached supplemental detector comparison

Use `supplemental_proposals427.run` for matched completed T57 reports from different detector weights.
Its pinned `supplemental-proposals-v1` bundle contains `baseline` and `supplemental` entries with report, result, and specification pins.
Stage the bundle as `bundle.json`. The adapter verifies completed receipts and unchanged settings before comparison.
It retains a single baseline selection and consults supplemental scores only after baseline abstention.
This adapter uses the existing queue contract without changing active shared template modules.
It does not merge boxes, run inference, train, or approve a runtime model.
See [the contract](../../Research/Plans/Supplemental427.md) for acceptance rules and negative tests.

## Training-only proposal errors and detector training

T87 accepts `admission` and a `family` parameter: `button`, `row`, or `tab`.
It produces `training-frames.json` from admitted training groups. It rejects group leakage and conflicting duplicate labels.
T88 accepts `frames` and `model`, with `count` and `seed` parameters.
It runs the pinned detector and writes `errors.json`. Missing or ambiguous proposals cannot enter its sampler.
Use T87 output references for T88 dependencies. See `Research/Experiments/batches/proposal419.json`.

T89 accepts `configuration`, `initialization`, and `membership`, with no parameters.
It wraps the resident YOLO trainer: 30 epochs, fixed-last selection, and no early stopping.
Membership uses `detector-training-membership-v1`, complete labels, pinned images, and separate train and calibration groups.
T89 has software caller checks and completed native detector fits.
DETECTOR422, IOS493, and IOS494 provide retained execution evidence.
On October 24, all 36 detector admission, freezing, and campaign tests pass.
These results qualify the tested training path. They do not qualify model accuracy or checkpoint restoration.
Each new fit still requires qualified membership and matched development comparisons.

T89 also accepts `detector-training-membership-v2` with training rows only.
Set `calibrationPolicy` to `none-fixed-last-training-diagnostics` explicitly.
The resident trainer measures its validation metrics on training images in this mode. These metrics are not held-out accuracy.
Keep fixed-last selection and patience 0. Queue separate development comparisons before training.
Do not split related layouts merely to satisfy a calibration requirement.

For retained native controls, `focusable_detector_labels422.py` prepares scoped button, row, and tab labels.
Supply the admitted manifest and T87 frame manifests. Omit calibration groups for the train-only contract.
The command checks recipe-to-scene coverage and preserves development exclusions. It does not qualify exhaustive general UI annotations.
See DETECTOR422 in the [offset review](../../Research/Plans/Offset421AndRefinementReview.md).

T90 accepts `checkpoint`, with no parameters. It reports missing restoration state without starting training.
Use only trusted, locally produced checkpoints. Loading a PyTorch checkpoint can execute serialized code.
Complete checkpoint state still requires independent restoration parity qualification.

T67–T86 remain prototypes pending the checks in `Research/Plans/Template418QualificationReview.md`.
Their software test completion does not establish real model training or scientific validity.

## Preferred path: catalog plans (BACKLOG410)

Catalogs, generated batches, and result records stay local. Versioned native capture recipes remain reusable source inputs.

For a catalog record, write a `plan` block in `Research/Experiments/backlog405.json` instead of a batch file.
Then use these commands:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/backlog_pipeline.py check
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/backlog_pipeline.py expand B405-073 --register --approve-listed --approver agent:SESSION
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/backlog_pipeline.py review B405-073
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/backlog_pipeline.py confirm B405-073 --outcome supported --by agent:SESSION --note "EVIDENCE"
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/backlog_pipeline.py render-tasks
```

`expand` writes the generated batch to `Research/Experiments/batches/` and uses the compiler below.
Each job records the catalog ID as its task, so `review` and the dashboard Backlog panel group results by record.
See the [backlog-grooming skill](../../.agents/skills/backlog-grooming/SKILL.md).

Use `scripts/experiment_batch402.py` with the existing template adapters.
This command does not replace the queue or start execution.

## Small example

```json
{
  "version": "experiment-batch-v1",
  "jobs": [{
    "version": "hcf-template-description-v1",
    "id": "example-selection-comparison",
    "owner": "Maximum-mini-NUIAK",
    "template": "T15",
    "question": "Does the candidate recover errors without losing previous successes?",
    "decision": "Reject losses. Review gains before preparing another training run.",
    "inputs": {
      "baseline": {"file": "reports/work/example/baseline.json"},
      "candidate": {"job": "existing-candidate", "attempt": 1, "output": "comparison.json"}
    },
    "parameters": {"comparison": "matched-selection"},
    "dependencies": []
  }]
}
```

The example needs real named inputs before registration.
Use `job` and `output` without `attempt` for a dependency that has not completed.
The compiler creates dependency hashes and sorts jobs before registration.
Use `file` only for an existing project-relative file. The compiler rejects traversal and symlinks.
For capture, set `capture.plan` to `{"input":"recipe"}` to reuse the verified recipe input.
Other capture authority fields remain explicit.

## Commands

```sh
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_batch402.py inspect BATCH.json
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_batch402.py preview BATCH.json
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_batch402.py register BATCH.json --approve EXACT_JOB_ID
```

Repeat `--approve` only for individually reviewed jobs.
Without that option, registration grants no execution approval.
The detached runner performs its existing readiness and resource checks.
Approval uses its own lock and can proceed during execution. The runner checks approval before dispatch and after execution.
Keep shared execution code changes at a qualified idle boundary. Preserve existing descriptions and submitted specifications.
The inspector reports each branch independently. A missing input does not hide valid independent descriptions.
Registration validates the selected batch before writing jobs.
An interrupted registration can resume with the same immutable descriptions.
Changed inputs or execution sources require a successor ID, not an edited submitted job.

## Select useful work

### Detector boxes to focus selection

T60 accepts a T57 `report` and its completion `receipt`. Set `policy` to `unchanged`, `hcf-ring-first`, or `abstention-fallback`.
It verifies original decisions before evaluating the fixed policy. It records gains, losses, new wrong selections, and unresolved baseline losses.
Use it for cached development comparisons only. It changes no model, threshold, or runtime behavior.

T59 accepts one `capture` artifact and produces `labels.json` for T56.
It supports verified retained Fixture development captures, including observed no-focus states.
It preserves capture events while deduplicating identical pixels with matching labels and groups.
Unknown focus, conflicting duplicates, changed images, and training-eligible inputs fail.
Use T59, T56, and T57 as a dependency graph. Do not write another capture-to-scoring script.

T57 compares both crop models on known boxes, detector boxes, and detector boxes with optional HCF rings.
Inputs are `capture`, `scorecard`, `ringProposals`, `mapping`, `baseline`, `candidate`, `baselineSelection`, `candidateSelection`, and `tool`.
Use completed T56 scorecards and retained T37 references. Pin each input with the existing batch compiler.
The template verifies unchanged reference scores before publishing results. It records rejected boxes and removed duplicates.
It does not use true classes to filter detector boxes. It never applies ring offsets to detector boxes.

T58 needs `button`, `row`, and `tab` reports from T57. All reports use the same model and crop-helper identities.
Both templates use diagnostic budgets. Neither template trains, captures, or accepts a model.
See the [pilot contract](../../Research/Plans/DetectorFocusPipelinePilot.md) for data limits and decisions.

- State the observed failure or unresolved question.
- Name the matched control and one changed factor.
- Freeze data roles, groups, model identity, preprocessing, and thresholds.
- State the measurement and the decision that follows it.
- Keep preparation dependencies separate from executable experiments.
- Group cheap reports that read the same evidence.
- Do not split reports merely to increase the ready count.
- Report useful ready duration as well as job count.
- Record unavailable measurements instead of substitute scores.

T33 reviews retained per-class metrics. It does not rerun inference or prove case-level preservation.
T34 measures native proposal geometry. It does not prove full-screen focus selection.
Use the existing comparison templates to preserve earlier successes before accepting a correction.

### Native-control admission and matched exposure

T53 admits retained native controls through an explicit role overlay. Inputs are `configuration` and `decision`.
It verifies approved source hashes, observed focus, measured bodies, capture intervals, and group, layout, and pixel separation.
Identical Standard and HCF pixels are allowed only when labels and roles agree. The artwork admission gate remains unchanged.

T54 produces `crops.json` for matched T06 training. Inputs are `configuration`, `artwork`, and `native`.
Its configuration fixes `arm`, `perLabel`, and `nativePerLabel` under `native-control-membership-v1`.
The control repeats artwork examples. The mixed arm replaces part of that exposure with equal button, row, and tab quotas.
Both arms retain all unique artwork examples, equal class counts, and unchanged development rows.
It rejects changed crops, preprocessing differences, conflicting labels, and cross-role pixel duplicates.
Use T06 with deduplication disabled and repeat 1 after this producer fixes exposure.
These adapters qualify preparation. Their success does not establish model improvement.

## Scientific backlog

### Native detector inputs and inference

T55 takes `configuration` and prepares development labels from retained T46 or admitted native-control captures.
It preserves source bounds, original classes, groups, and exclusions. It rejects changed files and conflicting duplicates.
It does not admit training data or establish complete annotation coverage.

T56 takes `labels` and `model`. It accepts an optional PyTorch `baseline` scorecard for matched comparisons.
Parameters match T43: `engine`, `confidence`, `imageSize`, and `slice`.
PyTorch supports iOS and tvOS. The production engine supports tvOS only.
The adapter reuses T43 inference and T42 matching. Outputs include `scorecard.json`, `bundle.json`, and `cases.json`.
Use T42 with the output bundle for further cached analysis.
See [native detector comparisons](../../Research/Plans/NativeDetector20261017.md) for current scope and qualification limits.

[BACKLOG405](../../Research/Plans/ExperimentBacklog405.md) separates scientific questions from engineering prerequisites.
Tasks.md owns status. The catalog supplies definitions, controls, decisions, and blockers.
Validate both catalogs before preparing a batch:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/experiment_backlog.py Research/Experiments/backlog405.json --tasks Tasks.md --engineering Research/Experiments/engineering405.json
```

T40 joins retained selection and geometry reports through verified producer receipts.
It performs no inference. It identifies proposal failure categories and preserves every gain and lost success.
Its first registered description remains unapproved. See BACKLOG405 for remaining qualification checks and exact dispatch scope.

T41 rescores one box change per job with the fixed crop classifier (`FocusRingClassifier.makeCrop`, BP-46).
Set `source` to `known-box`, `raw-proposal`, or `mapped-proposal`. Set `intervention.kind` to `none`, `round`, `translate` (`dx`, `dy`), or `margin` (`dw`, `dh`).
A `none` job must reproduce the cached T37 scores within 0.0001. This check proves candidate correspondence.
T41 reports per-case scores, crop hashes, gains, lost previous successes, and abstentions. It never accepts a model.

## Reusable model decision batches

For registered scoring jobs, use `scripts/workflow_batch435.py` to avoid manually pairing conditions.
Write a `model-decision-request-v1` request with `id`, `question`, `controlledComparison`, `training`, `baseline`, and `candidate`.
The last 2 fields contain exact job IDs. The helper matches their inputs and settings, not list positions.
Every baseline condition needs exactly 1 matching candidate condition.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_batch435.py prepare REQUEST.json --output reports/work/NEW-BATCH
```

After scope approval, add `--register --approve-new`. Identical requests preserve existing jobs and completed attempts.
Inspect requirements and completed decisions without changing execution:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_batch435.py inspect reports/work/NEW-BATCH/compiled/compiled.json --text
```

See [WORKFLOW435](../../Research/Plans/WorkflowPreparation435.md) for tested behavior and current limits.

Use `scripts/model_decision_batch434.py` for matched T06, T37, and T63 workflows.
See [WORKFLOW434](../../Research/Plans/ModelDecisionBatches434.md) for decisions, supported contracts, and qualification.

Write a `model-decision-batch-v1` JSON description with these fields:

- `id`: the new batch ID.
- `question`: what the experiment tests.
- `controlledComparison`: what changes and what stays fixed.
- `training`: the candidate T06 job ID.
- `pairs`: entries with `id`, `baseline`, and `candidate` scoring job IDs.
- `executionBatch`: null for existing jobs, or a pinned batch description for new execution jobs.
- `version`: `model-decision-batch-v1`.

Compile into a new project folder before admission:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/model_decision_batch434.py PLAN.json --output reports/work/NEW-BATCH
```

After scope approval, add `--register --approve-new` to admit the generated jobs.
The compiler does not start a runner or repeat existing training.
The follow-up produces a bounded decision report. It does not authorize new training or model promotion.

## Bounded campaign approval

For `workflow_campaign439.py`, use `--approval-transaction` with `--register` and 1–10 explicit `--approve JOB_ID` arguments.
This option preserves individual authorization checks and publishes the selected approval records once.
It does not approve unnamed jobs, restore revoked IDs, or start execution.
The individual approval path remains the default. Capture admission uses its existing path.
See [WORKFLOW442](../../Research/Plans/WorkflowTransaction442.md) for timing and recovery evidence.

## Exhausted attempts

For several compatible decision graphs, use `workflow_review437.py REQUEST --text`.
The request uses version `workflow-review-v1` and a `batches` list of compiled-manifest pins.
Each pin contains `path` and `sha256`. The command accepts up to 12 manifests.
It counts shared jobs once and reports failed evidence without hiding other batches.
It does not dispatch, approve, or retry work. See [WORKFLOW437](../../Research/Plans/WorkflowCompletion437.md).

A job is exhausted when it uses all of its attempts. Do not edit its specification.
Run `.venv-yolo/bin/python -B scripts/research_extensions.py inventory` to see the failure reason and a time estimate.
The maintainer saves a restart with larger limits in the dashboard Inspect dialog.
If the failure is not `timeout` or `output_limit`, repair the cause first. See [EXTENSION408](../../Research/Plans/Extension408.md).

T43 runs pinned detector weights on pinned reviewed frames and compares the result with a pinned baseline scorecard.
Its production engine reproduces the stored tvOS scorecard exactly. Its PyTorch engine does not; compare PyTorch arms only with each other.
See [INFERENCE412](../../Research/Plans/DetectorInference412.md).

T61 audits geometry from a completed T57 report without inference.
Supply pinned `report` and `receipt` inputs and empty `parameters`.
It compares detector boxes with known control bodies and reports paired score changes.
It reports ambiguous matches instead of treating them as reliable labels.
These are development measurements. Do not use their offsets for training.
See [the correction plan](../../Research/Plans/DetectorFocusPolicy.md).

## Retained consumer comparisons

T66 compares verified T57 reports at detector confidence 0.5 and 0.25.
Inputs are `highReport`, `highReceipt`, `lowReport`, and `lowReceipt`.
Set `policy` to `unchanged` for replay or `high-first` for the fixed fallback.
The adapter preserves a unique high-confidence selection before considering the lower-confidence report.
It reports each model and profile separately, including lost no-focus abstentions.
Use only matching inspected development inputs. No inference or model acceptance occurs.
See [the proposal policy](../../Research/Plans/ProposalTierPolicy.md).

T62 uses `archive` and no parameters. It verifies the producer manifest and creates development memberships.
T63 uses `membership`, `model`, and `tool`. Its `backend` is `vision` or `pytorch`.
Use a verified export receipt for Vision. Use a checkpoint for PyTorch.
T63 verifies production crop hashes and reports crop errors separately from frame decisions.
Vision replay requires scores within 0.01 of the retained producer scores.
PyTorch comparisons do not establish Vision parity. Neither template admits data to training.

## Fixed detector input-size comparisons

A detector-campaign-v1 request accepts optional changedFactor with weights or image-size.
The default weights comparison requires identical inference settings.
For image-size, set training to null and use registered T57 producers with T56 scorecard dependencies.
Only imageSize may differ. Model hashes, backend, confidence, NMS, labels, frames, and crop inputs must match.
Supported sizes are 640, 960, and 1280. No automatic model promotion follows.
The compiler preserves pending scorecards as dependencies. It verifies fixed crop inputs before registration.
See [STREAM511](../../Research/Stream511IndependentExperiments.md).

## SDK513: control crops and temporal preparation

Use `scripts/sdk_training513.py` for verified SDK action-pair inputs.
The compiler emits intake, crop, and temporal jobs through the existing queue.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/sdk_training513.py REQUEST.json --output OUTPUT_DIRECTORY
```

The request uses version `sdk-preparation-v1`.
Provide `id`, pinned `pairs`, pinned TTR `source`, pinned production `tool`, `exclusions`, and `admission`.
The source descriptor names its Git commit and pins every portable Ruby source file.
Exclusions contain `groups`, `contentGroups`, `sourceFamilies`, and `images` lists.
Set `admission` to null for review-only preparation.
For training, provide a reviewer, reason, and exact pair hashes mapped to `train` or `development`.
Producer splits must match these roles. Test packets cannot become training inputs.
Set `withinFamilyDevelopment` explicitly when development shares app ancestry.
Group overlap and duplicate pixels across roles remain prohibited.

The outputs are `intake.json`, `crops.json`, and `temporal.json`.
Use `crop_training_description` to bind a completed eligible crop producer to T06.
The binding checks configuration, initialization, roles, eligibility, and producer identity.
It does not approve or start training.
Temporal rows preserve absence labels and work with existing temporal preprocessing.

Missing observed profiles block admitted crop preparation without discarding valid temporal observations.
Do not infer complete detector labels from registered controls.
Do not infer background motion or native selection from registration metadata.
See [SDK513 qualification](../../Research/SDK513Preparation.md).

## STREAM514: retained resolution fallback

Use `resolution_fallback514.compile_plan` for matched completed 1280-pixel and 960-pixel T57 reports.
A `resolution-fallback-plan-v1` document contains `id` and `pairs`.
Each pair names completed `baseline` and `fallback` job IDs.
The compiler verifies identical weights, settings other than resolution, captures, crop models, thresholds, and development roles.
It emits one comparison per pair and a combined decision.
The fixed rule preserves a unique baseline selection. It uses the smaller resolution only after baseline abstention.
No-focus regressions reject the correction. Cached execution does not measure live latency.
The detached runner executes admitted jobs. No model or consumer behavior changes automatically.

## STREAM515: detector resolution and preservation comparisons

Use T56 for inference at a supported resolution without a baseline input.
Use `detector_resolution515.make_spec` to compare the completed scorecard with retained references.
The plan version is `detector-resolution-plan-v1`.
Each pair supplies pinned `baseline`, `preservation`, and `labels` references plus the `candidate` producer ID.
The comparison requires identical weights for the resolution arm.
The preservation arm permits different weights and remains a separate report.
A terminal specification with no index combines all pair reports.
Reject losses against either baseline. Keep source settings and data roles pinned.
Two isolated campaigns qualify this connection. It does not change inference or matching implementations.
