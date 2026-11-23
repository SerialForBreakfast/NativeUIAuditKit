# Experiment atlas — November 5, 2026

Owner: Maximum-mini-NUIAK.

The inline atlas provides four views of one frozen snapshot:

- Dependencies show recorded execution dependencies and verified output reuse.
- Model lanes separate the model streams and shared data work.
- Outcomes separate reported scientific conclusions from execution completion.
- Timeline shows the first recorded execution, grouped by model stream.

The snapshot contains 278 catalog records, 4,757 jobs, and 3,973 attempt records.
It also retains 213 execution campaigns without a primary catalog owner.
Campaigns and jobs are not counted as independent experiments.
Every job has one primary owner in this projection. Reused controls remain associated evidence.
Only owned execution establishes a catalog node's execution date or completion.

The graph contains 7,407 execution dependency links and 16,302 verified output-reuse links.
Dotted reuse links do not change runner prerequisites.
Grouped campaign paths can loop. Execution-job mode preserves the exact job relationships.
Model tags are inferred for navigation from catalog descriptions and job names.
Shared acquisition work can serve more than one model.

Results remain provisional. A completed job is not a model improvement.
Historical RC561 accuracy claims remain invalidated.
Missing scientific outcomes remain unassessed.
No threshold, model, evaluation membership, data role, approval, service, or schedule changes.
The atlas cannot start or approve work.

## Inspection

Select a node to inspect its question, outcome, blockers, decision rule, follow-ups, evidence paths, and attempts.
Trace a node to include its prerequisites and descendants outside the current filter.
Open execution jobs to inspect the actual members of a catalog experiment.
Use the inspection menu when marks overlap or labels are hidden at overview scale.
The graph saves presentation state only. It does not monitor the runner.

## Files

- `experiment-atlas.html`: inline fragment for the approved visualization platform.
- `data.json`: frozen metadata snapshot.
- `manifest.json`: source counts, hashes, and data checks.
- `interaction-checks.json`: browser checks.
- `preview.html`: local QA wrapper, not a published website.

The existing Cytoscape 3.33.1 library is verified by its recorded SHA-256.
The fragment embeds compressed data and library bytes. It needs no network data requests.
No capture images, model files, credentials, or raw coordination receipts are embedded.

## Refresh

Use the resident project interpreter. Verify the mounted volume before writing.

```sh
.venv-yolo/bin/python -B reports/visualizations/experiment-atlas-20261105/export_snapshot.py
.venv-yolo/bin/python -B reports/visualizations/experiment-atlas-20261105/add_lineage.py
.venv-yolo/bin/python -B reports/visualizations/experiment-atlas-20261105/add_attempt_history.py
.venv-yolo/bin/python -B reports/visualizations/experiment-atlas-20261105/build_atlas.py
```

These commands read the existing queue. They do not dispatch work or change existing records.
Audited recent summaries are preserved in the exporter and remain provisional.
Review those summaries when refreshing the snapshot.

## Validation

The data checks verify node identities, edge endpoints, unique primary ownership, and non-execution of reused controls.
They also verify known rejected candidates, native non-acceptance, compression, and library integrity.
Browser checks cover four views, filters, inspection, path tracing, full history, and explicit HCF rejection.
They also cover dark mode, 320 px and 360 px layouts, and runtime errors.
Rendered screenshots are QA evidence only.

## Delivery

The completed atlas passes 21 browser interaction checks.
No browser runtime errors occur during those checks.
Elapsed implementation time is approximately 27.7 min. The initial estimate is 30–60 min.
