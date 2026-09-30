# Diagnostic geometry adapter

Research/contract: [FocusGeometryAdapter](../../../Research/Plans/FocusGeometryAdapter.md).

Run existing `scripts/ttr_focus_manifest.py` intake first, without changing its
wrapper geometry. Then opt in to the diagnostic role using the exact input hash:

```sh
.venv-review/bin/python scripts/focus_geometry_diagnostic.py \
  --manifest PATH/TO/focus_dataset_manifest.json \
  --manifest-sha256 EXACT_SHA256 \
  --geometry-role artwork_layout_view_bounds \
  --output reports/work/FOCUS-GEOMETRY-ADAPTER-01/NEW_OUTPUT
```

Use `--geometry-role measured_control_wrapper` for the unchanged wrapper reference.
Output `geometry-diagnostic.json` accounts for every focused/unfocused frame as
rendered, blocked or failed. Unavailable artwork produces no substituted crop.
The report includes the original box, optional telemetry, selected box, source
hash, frame/element/state identity and runtime. Crop files are named by that bound
identity. No `focus_dataset_manifest.json` is emitted; ordinary dataset validation
rejects this version. Exit2 indicates failure; blocked-only diagnostics can exit0
but do not mean geometry is available. Inspect counts before claiming a usable set.

`validate_report` revalidates original intake and both bracket endpoints, hashes,
membership and exact production crop parity. This is nominal layout evidence,
not measured enlarged artwork-body bounds or admission to training.
