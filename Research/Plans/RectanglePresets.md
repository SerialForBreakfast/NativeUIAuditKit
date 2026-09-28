# Local rectangle presets

User-assigned annotation efficiency increment, 2026-09-28. Save selected boxes
(or all boxes when none are selected) under a named project-local preset. Load
from a picker across batches. Store image dimensions, taxonomy hash, labels and
two-corner pixel geometry only. Never carry focus state, approvals or native IDs.
Reject incompatible dimensions, invalid labels/geometry and duplicate names.
Loading adds proposals with fresh local IDs; never replaces existing annotations.
Human verifies layout compatibility and adjusts focused scaling on each image.
Provide Save preset and Load preset controls in the existing rectangle editor.
Tests cover persistence, rejection and actual Qt application. No model/device work.

## Focus dialog simplification

One visible Focused checkbox replaces mutually exclusive focus controls. On explicit
OK, unchecked serializes focused=false/unfocused=true; checked does the inverse.
Opening or canceling does not rewrite unknown proposals. Keep confirmed, flagged
and rejected separate. Enter/Return accepts a valid taxonomy label from every
dialog field; Escape cancels. Description is optional. Existing annotation schema
and independent Finish review confirmation remain unchanged.

## Focus list visibility

Show explicit focused/unfocused/unknown/conflicting/rejected state beside each
control and pin all active focused controls first. This is presentation only:
preserve rectangle geometry, group IDs, flags, selection and canvas stacking.
Disable list drag-reordering while automatic pinning is active. Show focused count
in the dock title, warning when multiple controls claim focus. Never auto-clear a
second focus; unusual/subnav states remain recordable but the existing single-focus
qualification check still blocks them pending interpretation. No model changes.

## Binary defaults in Finish review

User correction: Finish review must match the single Focused checkbox. Its read-only
preview proposes unfocused=true when both old flags are false; final explicit
human confirmation commits that default with the existing backups/stale checks.
Do not auto-clear conflicting true/true states, flagged controls, or rewrite source
documents during preview. Direct legacy revision parsing retains unknown semantics.
UI must disclose unchecked=unfocused and show uncommitted legacy defaults clearly.

Visual refinement: use only filled/hollow circles for normal focus states in
control rows; full state text remains in tooltips. Preserve warning/exclusion
symbols and the dock's focused-count warning. No label or annotation change.
