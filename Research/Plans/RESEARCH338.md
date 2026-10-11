# RESEARCH338 — research queue and replay qualification

Design: [ADR-0026](../ADR-0026-Queued-Research-Experiments.md).

## Scope

1. Add `scripts/research_queue.py` with `submit`, `run`, `status`, and `summarize` commands.
2. Support `research-spec-v1`, the `diagnostic` authority class, and the `python-callable` adapter.
3. Add focused tests that use small synthetic modules. The tests run no FOCUS code.
4. Replay 3 finished FOCUS audits through the queue. Compare every output with the recorded file.

No training, capture, device use, data-role change, or model change belongs to this work.
Recorded FOCUS folders stay read-only. Replay outputs go to `reports/work/research-queue/`.

## Queue layout

```
reports/work/research-queue/
  jobs/<job-id>/spec.json
  jobs/<job-id>/attempts/<n>/attempt.json
  jobs/<job-id>/attempts/<n>/out/          # job outputs
  jobs/<job-id>/attempts/<n>/stdout.log
  jobs/<job-id>/attempts/<n>/result.json
  summary.json
```

## Replay specs

| Job ID | Steps | Output attributes | Staged input | Compared files |
| --- | --- | --- | --- | --- |
| `replay-focus329-audit` | `boundary329.run` | `boundary329.OUT` | none | `registration.json`, `audit.json` |
| `replay-focus330-audit` | `controls330.audit`, `report_controls330.main` | both modules' `OUT` | recorded `detections.json` | `audit.json`, `report.json` |
| `replay-focus331-audit` | `regions331.audit`, `report_regions331.main` | both modules' `OUT` | none | `registration.json`, `audit.json`, `report.json` |

Each replay keeps the FOCUS329 audit as its recorded prior. It does not chain replay outputs.

Allowed differences, each declared in the spec:

- `seconds` in each audit: wall time.
- A file reference whose target is a replayed audit: its hash covers that audit's `seconds` field.
- Paths inside the attempt folder: compared after mapping them to the recorded folder.

## Acceptance

- Focused tests cover spec validation, refused authority classes, input hash changes, output collisions,
  timeouts, interrupted attempts, completed-job skipping, module-closure hashing, replay comparison, and the summary.
- Every replay job completes. Every compared file matches, except the declared fields.
- If a replay differs, the queue reports the exact field paths. Do not widen the allowed fields after the result.
- The offline Swift build and tests pass.
