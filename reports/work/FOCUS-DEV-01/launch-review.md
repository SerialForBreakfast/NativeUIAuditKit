# Resolved development experiment — execution not authorized

Protocol: `dataset/focus_dataset_manifest.json`.
Content hash: `fa1c7cffa8e42aac511353c9ccd99cf091dbf25a05cb3f5deba52e1ac458fca2`.
Decision template: `approval-draft.json`, explicitly approved=false. Do not edit it
to true without an actual maintainer decision. No experiment ID has been allocated.

Training: 40 native pairs + 86 distinct Fixture pairs = 252 examples. Validation:
nine native pairs = 18 examples. Fixture seeds7/19 remain one training group. No
independent Fixture validation exists; final production gates remain unassessed.
Four exact duplicate pairs, 48 maze pairs and the earlier overlapping two-pair smoke
do not enter training. Six kitchen-sink recipes remain absent. Original source
manifests, partial receipts and prior experimental memberships remain unchanged.

Configuration: warm FDR-007 weights / fresh AdamW optimizer, vendored MobileNetV4,
30 epochs, batch64, lr0.0003, seed42, no random augmentation, production16%/256
preprocessing; 1800-second cooperative budget. Imports/in-flight kernels are not
hard-preempted. Minimum native-validation BCE chooses the checkpoint; ties keep
the earliest epoch. No test data enters the trainer and no automatic retry/export.

Sampling uses the existing equal source/scene/style/control-stratum policy, **not
equal source totals**. The exact frozen weights imply 11.11% expected native and
88.89% Fixture sampling mass because Fixture supplies more strata. This is a
reviewable design choice, not proven optimal. Native retention must be reported.
If equal source totals are preferred, change and re-freeze the protocol before
approval; do not silently alter these weights at launch.

## Read-only preflight

From the project root, using the approved isolated Python environment:

```sh
PYTHONDONTWRITEBYTECODE=1 '/Users/josephmccraw/Library/Application Support/NativeUIAuditKit/Environments/focus-export-01/bin/python' scripts/train_focus_ring_detector.py --experiment-protocol reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json --experiment-arm warm-stretch --name mixed-appearance-development-proposed --dry-run
```

Expected exit2 until a valid approval is supplied. Once explicitly authorized,
save a separate decision record binding the exact protocol, arm and final run name,
allocate/log the next run ID, and pass that record with `--experiment-approval`.
Execution additionally requires `--execute --experiment-id <logged-id>`. Do not
run execution during this software tranche. Preflight does not import Torch or
deserialize weights. Training will validate the checkpoint state on load.

Next authorized training tranche should include the single run plus comparison
against retained FDR-007/shipped references on identical membership and native
challenge evidence. Fixture fit is diagnostic, not generalization. Home/Photos
must not be used for checkpoint selection, and existing physical qualification,
six quality gates and production fallback remain unchanged.
