# TRAIN-MPS-DIAG-13 — bounded local timing diagnostic

User continuation after the OHEM/timing repair authorizes one bounded local MPS
diagnostic, not full training, CUDA, promotion or an automatic experiment sweep.
Owner: Codex. Reuse the existing iOS trainer and repaired OHEM, with `--timing`.

Freeze the earlier512training members and64deterministically selected original
validation members. Verify every image/label hash and pixel/YOLO integrity, distinct
paths, dataset binding and train/validation pixel independence. Do not touch the
test split. Copy into a fresh diagnostic-only local dataset so trainer label caches
cannot modify source data. Pin local yolo11m.pt initialization, taxonomy, scripts,
installed runtime source and versions. Never download missing weights.

Run at batch8,imgsz640,2epochs,MPS,workers0,seed42 with existing trainer settings
otherwise unchanged. This is an early-training cost diagnostic (warmup remains3),
not a steady-state batch8/16 comparison or a model-quality experiment. Keep generated
weights isolated and explicitly ineligible for promotion; no run-ID allocation for
a production candidate. Log this diagnostic before model execution.

Resource limits:1800s wall-clock child deadline,8GiB available RAM at launch,
3GiB available runtime reserve,10GiB free disk throughout,2GiB diagnostic artifact
budget. These are conservative experiment safety limits, not model gates. Check
before model import. A supervisor samples resources and terminates only its owned
child on limit breach; no process/service cleanup, retries or closing user apps.
No environment changes to GPU allocation thresholds. Logs and caches stay in-project.

Deliver the exact frozen plan and source pins, runnable supervisor with isolated
positive/negative tests, preflight/resource receipt, optional actual timing results,
and one next decision. Distinguish model success, resource-blocked, failed and timed
out. Do not present a blocked preflight as successful training. Host-wall intervals
overlap and do not isolate GPU execution; no speedup claim from these measurements.
Normal hard termination may lack the trainer terminal record: supervisor receipt
is authoritative for process completion, and partial logs remain intact.

No TTR coordination needed: this local iOS diagnostic changes no producer action.
