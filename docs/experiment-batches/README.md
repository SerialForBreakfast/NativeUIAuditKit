# Define a batch without a new script

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
T89 has software caller checks. Real training qualification remains pending. Do not claim a ready training experiment without qualified membership.

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
