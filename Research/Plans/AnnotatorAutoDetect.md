# ANNOTATOR-AUTO-DETECT-01

User requests automatic likely annotation rectangles. Current NUIAK worker owns
the local review editor and new proposal helper/tests for this assignment.

Add an optional, explicitly invoked **Auto-detect boxes…** action to the existing
Labelme launcher. A bounded local raster proposal pass detects contrast-separated
rectangular panels and closed outlines using existing Pillow/NumPy dependencies.
Long horizontal boundaries are paired and checked against both vertical sides
to propose textured panels; larger enclosing candidates suppress internal fragments.
No model, download,
OCR, focus inference, taxonomy change or device access. This is a geometry aid,
not a complete UI-element detector; artwork, borderless rows and tiny keys may be
missed. Existing click suggestion and manual/preset workflows remain available.

Preview numbered candidates on the current screenshot in one modal dialog with
checkable proposals and one common editable label defaulted to the last-used label.
Do not prompt separately for each rectangle. Cancel changes nothing. Add selected
rectangles only, with new local IDs, unfocused default and confirmed=false; clear
frame reviewed but preserve content approval/settled and all existing annotations.
Duplicate suppression against existing geometry and within proposals prevents
repeated invocation from multiplying boxes. Respect100total boxes and40proposals.
No automatic save; ordinary undo removes the addition as a group.

Verify actual Qt action/dialog, cancel/select/add/undo/save/reload, default flags,
duplicate filtering and empty results; test bounded raster behavior and inspect
proposals on a retained development screenshot without modifying its annotations.
Offline Swift build/test required. Local-only tooling; shared TTR coordination not
applicable. Do not interrupt an existing annotator window with unsaved work.

Observed integration blocker: wheel platform dylibs have BSD hidden flags; Qt QDir
Files returns zero entries while Files|Hidden returns all4. Both sandbox/host
offscreen launches fail before tests. Cache byte-identical platform plugins in a
content-addressed project-local runtime directory without copying filesystem flags.
Preserve wheel files, signatures and system settings; no dependency reinstall.
On reuse, clear only UF_HIDDEN on verified app-owned cached copies if necessary;
the same display flag was observed on cache copies on a subsequent launch.

Implementation complete for review.110focused Python tests and123offline Swift
tests pass; retained development proposal overlays inspected. See
[handoff](../../reports/work/ANNOTATOR-AUTO-DETECT-01/handoff.md).
