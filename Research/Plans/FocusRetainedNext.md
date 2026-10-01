# FOCUS-RETAINED-NEXT-15 — retained coverage, input audit and next experiment

Owner: current NUIAK worker. Assigned 2026-09-30: user approved items 1–3.

Deliver an inventory of retained real recording frames against existing human
reviews, a small genuinely additive diagnostic annotation batch when warranted,
an audit of FDR020's actual 928-member input/weight/transform path, and one
changed-data experiment proposal with explicit readiness checks. Reconcile
superseded local queue entries without accepting another worker's work.

Source-session reservations survive selection: neighbors of the supplement's
training session are prospective training additions only after human confirmation
and explicit admission; neighbors of existing development frames stay development.
Neither distinct hashes nor additional frames establish source independence.
Do not inspect protected challenge pixels. Raster rectangle proposals may assist
review but provide neither semantic labels nor focus truth. Preserve originals.

Use the existing recorder importer and rectangle proposer. Audit the pinned
full-fit implementation, not historical OHEM/augmentation recipes. No model
loading, inference, training, capture, export, promotion or role changes. A
proposal whose new labels are unavailable must fail readiness rather than reuse
the old training approval or manufacture labels. Existing production crop QA is
reused; new crop QA follows human confirmation.

Evidence lives under reports/work/FOCUS-RETAINED-NEXT-15. Test new audit/selection
mechanisms and existing importer integration, then run offline Swift checks for
code changes. Completion is reviewable findings and exact next action, not a
new model or a fabricated launch-ready experiment. Coordination is local-only
unless a finding changes TTR's next action.

## Findings and decision

702retained files/739observations checked; four targeted Paramount frames prepared,
not an independent new corpus. FDR020's928training controls and333validation crops
reverified. Six human focused artwork controls already carry7.5%of loss, while
human buttons have no positive support. Next intervention is confirmed additional
contrast data, not more repeats of those six controls. Source recording also
contains Photos/Home/Settings relatives of development; preserve that limitation.
Exact new training control IDs, crop QA and admission remain human/data gates.
See the [integrated handoff](../../reports/work/FOCUS-RETAINED-NEXT-15/handoff.md).
