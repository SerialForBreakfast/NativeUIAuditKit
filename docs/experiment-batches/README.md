# Define a batch without a new script

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
    "owner": "research-host-NUIAK",
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
Batch approval holds the existing dispatch lock. If a batch is running, approval returns `resource_busy` without stopping it.
Registration remains intact. Repeat admission at an idle boundary with the same descriptions and explicit job IDs.
The inspector reports each branch independently. A missing input does not hide valid independent descriptions.
Registration validates the selected batch before writing jobs.
An interrupted registration can resume with the same immutable descriptions.
Changed inputs or execution sources require a successor ID, not an edited submitted job.

## Select useful work

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

## Scientific backlog

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

## After a job is exhausted

A job is exhausted when it uses all of its attempts. Do not edit its specification.
Run `.venv-yolo/bin/python -B scripts/research_extensions.py inventory` to see the failure reason and a time estimate.
The maintainer saves a restart with larger limits in the dashboard Inspect dialog.
If the failure is not `timeout` or `output_limit`, repair the cause first. See [EXTENSION408](../../Research/Plans/Extension408.md).

T43 runs pinned detector weights on pinned reviewed frames and compares the result with a pinned baseline scorecard.
Its production engine reproduces the stored tvOS scorecard exactly. Its PyTorch engine does not; compare PyTorch arms only with each other.
See [INFERENCE412](../../Research/Plans/DetectorInference412.md).
