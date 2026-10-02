# SETTINGS-CONTEXT-24

Assigned continuation October2,2026. Diagnose remaining Settings failures and test
one fixed region change, plus a reusable visual error gallery through the actual CLI.
Compare23's full-crop stability with stability measured only inside the tracked row
body, excluding one source pixel at its boundary. Keep thresholds, tracking,
highlight guard, membership and independent human scoring unchanged. Both metrics
use the same production256x256crop; a coordinate mask is not a second cropper.

Map before-body and tracked-after-body into each expanded/clamped native crop,
including the native rounded intermediate dimensions; use their mask intersection.
No after-annotation geometry is supplied to prediction. Preserve full-crop change
guard and illumination checks. Report whether changed pixels lie inside or outside
the body and how tracking displacement relates to text-edge differences.

Execute <=100retained controls and <=16generated adversarial cases, <=300seconds
per replay, <=512MiB output. Freeze policies before execution. Tests must include
neighbor changes, internal content changes, translations and focus-border changes;
if body masking hides focus evidence, report failure instead of promoting it.
Deliver overlays, per-control/action comparison, source pins, CLI tests and required
offline Swift checks. Existing model/corpus membership stays unchanged.
