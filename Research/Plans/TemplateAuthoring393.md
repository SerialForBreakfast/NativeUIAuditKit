# Author a bounded crop experiment

Use this binding for software qualification on retained development crops.
Do not use it for final audit, capture, training, or model acceptance.

## Describe the experiment

Use `experiment-description-v1` with these fields:

| Field | Requirement |
| --- | --- |
| `id` | Stable identifier with at most 48 characters |
| `owner` | Existing Machine-Project owner format |
| `question` | What this test checks |
| `decision` | What the result changes; include failure handling |
| `manifest` | Repository-relative path and SHA-256 |
| `model` | Repository-relative checkpoint path and SHA-256 |
| `batchSize` | Integer from 1 to 16 |
| `version` | `experiment-description-v1` |

The membership manifest uses `prepared-crop-membership-v1` and `production-crops-rgb256-v1`.
Each row supplies `id`, `group`, `role`, `profile`, `label`, and an image path with its SHA-256.
Use 1–16 existing 256 × 256 crops. Use development roles only.
Use labels 0 or 1 and profiles `standard` or `hcf`.
The adapter preserves crop size and uses the existing trainer's RGB conversion.

## Preview and register

Run commands from the active checkout with its existing Python environment.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_templates.py catalog
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_templates.py preview description.json
PYTHONPATH=scripts .venv-yolo/bin/python scripts/experiment_templates.py register description.json --queue reports/work/isolated-queue
```

Preview checks requirements without writing jobs.
Registration writes preparation, scoring, and report jobs with explicit dependencies.
Use the existing review and approval flow before execution.
Let the detached runner execute approved live jobs.

If inputs or code change after submission, create an explicit successor description.
Do not edit the submitted specification or remove failure evidence.
If registration stops, submit the unchanged description again.
Registration preserves completed matching registrations and rejects conflicts.

## Extend the binding

Add a new adapter only when the existing operation cannot express the required test.
Add a version when input meaning, defaults, preprocessing, or acceptance changes.
Test a successful case and predictable failure cases through an isolated queue.
Preserve older bindings while approved jobs depend on them.
Do not advertise contract-only entries as ready experiments.

See [measured results](../Workflow394Results.md) and [the complete implementation plan](ExperimentTemplates393.md).
