# Define a batch without a new script

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
