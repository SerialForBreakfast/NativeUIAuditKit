# CoreML startup RCA — 2026-09-22

## Finding

The current failure is a filesystem read before conversion, not a demonstrated
model/converter defect. `runtime-probe-warm.json` records exit1 after57.119s;
its log ends in Python importlib `get_data`, reached through coremltools/libsvm,
with `TimeoutError: [Errno 60] Operation timed out`. This is not deadline exit124.

`dataless-evidence.txt` records `hidden,compressed,dataless` on four installed files
under `.venv-yolo/lib/python3.13/site-packages/`:

- `coremltools/converters/libsvm/__init__.py`
- `coremltools/converters/libsvm/_libsvm_converter.py`
- `coremltools/converters/libsvm/_libsvm_util.py`
- `scipy/stats/__init__.py`

A separate `wc` read of the SciPy initializer also timed out. Apple documents that
dataless placeholders require content materialization and reads can hang or fail
with ETIMEDOUT. [Apple TN3150](https://developer.apple.com/documentation/technotes/tn3150-getting-ready-for-data-less-files).
Follow-up identifies iCloud Drive as the provider. Its supported download API
accepts the request but the probe file stays dataless and fails a host read.
An account upload-quota error also exists, but the download failure's underlying
cause remains unproven. [Repair attempt and next authority](residency-repair.md).
Do not assume sandbox denial or a broken native extension.

## Isolation

The previously implicated `scipy.interpolate._rgi` now imports in0.554s
(`isolated-scipy.json`); two sampled source/native files read in less than0.3ms
each (`read-timing.json`). Warming one module does not qualify the whole tree.
The earlier612s export remains failed evidence; this probe does not establish
every cause of its elapsed time. No checkpoint was loaded by these probes.

Installed metadata: coremltools9.0, Torch2.13.0, SciPy1.18.1, scikit-learn1.9.0.
coremltools warns Torch2.13 is untested (tested2.7), and its sklearn support range
excludes1.9. These are subsequent compatibility risks, not causes of errno60.

## Safe repair and resume

1. Maintainer restores through the identified iCloud provider and makes `.venv-yolo`
   locally resident/kept downloaded. Do not change global security/sync settings
   or repeat folder-access prompts as a substitute.
2. Alternatively, separately authorize a pinned export environment in non-evictable
   storage with explicit cache/output authority. Preserve the current environment,
   checkpoints and reports; no implicit reinstall, relocation or deletion.
3. Recheck residency, then one bounded full Torch/coremltools import. Only after
   that passes resume isolated export and the prepared compile/parity path.
   Import success is not conversion compatibility or model qualification.

No dependency changes, downloads, export retry, training, promotion, service reset
or optional-import bypass occurred. Both probes finished; no background work.
Software safeguards retain prior test evidence; actual export remains blocked,
model gates not assessed. No SMB update for this local-only issue.
